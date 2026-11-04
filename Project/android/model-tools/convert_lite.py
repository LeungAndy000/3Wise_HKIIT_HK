"""Convert the unchanged exported graph with the official end-side Lite tool."""
import argparse
import os
from pathlib import Path
import subprocess
import json

ROOT = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-dir", type=Path, default=ROOT / "artifacts/android/export_v1")
    args = parser.parse_args()
    lite = ROOT / "artifacts/android/tools/mindspore-lite-2.7.1-linux-x64"
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = f"{lite}/tools/converter/lib:{lite}/runtime/lib:" + env.get("LD_LIBRARY_PATH", "")
    command = [str(lite / "tools/converter/converter/converter_lite"),
               "--fmk=MINDIR", f"--modelFile={args.export_dir}/wisemessage_1x256.mindir",
               f"--outputFile={args.export_dir}/wisemessage", "--optimize=general",
               "--saveType=MINDIR_LITE", "--infer=true"]
    result = subprocess.run(command, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (args.export_dir / "converter.log").write_text(result.stdout)
    (args.export_dir / "converter_command.json").write_text(json.dumps(command, indent=2) + "\n")
    print(result.stdout, flush=True)
    return result.returncode

if __name__ == "__main__":
    raise SystemExit(main())
