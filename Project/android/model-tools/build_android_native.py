"""Relink official ARM64 static objects into a genuine 16 KB JNI library.

No ELF-header modifications are used. NDK r28+ clang/lld lays out fresh load
segments with 16 KB page alignment. The upstream archives remain untouched.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ndk", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path)
    args = parser.parse_args()
    from inspect_android_runtime import elf_loads
    toolchain = args.ndk / "toolchains/llvm/prebuilt/linux-x86_64/bin"
    compiler = toolchain / "aarch64-linux-android26-clang++"
    runtime = ROOT / "artifacts/android/tools/mindspore-lite-2.7.1-android-aarch64/runtime"
    target = ROOT / "android/app/src/main/jniLibs/arm64-v8a/libwisemessage_native.so"
    target.parent.mkdir(parents=True, exist_ok=True)
    report_dir = args.report_dir or ROOT / "artifacts/android" / datetime.now(timezone.utc).strftime("native_relink_%Y%m%dT%H%M%S_%fZ")
    report_dir.mkdir(parents=True, exist_ok=False)
    linked = report_dir / target.name
    command = [str(compiler), "-O2", "-fPIC", "-fvisibility=hidden", "-std=c++17", "-shared", "-static-libstdc++",
               "-Wl,-z,max-page-size=16384", "-Wl,-z,common-page-size=16384", "-Wl,--no-undefined",
               "-I", str(runtime), str(Path(__file__).with_name("wisemessage_jni.cc")),
               "-Wl,--whole-archive", str(runtime / "lib/libmindspore-lite.a"), "-Wl,--no-whole-archive",
               str(runtime / "third_party/securec/libsecurec.a"), "-llog", "-ldl", "-lm", "-latomic", "-o", str(linked)]
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (report_dir / "build.log").write_text(result.stdout)
    (report_dir / "command.json").write_text(json.dumps(command, indent=2) + "\n")
    print(result.stdout[-5000:], flush=True)
    result.check_returncode()
    loads = elf_loads(linked)
    result = subprocess.run([str(toolchain / "llvm-readelf"), "-d", "-l", str(linked)], text=True, stdout=subprocess.PIPE, check=True)
    (report_dir / "readelf.txt").write_text(result.stdout)
    report = {"library": str(target.relative_to(ROOT)), "bytes": linked.stat().st_size,
              "sha256": hashlib.sha256(linked.read_bytes()).hexdigest(), "pt_load": loads,
              "supports_16kb_alignment": all(p["alignment"] >= 16384 and (p["virtual_address"] - p["offset"]) % 16384 == 0 for p in loads),
              "method": "Real NDK clang/lld link of unchanged official MindSpore Lite 2.7.1 ARM64 static objects, whole-archive kernel registration; static libc++",
              "ndk": str(args.ndk), "jni_class": "hk.wisemessage.app.ml.NativeMessageEngine", "report_dir": str(report_dir),
              "input_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in
                  (runtime / "lib/libmindspore-lite.a", runtime / "third_party/securec/libsecurec.a", Path(__file__).with_name("wisemessage_jni.cc"))},
              "compiler_version": subprocess.run([str(compiler), "--version"], text=True, stdout=subprocess.PIPE, check=True).stdout.strip()}
    (report_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report), flush=True)
    if not report["supports_16kb_alignment"]:
        raise RuntimeError("Native load segments are not 16 KB aligned")
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != report["sha256"]:
        shutil.copy2(target, report_dir / "previous_libwisemessage_native.so")
    shutil.copy2(linked, target)
    (ROOT / "artifacts/android/native_relink_latest.json").write_text(json.dumps(report, indent=2) + "\n")

if __name__ == "__main__":
    main()
