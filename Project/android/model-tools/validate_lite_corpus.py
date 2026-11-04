"""Revalidate the local Lite graph on all previously reported labelled tests.

Uses immutable saved native MindSpore evaluation probabilities for comparison;
no model selection or threshold tuning occurs here.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

def main():
    import numpy as np
    from wisemessage.tokenizer import MessageTokenizer
    from wisemessage.metrics import binary_metrics, classification_metrics
    source = ROOT / "artifacts/runs/domain_v2_20261023_1050"
    export = ROOT / "artifacts/android/export_v2"
    target = ROOT / "artifacts/android/full_corpus_v1"
    target.mkdir(parents=True, exist_ok=True)
    lite = ROOT / "artifacts/android/tools/mindspore-lite-2.7.1-linux-x64"
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = f"{lite}/runtime/lib:{lite}/tools/converter/lib:" + env.get("LD_LIBRARY_PATH", "")
    subprocess.run(["g++", "-O2", "-std=c++17", "-D_GLIBCXX_USE_CXX11_ABI=0", str(Path(__file__).with_name("lite_parity.cc")),
                    "-I", str(lite / "runtime"), "-L", str(lite / "runtime/lib"),
                    f"-Wl,-rpath-link,{lite}/tools/converter/lib", "-lmindspore-lite", "-o", str(target / "lite_parity")], check=True)
    tokenizer = MessageTokenizer(source / "model/vocab.txt", 256, True)
    reference = json.loads((source / "evaluation/performance.json").read_text())
    report = {"status": "running", "source_checkpoint_sha256": reference["checkpoint_sha256"], "runtime": "mindspore-lite-2.7.1-end-side-linux-x64", "datasets": {}}
    started = time.monotonic()
    for name, original in reference["datasets"].items():
        if name == "external_unreviewed":
            continue
        datafile = ROOT / "data/prepared_domain_v2" / f"{name}.jsonl"
        digest = hashlib.sha256(datafile.read_bytes()).hexdigest()
        if digest != original["sha256"]:
            raise RuntimeError(f"Dataset changed: {name}")
        rows = [json.loads(line) for line in datafile.read_text(encoding="utf-8").splitlines() if line.strip()]
        if "identity_exclusions" in original:
            excluded = set(original["identity_exclusions"]["excluded_record_ids"])
            rows = [row for row in rows if row["record_id"] not in excluded]
        if len(rows) != original["samples"]:
            raise RuntimeError(f"Row count differs: {name}")
        inputs = tokenizer.encode_batch([row["text"] for row in rows])
        dataset_dir = target / name
        dataset_dir.mkdir(parents=True, exist_ok=True)
        for key, values in inputs.items():
            values.tofile(dataset_dir / f"full_{key}.bin")
        result = subprocess.run([str(target / "lite_parity"), str(export / "wisemessage.ms"), str(dataset_dir), str(len(rows))],
                                env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (dataset_dir / "runtime.log").write_text(result.stdout)
        result.check_returncode()
        timing = json.loads(result.stdout.splitlines()[-1])
        logits = np.fromfile(dataset_dir / "lite_logits.bin", np.float32).reshape(len(rows), 3)
        scores = np.exp(logits - logits.max(1, keepdims=True))
        scores /= scores.sum(1, keepdims=True)
        np.save(dataset_dir / "probabilities.npy", scores)
        native = np.load(source / "evaluation" / f"{name}_probabilities.npy")
        metrics = (binary_metrics(np.asarray([row["risk_label"] for row in rows]), scores[:, 1:].sum(1) >= 0.5)
                   if name in ("binary_domain_test", "external_mudou_binary")
                   else classification_metrics(np.asarray([row["label"] for row in rows]), scores))
        value = {"samples": len(rows), "dataset_sha256": digest, "timing": timing,
                 "max_abs_probability_difference": float(np.max(np.abs(scores - native))),
                 "argmax_agreement": float(np.mean(scores.argmax(1) == native.argmax(1))),
                 "unwanted_decision_agreement": float(np.mean((scores[:, 1:].sum(1) >= 0.5) == (native[:, 1:].sum(1) >= 0.5))),
                 "metrics": metrics, "evaluation_role": original["evaluation_role"]}
        value["passed"] = value["max_abs_probability_difference"] < 0.001 and value["argmax_agreement"] == 1 and value["unwanted_decision_agreement"] == 1
        report["datasets"][name] = value
        (target / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"dataset": name, **value}), flush=True)
    report.update(status="completed", elapsed_seconds=time.monotonic() - started,
                  passed=all(value["passed"] for value in report["datasets"].values()),
                  total_samples=sum(value["samples"] for value in report["datasets"].values()),
                  arm64_device_execution_verified=False)
    (target / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "datasets"}), flush=True)

if __name__ == "__main__":
    main()
