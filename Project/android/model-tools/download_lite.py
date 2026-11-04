"""Fetch official, checksum-pinned MindSpore Lite end-side tools without deletion."""
from pathlib import Path
import hashlib
import json
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "artifacts/android/tools"
SOURCES = {
    "linux-x64": ("linux/x86_64", "78d288af3355094e190aca0308fa1bafaec99826c0627c1f1f8896737ad5456f"),
    "android-aarch64": ("android/gpu", "c67605f4ab2dab083c7c6c8bf7167c95e650de8845090e5572a081e14547e72e"),
}

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, (platform, digest) in SOURCES.items():
        filename = f"mindspore-lite-2.7.1-{name}.tar.gz"
        url = f"https://ms-release.obs.cn-north-4.myhuaweicloud.com/2.7.1/MindSporeLite/lite/release/{platform}/{filename}"
        target = DEST / filename
        if not target.exists():
            print(f"Downloading {url}", flush=True)
            urllib.request.urlretrieve(url, target)
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            raise RuntimeError(f"Checksum mismatch: {filename}: {actual}")
        with tarfile.open(target, "r:gz") as archive:
            archive.extractall(DEST, filter="data")
        results[name] = {"url": url, "sha256": actual, "bytes": target.stat().st_size}
        print(f"Verified {filename}", flush=True)
    (DEST / "downloads.json").write_text(json.dumps(results, indent=2) + "\n")

if __name__ == "__main__":
    main()
