"""Contract checks for artifact integrity and privacy-conscious API responses."""

import json
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from wisemessage.predictor import (
    ModelArtifactError, classify_probabilities, read_classifier_manifest, sha256_file,
)
from wisemessage.service import create_app


class FakePredictor:
    model_id = "contract-test-only"

    def predict(self, messages):
        return classify_probabilities(np.tile([0.05, 0.10, 0.85], (len(messages), 1)),
                                      model_id=self.model_id, thresholds={"spam": 0.5, "scam": 0.5})


def make_manifest(tmp_path):
    for name in ("model.ckpt", "config.json", "vocab.txt"):
        (tmp_path / name).write_text("test-only-placeholder", encoding="utf-8")
    manifest = {
        "format_version": 1, "framework": "mindspore", "task": "sms_spam_scam_detection",
        "checkpoint_type": "message_classifier", "model_id": "contract-test-only",
        "id2label": {"0": "normal", "1": "spam", "2": "scam"},
        "checkpoint": "model.ckpt", "config": "config.json", "vocab": "vocab.txt",
        "checkpoint_sha256": sha256_file(tmp_path / "model.ckpt"),
        "config_sha256": sha256_file(tmp_path / "config.json"),
        "tokenizer_sha256": sha256_file(tmp_path / "vocab.txt"),
        "config_fingerprint": "test-fingerprint", "max_length": 128,
        "thresholds": {"spam": 0.5, "scam": 0.5}, "do_lower_case": True,
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


def test_manifest_hash_and_task_integrity(tmp_path):
    make_manifest(tmp_path)
    manifest, files = read_classifier_manifest(tmp_path)
    assert manifest["model_id"] == "contract-test-only"
    assert files["checkpoint"].parent == tmp_path
    (tmp_path / "config.json").write_text("altered", encoding="utf-8")
    with pytest.raises(ModelArtifactError, match="config SHA256"):
        read_classifier_manifest(tmp_path)


def test_manifest_rejects_encoder_only_checkpoint(tmp_path):
    manifest = make_manifest(tmp_path)
    manifest["checkpoint_type"] = "pretrained_encoder"
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ModelArtifactError, match="fine-tuned"):
        read_classifier_manifest(tmp_path)


def test_manifest_rejects_path_escape(tmp_path):
    root = tmp_path / "bundle"
    root.mkdir()
    manifest = make_manifest(root)
    outside = tmp_path / "outside.ckpt"
    outside.write_text("outside", encoding="utf-8")
    manifest["checkpoint"] = "../outside.ckpt"
    manifest["checkpoint_sha256"] = sha256_file(outside)
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ModelArtifactError, match="inside"):
        read_classifier_manifest(root)


def test_decisions_do_not_call_below_threshold_safe():
    values = np.array([[0.9, 0.05, 0.05], [0.1, 0.8, 0.1], [0.3, 0.3, 0.4]])
    results = classify_probabilities(values, model_id="test", thresholds={"spam": 0.5, "scam": 0.5})
    assert [result["decision"] for result in results] == ["below_threshold", "flag_for_review", "uncertain"]
    assert [result["predicted_label"] for result in results] == ["normal", "spam", "scam"]


def test_invalid_model_probabilities_are_rejected():
    with pytest.raises(RuntimeError, match="normalized"):
        classify_probabilities([[0.5, 0.5, 0.5]], model_id="test", thresholds={"spam": 0.5, "scam": 0.5})


def test_aggregate_unwanted_threshold_preserves_unknown_subtype_evidence():
    probabilities = [[0.4, 0.3, 0.3]]
    old = classify_probabilities(probabilities, model_id="test", thresholds={"spam": 0.5, "scam": 0.5})[0]
    aggregated = classify_probabilities(probabilities, model_id="test",
                                       thresholds={"spam": 1., "scam": 1., "unwanted": 0.5})[0]
    assert old["decision"] == "below_threshold"
    assert aggregated["decision"] == "flag_for_review"
    assert aggregated["unwanted_score"] == pytest.approx(0.6)
    # Reporting aggregate risk does not invent a fine-grained scam label.
    assert aggregated["predicted_label"] == "normal"
    assert aggregated["scores"] == old["scores"]


