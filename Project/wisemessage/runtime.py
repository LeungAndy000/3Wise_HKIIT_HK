"""Native MindSpore setup with configurable, externally installed CUDA libraries."""

import os
from pathlib import Path


def configure_environment():
    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    configured_cuda = os.environ.get("WISEMESSAGE_CUDA_HOME") or os.environ.get("CUDA_HOME")
    cuda = Path(configured_cuda or "/home/victor/.venvs/mindspore-gpu/cuda-11.6")
    if cuda.is_dir() and (Path("/dev/dxg").exists() or configured_cuda):
        libraries = [Path("/usr/lib/wsl/lib"), cuda.parent / "lib/mindspore-cuda"]
        nvidia_root = Path(os.environ.get("WISEMESSAGE_NVIDIA_LIBRARY_ROOT") or
                           "/home/victor/.venvs/mindspore-gpu/lib/python3.11/site-packages/nvidia")
        libraries.extend(sorted(nvidia_root.glob("*/lib")))
        libraries.extend(Path(value) for value in
                         os.environ.get("WISEMESSAGE_CUDA_LIBRARY_DIRS", "").split(os.pathsep) if value)
        os.environ["CUDA_HOME"] = str(cuda)
        os.environ["PATH"] = os.pathsep.join(dict.fromkeys(
            [str(cuda / "bin"), *filter(None, os.environ.get("PATH", "").split(os.pathsep))]))
        # Preserve caller-provided libraries; repeat startup calls remain idempotent.
        os.environ["LD_LIBRARY_PATH"] = os.pathsep.join(dict.fromkeys(
            [*(str(path) for path in libraries if path.is_dir()),
             *filter(None, os.environ.get("LD_LIBRARY_PATH", "").split(os.pathsep))]))


def configure_runtime(device_target="CPU", seed=2026, tf32=True):
    configure_environment()
    import mindspore as ms
    if device_target not in {"CPU", "GPU", "Ascend"}:
        raise ValueError("Unsupported device target")
    if ms.get_context("device_target") != device_target:
        ms.set_device(device_target)
    ms.set_context(mode=ms.PYNATIVE_MODE)
    if device_target == "GPU" and tf32:
        ms.set_context(gpu_config={"matmul_allow_tf32": True, "conv_allow_tf32": True})
    ms.set_seed(seed)
    return ms
