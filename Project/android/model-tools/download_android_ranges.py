"""Resilient official artifact download with checked HTTP byte ranges."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import tarfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "artifacts/android/tools"
URL = "https://ms-release.obs.cn-north-4.myhuaweicloud.com/2.7.1/MindSporeLite/lite/release/android/gpu/mindspore-lite-2.7.1-android-aarch64.tar.gz"
TOTAL = 37358185
SHA = "c67605f4ab2dab083c7c6c8bf7167c95e650de8845090e5572a081e14547e72e"

def get_chunk(index):
    start = index * 1024 * 1024
    end = min(TOTAL - 1, start + 1024 * 1024 - 1)
    path = DEST / "android_range_parts" / f"{index:03d}.bin"
    if path.is_file() and path.stat().st_size == end - start + 1:
        return path
    for attempt in range(8):
        try:
            request = urllib.request.Request(URL, headers={"Range": f"bytes={start}-{end}"})
            with urllib.request.urlopen(request, timeout=20) as response:
                if response.status != 206 or response.headers.get("Content-Range") != f"bytes {start}-{end}/{TOTAL}":
                    raise RuntimeError("Invalid HTTP range response")
                data = response.read()
            if len(data) != end - start + 1:
                raise RuntimeError("Truncated range")
            path.write_bytes(data)
            print(f"chunk {index} verified length {len(data)}", flush=True)
            return path
        except Exception as error:
            print(f"chunk {index} retry {attempt}: {error}", flush=True)
            time.sleep(1)
    raise RuntimeError(f"Cannot download range {index}")

def main():
    (DEST / "android_range_parts").mkdir(parents=True, exist_ok=True)
    count = (TOTAL + 1024 * 1024 - 1) // (1024 * 1024)
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = [pool.submit(get_chunk, index) for index in range(count)]
        for result in as_completed(results):
            result.result()
    target = DEST / "mindspore-lite-2.7.1-android-aarch64.ranges.tar.gz"
    with target.open("wb") as output:
        for index in range(count):
            output.write((DEST / "android_range_parts" / f"{index:03d}.bin").read_bytes())
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    if actual != SHA:
        raise RuntimeError(f"Official checksum mismatch: {actual}")
    print(f"Official SHA verified: {actual}", flush=True)
    # Extract only Java/AAR/native runtime files, avoiding unnecessary source trees.
    with tarfile.open(target) as archive:
        members = [member for member in archive.getmembers() if "/runtime/" in member.name]
        archive.extractall(DEST, members=members, filter="data")
    (DEST / "android_download.json").write_text(json.dumps({"url": URL, "sha256": actual, "bytes": TOTAL}, indent=2) + "\n")
    print("Android runtime extracted", flush=True)

if __name__ == "__main__":
    main()
