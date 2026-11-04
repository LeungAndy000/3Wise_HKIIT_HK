"""Compare saved CPU/GPU demonstrations without executing either device."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time


ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--wait-seconds", type=int, default=0)
    parser.add_argument("--tolerance", type=float, default=.001)
    args = parser.parse_args(argv)
    if not 0 < args.tolerance <= .001:
        parser.error("tolerance must be positive and no greater than .001")
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = ROOT / run_dir
    output = run_dir / "runtime_validation"
    output.mkdir(parents=True, exist_ok=True)
    cpu_path = output / "report.json"
    gpu_path = run_dir / "evaluation/example_predictions.json"
    performance_path = run_dir / "evaluation/performance.json"
    deadline = time.monotonic() + max(0, args.wait_seconds)
    next_notice = 0
    while True:
        cpu, gpu, performance = map(read_json, (cpu_path, gpu_path, performance_path))
        if cpu and gpu and performance:
            break
        if time.monotonic() >= deadline:
            raise FileNotFoundError("Saved CPU, GPU example, and performance reports are not all ready")
        if time.monotonic() >= next_notice:
            print("Waiting for saved CPU and GPU reports", flush=True)
            next_notice = time.monotonic() + 30
        time.sleep(min(5, max(.01, deadline - time.monotonic())))
    report = {
        "purpose": "Read-only comparison of already computed CPU/GPU demonstration predictions; not an accuracy benchmark",
        "new_model_inference_performed": False, "tolerance": args.tolerance,
        "cpu_report": str(cpu_path), "gpu_examples_report": str(gpu_path),
        "compared_at": datetime.now(timezone.utc).isoformat(), "passed": False,
    }
    try:
        assert cpu["passed"], "CPU runtime validation did not pass"
        assert cpu["checkpoint_sha256"] == performance["checkpoint_sha256"], "Device reports reference different weights"
        cpu_examples = {value["message"]: value for value in cpu["example_predictions"]}
        gpu_examples = {value["message"]: value for value in gpu["examples"]}
        assert set(cpu_examples) == set(gpu_examples), "CPU/GPU demonstration messages do not match"
        assert len(cpu_examples) == len(cpu["example_predictions"]) == len(gpu["examples"]), "Duplicate demonstration messages"
        differences = []
        for message in cpu_examples:
            first, second = cpu_examples[message], gpu_examples[message]
            assert first["model_id"] == second["model_id"] == cpu["model_id"]
            assert first["thresholds"] == second["thresholds"], "Device reports reference different thresholds"
            maximum = max(abs(first["scores"][label] - second["scores"][label]) for label in ("normal", "spam", "scam"))
            unwanted_difference = abs(first["unwanted_score"] - second["unwanted_score"])
            same_decision = first["decision"] == second["decision"]
            differences.append({"message": message, "maximum_class_probability_difference": maximum,
                                "unwanted_probability_difference": unwanted_difference,
                                "cpu_decision": first["decision"], "gpu_decision": second["decision"],
                                "decisions_match": same_decision})
        report["model_id"] = cpu["model_id"]
        report["checkpoint_sha256"] = cpu["checkpoint_sha256"]
        report["samples"] = len(differences)
        report["per_message"] = differences
        report["maximum_class_probability_difference"] = max(value["maximum_class_probability_difference"] for value in differences)
        report["maximum_unwanted_probability_difference"] = max(value["unwanted_probability_difference"] for value in differences)
        report["all_aggregate_decisions_match"] = all(value["decisions_match"] for value in differences)
        assert report["maximum_class_probability_difference"] <= args.tolerance, "CPU/GPU class probability parity failed"
        assert report["maximum_unwanted_probability_difference"] <= args.tolerance, "CPU/GPU aggregate probability parity failed"
        assert report["all_aggregate_decisions_match"], "CPU/GPU aggregate review decisions differ"
        report["passed"] = True
    except (AssertionError, KeyError, ValueError) as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    path = output / "device_parity.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "report": str(path),
                      "maximum_probability_difference": report.get("maximum_class_probability_difference"),
                      "error": report.get("error")}), flush=True)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
