"""Check an exported classifier through CPU prediction, local API, and CLI.

Demonstration messages establish runtime compatibility only. They are not
accuracy ground truth, and this script neither trains nor accesses the GPU.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def extract_cli_json(stdout):
    decoder = json.JSONDecoder()
    for position, character in enumerate(stdout):
        if character == "{":
            try:
                value, _ = decoder.raw_decode(stdout[position:])
            except ValueError:
                continue
            if isinstance(value, dict) and isinstance(value.get("results"), list):
                return value
    raise ValueError("CPU CLI did not return a JSON prediction result")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", default="artifacts/runs/domain_v2_20261023_1050")
    parser.add_argument("--wait-seconds", type=int, default=0)
    args = parser.parse_args(argv)
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = ROOT / run_dir
    model_dir = run_dir / "model"
    output = run_dir / "runtime_validation"
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "purpose": "Actual trained-model CPU/API/CLI runtime validation; examples are not accuracy ground truth",
        "device_target": "CPU", "gpu_inference_performed": False,
        "training_performed": False, "started_at": datetime.now(timezone.utc).isoformat(),
        "model_dir": str(model_dir), "checks": {}, "passed": False,
    }
    started = time.perf_counter()
    try:
        deadline = time.monotonic() + max(0, args.wait_seconds)
        next_wait_notice = 0
        while not (model_dir / "manifest.json").is_file():
            if time.monotonic() >= deadline:
                raise FileNotFoundError("Trained classifier bundle is not ready")
            if time.monotonic() >= next_wait_notice:
                print("Waiting for exported trained-classifier manifest", flush=True)
                next_wait_notice = time.monotonic() + 30
            time.sleep(min(3, max(.01, deadline - time.monotonic())))
        from wisemessage.predictor import MessagePredictor, read_classifier_manifest, sha256_file
        from wisemessage.service import create_app
        from fastapi.testclient import TestClient
        import numpy as np

        manifest, files = read_classifier_manifest(model_dir)
        model_ready_tick = time.perf_counter()
        report["waiting_seconds"] = model_ready_tick - started
        report["model_ready_at"] = datetime.now(timezone.utc).isoformat()
        report["model_id"] = manifest["model_id"]
        identity = sha256_file(files["checkpoint"])
        report["checkpoint_sha256"] = identity
        report["checks"]["strict_trained_classifier_manifest_and_asset_hashes"] = True
        messages = [
            "明天上午十點覆診，請帶同身份證。",
            "明天上午十点复诊，请带同身份证。",
            "您的帳戶異常，請立即提供驗證碼以免凍結。",
            "您的账户异常，请立即提供验证码以免冻结。",
        ]
        input_path = output / "input_messages.json"
        write_json(input_path, messages)
        predictor = MessagePredictor(model_dir, device_target="CPU", batch_size=4)
        direct = predictor.predict(messages)
        assert len(direct) == 4
        direct_scores = np.asarray([list(value["scores"].values()) for value in direct])
        assert direct_scores.shape == (4, 3) and np.isfinite(direct_scores).all()
        assert np.allclose(direct_scores.sum(1), 1, atol=1e-5)
        assert all(value["model_id"] == manifest["model_id"] for value in direct)
        assert np.allclose([value["unwanted_score"] for value in direct], direct_scores[:, 1:].sum(1), atol=1e-6)
        for value in direct:
            if "unwanted" in predictor.thresholds:
                flagged = value["unwanted_score"] >= predictor.thresholds["unwanted"]
            else:
                flagged = any(value["scores"][label] >= predictor.thresholds[label] for label in ("spam", "scam"))
            assert (value["decision"] == "flag_for_review") == flagged
        report["aggregate_unwanted_threshold"] = predictor.thresholds.get("unwanted")
        report["checks"]["actual_cpu_predictor_simplified_and_traditional"] = True
        report["example_predictions"] = [{"message": text, **prediction}
                                         for text, prediction in zip(messages, direct)]
        # No injected predictor: the actual lifespan loads the trained bundle.
        with TestClient(create_app(model_dir=model_dir, device_target="CPU")) as client:
            health = client.get("/health")
            assert health.status_code == 200 and health.json()["model_id"] == manifest["model_id"]
            assert health.json()["fetches_urls"] is False
            response = client.post("/predict", json={"messages": messages})
            assert response.status_code == 200
            api_values = response.json()["results"]
            api_scores = np.asarray([list(value["scores"].values()) for value in api_values])
            maximum_difference = float(np.max(np.abs(api_scores - direct_scores)))
            assert maximum_difference < 1e-5
            assert [value["decision"] for value in api_values] == [value["decision"] for value in direct]
            assert np.allclose([value["unwanted_score"] for value in api_values],
                               [value["unwanted_score"] for value in direct], atol=1e-6)
            assert all(value["thresholds"] == predictor.thresholds for value in api_values)
            scan = client.post("/scan-text", json={"text": messages[0]})
            assert scan.status_code == 200 and scan.json()["model_id"] == manifest["model_id"]
            invalid_codes = []
            for payload in ({"messages": []}, {"messages": [""]}, {"messages": [123]}, {"messages": ["x" * 20_001]}):
                invalid_codes.append(client.post("/predict", json=payload).status_code)
            assert invalid_codes == [422] * 4
            report["api"] = {"health_status": health.status_code, "predict_status": response.status_code,
                             "scan_text_status": scan.status_code, "invalid_request_statuses": invalid_codes,
                             "maximum_probability_difference_vs_direct": maximum_difference,
                             "returned_thresholds_match_manifest": True,
                             "returned_thresholds": api_values[0]["thresholds"],
                             "actual_model_loaded_at_startup": True}
        report["checks"]["actual_model_api_health_predict_scan_text_invalid_requests"] = True
        command = [sys.executable, "-B", "-m", "wisemessage", "predict", "--model-dir", str(model_dir),
                   "--device-target", "CPU", "--batch-size", "4", "--input-json", str(input_path)]
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(command, cwd=ROOT, env=environment, stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, encoding="utf-8", timeout=120)
        (output / "cpu_cli_stdout.log").write_text(result.stdout, encoding="utf-8")
        (output / "cpu_cli_stderr.log").write_text(result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(f"Actual CPU CLI failed with exit code {result.returncode}")
        cli_values = extract_cli_json(result.stdout)["results"]
        assert len(cli_values) == 4
        cli_scores = np.asarray([list(value["scores"].values()) for value in cli_values])
        cli_difference = float(np.max(np.abs(cli_scores - direct_scores)))
        assert cli_difference < 1e-5
        assert [value["decision"] for value in cli_values] == [value["decision"] for value in direct]
        if "unwanted" in predictor.thresholds:
            assert all(value["thresholds"]["unwanted"] == predictor.thresholds["unwanted"] for value in cli_values)
        report["cli"] = {"exit_code": result.returncode, "messages": len(cli_values),
                         "maximum_probability_difference_vs_direct": cli_difference}
        report["checks"]["actual_cpu_cli_utf8_json_input"] = True
        assert sha256_file(files["checkpoint"]) == identity
        report["checks"]["checkpoint_unchanged"] = True
        report["passed"] = True
        report["runtime_validation_seconds"] = time.perf_counter() - model_ready_tick
    except BaseException as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["traceback"] = traceback.format_exc()
    finally:
        report["elapsed_seconds"] = time.perf_counter() - started
        report["completed_at"] = datetime.now(timezone.utc).isoformat()
        write_json(output / "report.json", report)
        print(json.dumps({"passed": report["passed"], "report": str(output / "report.json"),
                          "error": report.get("error"), "elapsed_seconds": report["elapsed_seconds"]}), flush=True)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
