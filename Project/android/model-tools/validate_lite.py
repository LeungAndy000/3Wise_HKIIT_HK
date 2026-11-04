"""Compile and run the exact end-side Lite CPU runtime on export parity inputs."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import hashlib

ROOT = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-dir", type=Path, default=ROOT / "artifacts/android/export_v1")
    args = parser.parse_args()
    lite = ROOT / "artifacts/android/tools/mindspore-lite-2.7.1-linux-x64"
    executable = args.export_dir / "lite_parity"
    subprocess.run(["g++", "-O2", "-std=c++17", "-D_GLIBCXX_USE_CXX11_ABI=0", str(Path(__file__).with_name("lite_parity.cc")),
                    "-I", str(lite / "runtime"), "-L", str(lite / "runtime/lib"),
                    f"-Wl,-rpath-link,{lite}/tools/converter/lib", "-lmindspore-lite", "-o", str(executable)], check=True)
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = f"{lite}/runtime/lib:{lite}/tools/converter/lib:" + env.get("LD_LIBRARY_PATH", "")
    export = json.loads((args.export_dir / "export_report.json").read_text())
    result = subprocess.run([str(executable), str(args.export_dir / "wisemessage.ms"), str(args.export_dir), str(export["samples"])],
                            text=True, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (args.export_dir / "lite_runtime.log").write_text(result.stdout)
    print(result.stdout[-5000:], flush=True)
    result.check_returncode()
    import numpy as np
    native = np.load(args.export_dir / "reference_logits.npy")
    converted = np.fromfile(args.export_dir / "lite_logits.bin", dtype=np.float32).reshape(native.shape)
    def softmax(x):
        e = np.exp(x - x.max(axis=1, keepdims=True))
        return e / e.sum(axis=1, keepdims=True)
    report = {"runtime": "mindspore-lite-2.7.1-end-side-linux-x64", "samples": len(native),
              "max_abs_logit_difference": float(np.max(np.abs(native - converted))),
              "max_abs_probability_difference": float(np.max(np.abs(softmax(native) - softmax(converted)))),
              "argmax_agreement": float(np.mean(native.argmax(1) == converted.argmax(1))),
              "model_sha256": hashlib.sha256((args.export_dir / "wisemessage.ms").read_bytes()).hexdigest(),
              "source_checkpoint_sha256": export["source_checkpoint_sha256"],
              "rtol": 0.001, "atol": 0.001}
    report["passed"] = bool(np.allclose(native, converted, rtol=0.001, atol=0.001) and report["argmax_agreement"] == 1)
    (args.export_dir / "lite_parity.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report), flush=True)
    if not report["passed"]:
        raise RuntimeError("Lite/native parity failed")

if __name__ == "__main__":
    main()
