#!/usr/bin/env python3
"""Download official Windows ADB so USB phones need no WSL USB forwarding."""
import hashlib
import json
from pathlib import Path
import zipfile
from bootstrap_toolchain import ROOT, DOWNLOADS, chunked_download, extract_zip

def main():
    url = 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip'
    archive = DOWNLOADS / 'platform-tools-windows-build-20261023.zip'
    if not archive.exists() or not zipfile.is_zipfile(archive):
        chunked_download(url, archive)
    destination = ROOT / 'artifacts/android/toolchain/windows-platform-tools'
    adb = destination / 'platform-tools/adb.exe'
    if not adb.exists():
        extract_zip(archive, destination)
    properties = (destination / 'platform-tools/source.properties').read_text()
    report = {'url': url, 'archive': str(archive.relative_to(ROOT)), 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'bytes': archive.stat().st_size, 'adb': str(adb.relative_to(ROOT)), 'source_properties': properties.splitlines()}
    (ROOT / 'artifacts/android/toolchain/windows-adb.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
