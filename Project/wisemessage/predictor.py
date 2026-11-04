"""Local inference for a verified, fine-tuned WiseMessage classifier.

Messages are treated as text only: inference never fetches URLs, accesses an
inbox, forwards messages, or logs their contents.
"""

import hashlib
import json
import math
from pathlib import Path
from threading import Lock


LABELS = {0: "normal", 1: "spam", 2: "scam"}
MAX_MESSAGE_LENGTH = 20_000


class ModelArtifactError(ValueError):
    """A classifier bundle is incomplete or has an inconsistent identity."""


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _asset(root, value):
    if not isinstance(value, str) or not value:
        raise ModelArtifactError("Manifest asset paths must be nonempty strings")
    candidate = (root / value).resolve()
    if not candidate.is_relative_to(root) or not candidate.is_file():
        raise ModelArtifactError("Each manifest asset must be a file inside the model bundle")
    return candidate


def _threshold(value):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or not 0 <= value <= 1):
        raise ModelArtifactError("Class thresholds must be finite values between zero and one")
    return float(value)


def read_classifier_manifest(model_dir):
    """Verify the complete portable bundle before loading MindSpore."""
    root = Path(model_dir).resolve()
    try:
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ModelArtifactError("A valid trained-classifier manifest.json is required") from exc
    if not isinstance(manifest, dict):
        raise ModelArtifactError("Classifier manifest must contain an object")
    for name, expected in {
        "format_version": 1, "framework": "mindspore",
        "task": "sms_spam_scam_detection", "checkpoint_type": "message_classifier",
    }.items():
        if manifest.get(name) != expected:
            raise ModelArtifactError("Only a fine-tuned MindSpore message classifier can serve predictions")
    if not isinstance(manifest.get("model_id"), str) or not manifest["model_id"].strip():
        raise ModelArtifactError("A nonempty trained model_id is required")
    label_map = manifest.get("id2label", manifest.get("labels"))
    if isinstance(label_map, list):
        label_map = {index: label for index, label in enumerate(label_map)}
    try:
        label_map = {int(key): value for key, value in label_map.items()}
    except (TypeError, ValueError, AttributeError) as exc:
        raise ModelArtifactError("Classifier label mapping is required") from exc
    if label_map != LABELS:
        raise ModelArtifactError("Expected normal=0, spam=1, and scam=2 labels")
    thresholds = manifest.get("thresholds", {"spam": 0.5, "scam": 0.5})
    if not isinstance(thresholds, dict) or any(name not in thresholds for name in ("spam", "scam")):
        raise ModelArtifactError("Spam and scam thresholds are required")
    for label in ("spam", "scam"):
        _threshold(thresholds[label])
    if "unwanted" in thresholds:
        _threshold(thresholds["unwanted"])
    files = {key: _asset(root, manifest.get(key)) for key in ("checkpoint", "config", "vocab")}
    for asset_name, hash_names in {
        "checkpoint": ("checkpoint_sha256",),
        "config": ("config_sha256",),
        "vocab": ("tokenizer_sha256", "vocab_sha256"),
    }.items():
        expected = next((manifest.get(name) for name in hash_names if manifest.get(name)), None)
        if not isinstance(expected, str) or len(expected) != 64 or sha256_file(files[asset_name]) != expected:
            raise ModelArtifactError(f"{asset_name} SHA256 does not match its manifest")
    if not isinstance(manifest.get("config_fingerprint"), str) or not manifest["config_fingerprint"]:
        raise ModelArtifactError("The model configuration fingerprint is required")
    length = manifest.get("max_length", manifest.get("pad_size", 128))
    if isinstance(length, bool) or not isinstance(length, int) or length < 2:
        raise ModelArtifactError("max_length must be an integer of at least two")
    if not isinstance(manifest.get("do_lower_case", True), bool):
        raise ModelArtifactError("do_lower_case must be boolean")
    return manifest, files


def validate_message(message):
    if not isinstance(message, str) or not message.strip() or len(message) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"Each message must contain text and be at most {MAX_MESSAGE_LENGTH} characters")
    return message