def test_manifest_rejects_nonfinite_aggregate_threshold(tmp_path):
    manifest = make_manifest(tmp_path)
    manifest["thresholds"]["unwanted"] = float("nan")
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ModelArtifactError, match="finite"):
        read_classifier_manifest(tmp_path)


def test_aggregate_score_handles_float32_rounding_at_one():
    probabilities = np.asarray([[1e-9, .6, .4]], dtype=np.float32)
    prediction = classify_probabilities(probabilities, model_id="test",
                                         thresholds={"spam": 1., "scam": 1., "unwanted": .5})[0]
    assert 0 <= prediction["unwanted_score"] <= 1


def test_api_preserves_aggregate_unwanted_score_and_threshold():
    class AggregatePredictor:
        model_id = "aggregate-contract-test"

        def predict(self, messages):
            return classify_probabilities(np.tile([0.4, 0.3, 0.3], (len(messages), 1)),
                                          model_id=self.model_id,
                                          thresholds={"spam": 1., "scam": 1., "unwanted": 0.5})

    with TestClient(create_app(predictor=AggregatePredictor())) as client:
        response = client.post("/predict", json={"messages": ["測試"]})
        assert response.status_code == 200
        prediction = response.json()["results"][0]
        assert prediction["decision"] == "flag_for_review"
        assert prediction["unwanted_score"] == pytest.approx(.6)
        assert prediction["thresholds"]["unwanted"] == .5


def test_api_classifies_traditional_simplified_without_echoing_message():
    messages = ["您的账户需要立即验证。", "您的帳戶需要立即驗證。"]
    with TestClient(create_app(predictor=FakePredictor())) as client:
        assert client.get("/health").json()["fetches_urls"] is False
        response = client.post("/predict", json={"messages": messages})
        assert response.status_code == 200
        assert len(response.json()["results"]) == 2
        assert all(result["decision"] == "flag_for_review" for result in response.json()["results"])
        assert not any(message in response.text for message in messages)
        assert client.post("/scan-text", json={"text": messages[0]}).status_code == 200


@pytest.mark.parametrize("payload", [{"messages": []}, {"messages": [""]},
                                     {"messages": ["   "]}, {"messages": [123]},
                                     {"messages": ["x"] * 65}])
def test_api_rejects_invalid_requests(payload):
    with TestClient(create_app(predictor=FakePredictor())) as client:
        assert client.post("/predict", json=payload).status_code == 422


def test_api_readiness_requires_classifier(tmp_path):
    with TestClient(create_app(model_dir=tmp_path / "missing")) as client:
        assert client.get("/health").status_code == 503
        assert client.post("/predict", json={"messages": ["測試"]}).status_code == 503


def test_gpu_cli_bootstraps_environment_before_model_import(monkeypatch):
    from wisemessage.__main__ import main
    from wisemessage import runtime
    import os

    class Reexecuted(Exception):
        pass

    recorded = {}
    monkeypatch.delenv("WISEMESSAGE_GPU_BOOTSTRAPPED", raising=False)
    monkeypatch.setattr(runtime, "configure_environment", lambda: recorded.update(configured=True))

    def fake_exec(executable, arguments, environment):
        recorded.update(arguments=arguments, environment=environment)
        raise Reexecuted

    monkeypatch.setattr(os, "execvpe", fake_exec)
    with pytest.raises(Reexecuted):
        main(["predict", "--device-target", "GPU", "--model-dir", "unused", "--message", "測試"])
    assert recorded["configured"] is True
    assert recorded["environment"]["WISEMESSAGE_GPU_BOOTSTRAPPED"] == "1"
    assert recorded["arguments"][1:3] == ["-m", "wisemessage"]
