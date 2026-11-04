"""Bundle source licenses from the project and pinned upstream runtime archive."""
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]

def relevant(name):
    base = Path(name).name.lower()
    return "license" in base or "licence" in base or "notice" in base or base.startswith("copying")

def main():
    assets = ROOT / "android/app/src/main/assets/wisemessage"
    target = assets / "runtime-licenses"
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "LICENSE.txt", assets / "LICENSE.txt")
    archive = ROOT / "artifacts/android/tools/mindspore-lite-2.7.1-android-aarch64.ranges.tar.gz"
    copied = []
    examined = []
    with tarfile.open(archive) as tar:
        members = [member for member in tar.getmembers() if member.isfile()]
        for member in members:
            if relevant(member.name):
                relative = Path(*Path(member.name).parts[1:])
                if relative.is_absolute() or ".." in relative.parts:
                    raise ValueError("Unsafe upstream archive path")
                destination = target / "archive" / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                data = tar.extractfile(member).read()
                destination.write_bytes(data)
                copied.append({"source": member.name, "asset": str(destination.relative_to(assets)),
                               "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
        examined.append(str(archive.relative_to(ROOT)))
    runtime_root = archive.parent / "mindspore-lite-2.7.1-android-aarch64"
    for aar in runtime_root.glob("*.aar"):
        with zipfile.ZipFile(aar) as zipped:
            for name in zipped.namelist():
                if name.endswith("/") or not relevant(name):
                    continue
                relative = Path(name)
                if relative.is_absolute() or ".." in relative.parts:
                    raise ValueError("Unsafe upstream AAR path")
                destination = target / aar.stem / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                data = zipped.read(name)
                destination.write_bytes(data)
                copied.append({"source": f"{aar.name}!{name}", "asset": str(destination.relative_to(assets)),
                               "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
        examined.append(str(aar.relative_to(ROOT)))
    report = {"project_license": "assets/wisemessage/LICENSE.txt", "upstream_archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
              "examined": examined, "upstream_notices": copied,
              "note": "Only actual files distributed by the upstream archive/AAR were copied; no license text was inferred or invented."}
    (ROOT / "artifacts/android/runtime_license_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report), flush=True)

if __name__ == "__main__":
    main()