def classify_probabilities(probabilities, *, model_id, thresholds):
    """Convert class scores to cautious decisions without claiming legitimacy."""
    import numpy as np

    values = np.asarray(probabilities, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != 3 or not np.isfinite(values).all():
        raise RuntimeError("Classifier produced invalid class probabilities")
    if (values < 0).any() or (values > 1).any() or not np.allclose(values.sum(axis=1), 1, atol=1e-5):
        raise RuntimeError("Classifier probabilities are not normalized")
    results = []
    for scores in values:
        predicted_id = int(scores.argmax())
        # Float32 softmax summation can exceed one by a rounding unit.
        unwanted_score = float(np.clip(scores[1] + scores[2], 0., 1.))
        if "unwanted" in thresholds:
            flagged = unwanted_score >= thresholds["unwanted"]
        else:
            flagged = any(float(scores[label_id]) >= thresholds[LABELS[label_id]] for label_id in (1, 2))
        decision = "flag_for_review" if flagged else ("below_threshold" if predicted_id == 0 else "uncertain")
        results.append({
            "model_id": model_id,
            "predicted_label": LABELS[predicted_id],
            "scores": {label: float(scores[index]) for index, label in LABELS.items()},
            "unwanted_score": unwanted_score,
            "decision": decision,
            "thresholds": dict(thresholds),
        })
    return results


class MessagePredictor:
    def __init__(self, model_dir, device_target="CPU", batch_size=32):
        if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size < 1:
            raise ValueError("batch_size must be a positive integer")
        self.manifest, files = read_classifier_manifest(model_dir)
        from .config import MessageConfig
        from .runtime import configure_runtime
        from .tokenizer import MessageTokenizer

        self._ms = configure_runtime(device_target)
        from .model import MessageClassifier
        self.config = MessageConfig.from_json(files["config"])
        fingerprint = self.config.fingerprint
        if callable(fingerprint):
            fingerprint = fingerprint()
        if fingerprint != self.manifest["config_fingerprint"]:
            raise ModelArtifactError("The classifier configuration fingerprint does not match")
        max_length = self.manifest.get("max_length", self.manifest.get("pad_size", 128))
        self.tokenizer = MessageTokenizer(files["vocab"], max_length=max_length,
                                          do_lower_case=self.manifest.get("do_lower_case", True))
        if self.config.vocab_size != self.tokenizer.vocab_size:
            raise ModelArtifactError("Vocabulary size does not match the classifier configuration")
        if self.config.pad_token_id != self.tokenizer.pad_token_id:
            raise ModelArtifactError("Padding token ID does not match the classifier configuration")
        if max_length > self.config.max_position_embeddings:
            raise ModelArtifactError("Tokenizer length exceeds model position embeddings")
        self.model = MessageClassifier(self.config)
        parameters = self._ms.load_checkpoint(str(files["checkpoint"]))
        missing, unexpected = self._ms.load_param_into_net(self.model, parameters, strict_load=True)
        if missing or unexpected:
            raise ModelArtifactError("Classifier checkpoint does not match all model parameters")
        self.model.set_train(False)
        self.model_id = self.manifest["model_id"]
        self.thresholds = {label: _threshold(value) for label, value in
                           self.manifest.get("thresholds", {"spam": 0.5, "scam": 0.5}).items()
                           if label in ("spam", "scam", "unwanted")}
        self.batch_size = batch_size
        self._lock = Lock()

    def predict(self, messages):
        import numpy as np

        if isinstance(messages, str):
            raise ValueError("Pass a list of messages rather than one string")
        messages = [validate_message(message) for message in messages]
        predictions = []
        with self._lock:
            for start in range(0, len(messages), self.batch_size):
                batch_messages = messages[start:start + self.batch_size]
                encoded = self.tokenizer.encode_batch(batch_messages)
                tensors = [self._ms.Tensor(encoded[name], self._ms.int32)
                           for name in ("input_ids", "attention_mask", "token_type_ids")]
                logits = self.model(*tensors).asnumpy()
                if logits.shape != (len(batch_messages), 3) or not np.isfinite(logits).all():
                    raise RuntimeError("Classifier produced invalid logits")
                values = np.exp(logits - logits.max(axis=1, keepdims=True))
                probabilities = values / values.sum(axis=1, keepdims=True)
                predictions.extend(classify_probabilities(probabilities, model_id=self.model_id,
                                                         thresholds=self.thresholds))
        return predictions
