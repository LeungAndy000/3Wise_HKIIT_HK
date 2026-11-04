"""Download pinned official MiniRBT sources, or safely bridge its torch weights."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

REPO = "hfl/minirbt-h256"
REVISION = "446e1b4012b10946f479563005700c54c9db3f7c"
FILES = ("config.json", "vocab.txt", "README.md", "pytorch_model.bin")


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(data)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("download", "extract"))
    parser.add_argument("--output-dir", default="artifacts/sources/minirbt")
    args = parser.parse_args()
    root = Path(args.output_dir)
    root.mkdir(parents=True, exist_ok=True)
    if args.phase == "download":
        provenance = {"repository": REPO, "revision": REVISION, "license": "apache-2.0", "files": {}}
        for name in FILES:
            url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{name}"
            target = root / name
            if not target.exists():
                urllib.request.urlretrieve(url, target)
            if target.stat().st_size < 20:
                raise ValueError(f"Invalid source file: {name}")
            provenance["files"][name] = {"url": url, "sha256": digest(target), "bytes": target.stat().st_size}
            print(json.dumps({"phase": "downloaded", "file": name, **provenance["files"][name]}), flush=True)
        provenance["downloaded_at"] = datetime.now(timezone.utc).isoformat()
        (root / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    else:
        import numpy as np
        import torch
        source = torch.load(root / "pytorch_model.bin", map_location="cpu", weights_only=True)
        if not isinstance(source, dict) or not all(isinstance(key, str) and torch.is_tensor(value) for key, value in source.items()):
            raise ValueError("Expected a tensor-only named state dict")
        values = {key: value.detach().cpu().numpy() for key, value in source.items()}
        bridge = root / "source_state.npz"
        if bridge.exists():
            raise ValueError("NPZ bridge already exists; refusing to replace it")
        np.savez(bridge, **values)
        (root / "extraction.json").write_text(json.dumps({"safe_weights_only": True, "torch_version": torch.__version__,
            "source_sha256": digest(root / "pytorch_model.bin"), "npz_sha256": digest(bridge),
            "tensors": {key: {"shape": list(value.shape), "dtype": str(value.dtype)} for key, value in values.items()}}, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"phase": "extracted", "tensors": len(values), "npz_bytes": bridge.stat().st_size}), flush=True)


if __name__ == "__main__":
    main()
