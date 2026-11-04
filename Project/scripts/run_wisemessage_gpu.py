"""Launch the WiseMessage CLI with CUDA libraries visible at process startup.

Example, inside the project's WSL MindSpore environment:
    python scripts/run_wisemessage_gpu.py predict \
        --model-dir artifacts/runs/domain_v2_20261023_1050/model \
        --device-target GPU --message '請檢查這則訊息'

Arguments are passed directly as an argv list, without a shell.
"""

import os
from pathlib import Path
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))


def main():
    from wisemessage.runtime import configure_environment
    configure_environment()
    argv = sys.argv[1:]
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        argv = ["--help"]
    environment = os.environ.copy()
    # The child receives LD_LIBRARY_PATH before Python/MindSpore initializes.
    result = subprocess.run([sys.executable, "-m", "wisemessage", *argv],
                            cwd=PROJECT, env=environment, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
