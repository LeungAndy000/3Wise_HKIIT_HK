"""Exercise the real Java/native bridge with the same source as Android."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]

def main():
    import numpy as np
    target = ROOT / "artifacts/android" / datetime.now(timezone.utc).strftime("host_jni_%Y%m%dT%H%M%S_%fZ")
    target.mkdir(parents=True)
    jdk = Path("/home/victor/.local/share/wisemessage-android/jdk-17.0.16+8")
    lite = ROOT / "artifacts/android/tools/mindspore-lite-2.7.1-linux-x64"
    bridge = Path(__file__).with_name("wisemessage_jni.cc")
    subprocess.run(["g++", "-O2", "-shared", "-fPIC", "-std=c++17", "-D_GLIBCXX_USE_CXX11_ABI=0",
                    "-I", str(jdk / "include"), "-I", str(jdk / "include/linux"), "-I", str(lite / "runtime"),
                    str(bridge), "-L", str(lite / "runtime/lib"), f"-Wl,-rpath-link,{lite}/tools/converter/lib",
                    "-lmindspore-lite", "-o", str(target / "libwisemessage_native.so")], check=True)
    engine = ROOT / "android/app/src/main/java/hk/wisemessage/app/ml/NativeMessageEngine.java"
    subprocess.run([str(jdk / "bin/javac"), "-d", str(target), str(engine), str(Path(__file__).with_name("NativeBridgeSmoke.java"))], check=True)
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = f"{lite}/runtime/lib:{lite}/tools/converter/lib:" + env.get("LD_LIBRARY_PATH", "")
    export = ROOT / "artifacts/android/export_v2"
    result = subprocess.run([str(jdk / "bin/java"), f"-Djava.library.path={target}", "-cp", str(target),
                             "hk.wisemessage.app.ml.NativeBridgeSmoke", str(export / "wisemessage.ms"), str(export), str(target / "jni_logits.bin")],
                            env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (target / "runtime.log").write_text(result.stdout)
    print(result.stdout, flush=True)
    result.check_returncode()
    native = np.load(export / "reference_logits.npy")
    jni = np.fromfile(target / "jni_logits.bin", np.float32).reshape(native.shape)
    report = {"samples": len(jni), "max_abs_logit_difference": float(np.max(np.abs(native - jni))),
              "argmax_agreement": float(np.mean(native.argmax(1) == jni.argmax(1))),
              "error_paths_checked": 4, "bridge_source_sha256": hashlib.sha256(bridge.read_bytes()).hexdigest(),
              "java_engine_sha256": hashlib.sha256(engine.read_bytes()).hexdigest(),
              "passed": bool(np.allclose(native, jni, atol=.001, rtol=.001) and np.mean(native.argmax(1) == jni.argmax(1)) == 1),
              "platform": "Linux x86_64; Android JNI source and Java native engine exercised on host"}
    (target / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report), flush=True)
    if not report["passed"]:
        raise RuntimeError("JNI/native model parity failed")

if __name__ == "__main__":
    main()
