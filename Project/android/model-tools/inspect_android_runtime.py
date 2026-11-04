"""Record native alignment and extract official Java archives for provenance."""
import hashlib
import json
from pathlib import Path
import struct
import tarfile

ROOT = Path(__file__).resolve().parents[2]

def elf_loads(path):
    data = path.read_bytes()
    if data[:5] != b"\x7fELF\x02":
        raise ValueError("Expected 64-bit ELF")
    endian = "<" if data[5] == 1 else ">"
    offset = struct.unpack_from(endian + "Q", data, 32)[0]
    entsize, count = struct.unpack_from(endian + "HH", data, 54)
    loads = []
    for index in range(count):
        header = struct.unpack_from(endian + "IIQQQQQQ", data, offset + index * entsize)
        if header[0] == 1:
            loads.append({"offset": header[2], "virtual_address": header[3], "alignment": header[7]})
    return loads

def main():
    tools = ROOT / "artifacts/android/tools"
    archive = tools / "mindspore-lite-2.7.1-android-aarch64.ranges.tar.gz"
    with tarfile.open(archive) as tar:
        members = [m for m in tar.getmembers() if m.name.endswith((".aar", ".jar"))]
        tar.extractall(tools, members=members, filter="data")
        print("Java files:", [m.name for m in members], flush=True)
    runtime = tools / "mindspore-lite-2.7.1-android-aarch64/runtime"
    report = {"official_archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "libraries": {}}
    for path in (runtime / "lib").glob("*.so"):
        loads = elf_loads(path)
        report["libraries"][path.name] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "pt_load": loads,
                                          "supports_16kb_alignment": all(p["alignment"] >= 16384 for p in loads)}
    (ROOT / "artifacts/android/official_android_alignment.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report), flush=True)

if __name__ == "__main__":
    main()
