"""Export the trained native MindSpore classifier for local Android deployment.

Run in the existing WiseMessage MindSpore WSL environment. No retraining or
checkpoint rewriting is performed. All intermediate files remain available.
"""
import argparse
from pathlib import Path
import hashlib
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, default=ROOT / "artifacts/runs/domain_v2_20261023_1050/model")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/android/export_v1")
    parser.add_argument("--samples", type=int, default=96)
    parser.add_argument("--format", choices=["MINDIR", "ONNX"], default="MINDIR")
    parser.add_argument("--portable-scalars", action="store_true")
    args = parser.parse_args()
    import mindspore as ms
    import numpy as np
    from wisemessage.config import MessageConfig
    from wisemessage.model import MessageClassifier
    from wisemessage.tokenizer import MessageTokenizer

    ms.set_context(mode=ms.GRAPH_MODE, device_target="CPU")
    ms.set_seed(2026)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((args.model_dir / "manifest.json").read_text(encoding="utf-8"))
    checkpoint = args.model_dir / manifest["checkpoint"]
    if sha256(checkpoint) != manifest["checkpoint_sha256"]:
        raise ValueError("Trained checkpoint checksum mismatch")
    config = MessageConfig.from_json(args.model_dir / manifest["config"])
    net = MessageClassifier(config)
    missing, unused = ms.load_param_into_net(net, ms.load_checkpoint(str(checkpoint)), strict_load=True)
    if missing or unused:
        raise ValueError(f"Strict checkpoint load failed: {missing}, {unused}")
    net.set_train(False)
    export_net = net
    if args.portable_scalars:
        sys.path.insert(0, str(ROOT / "android/model-tools"))
        from portable_network import PortableClassifier
        export_net = PortableClassifier(config)
        missing, unused = ms.load_param_into_net(export_net, ms.load_checkpoint(str(checkpoint)), strict_load=True)
        if missing or unused:
            raise ValueError(f"Portable checkpoint load failed: {missing}, {unused}")
        export_net.set_train(False)
    tokenizer = MessageTokenizer(args.model_dir / manifest["vocab"], manifest["max_length"], manifest["do_lower_case"])
    datafile = ROOT / "data/domain_v2/test.jsonl"
    if not datafile.exists():
        candidates = list((ROOT / "data").glob("*/test.jsonl"))
        datafile = next((p for p in candidates if "domain" in p.parent.name), candidates[0])
    rows = [json.loads(line) for line in datafile.read_text(encoding="utf-8").splitlines() if line.strip()]
    # Deterministic stratified coverage is used solely to verify export parity.
    selected = []
    groups = {}
    for row in rows:
        groups.setdefault(str(row.get("label")), []).append(row)
    for index in range(args.samples):
        label = sorted(groups)[index % len(groups)]
        choices = groups[label]
        selected.append(choices[(index // len(groups) * 37) % len(choices)])
    texts = [row["text"] for row in selected]
    encoded = tokenizer.encode_batch(texts)
    inputs = [ms.Tensor(encoded[name][0:1]) for name in ("input_ids", "attention_mask", "token_type_ids")]
    stem = args.output_dir / "wisemessage_1x256"
    started = time.monotonic()
    ms.export(export_net, *inputs, file_name=str(stem), file_format=args.format)
    print(f"Exported {stem} {args.format}", flush=True)
    logits = []
    portable_logits = []
    for index in range(len(texts)):
        batch = [ms.Tensor(encoded[name][index:index + 1]) for name in ("input_ids", "attention_mask", "token_type_ids")]
        logits.append(net(*batch).asnumpy()[0])
        if args.portable_scalars:
            portable_logits.append(export_net(*batch).asnumpy()[0])
    np.savez(args.output_dir / "parity_inputs.npz", **encoded)
    np.save(args.output_dir / "reference_logits.npy", np.asarray(logits, np.float32))
    portable_max_abs = 0.0
    if args.portable_scalars:
        portable_max_abs = float(np.max(np.abs(np.asarray(logits) - np.asarray(portable_logits))))
        np.save(args.output_dir / "portable_logits.npy", np.asarray(portable_logits, np.float32))
        if not np.allclose(logits, portable_logits, atol=0.0001, rtol=0.0001):
            raise RuntimeError(f"Portable-wrapper equivalence failed: {portable_max_abs}")
    for index in range(len(texts)):
        sample_dir = args.output_dir / "binary_inputs" / str(index)
        sample_dir.mkdir(parents=True, exist_ok=True)
        for name, values in encoded.items():
            values[index:index + 1].tofile(sample_dir / f"{name}.bin")
    (args.output_dir / "parity_texts.json").write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = {
        "model_id": manifest["model_id"], "source_checkpoint_sha256": sha256(checkpoint),
        "framework_version": ms.__version__, "export_format": args.format,
        "source_test_file": str(datafile.relative_to(ROOT)), "source_test_sha256": sha256(datafile),
        "samples": len(texts), "input_order": ["input_ids", "attention_mask", "token_type_ids"],
        "input_shape": [1, manifest["max_length"]], "input_dtype": "int32",
        "output_shape": [1, 3], "output_dtype": "float32", "output_semantics": "unnormalized logits",
        "labels": ["normal", "spam", "scam"], "elapsed_seconds": time.monotonic() - started,
        "portable_scalar_reciprocals": args.portable_scalars, "wrapper_max_abs_difference": portable_max_abs,
    }
    (args.output_dir / "export_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
