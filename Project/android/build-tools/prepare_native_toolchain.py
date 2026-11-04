#!/usr/bin/env python3
"""Fetch the NDK needed to link an actual 16 KB ARM64 MindSpore library."""
import hashlib
import json
import os
from pathlib import Path
import zipfile
import stat
import time
from bootstrap_toolchain import ROOT, TOOLS, DOWNLOADS, chunked_download, extract_zip

URL = 'https://dl.google.com/android/repository/android-ndk-r28c-linux.zip'
EXPECTED_SHA1 = 'a7b54a5de87fecd125a17d54f73c446199e72a64'
EXPECTED_BYTES = 722261334

def main():
    path = DOWNLOADS / 'android-ndk-r28c-linux.zip'
    if not path.exists() or path.stat().st_size != EXPECTED_BYTES or not zipfile.is_zipfile(path):
        chunked_download(URL, path)
    with path.open('rb') as stream:
        actual_sha1 = hashlib.file_digest(stream, 'sha1').hexdigest()
    if actual_sha1 != EXPECTED_SHA1:
        raise RuntimeError(f'Official NDK SHA-1 mismatch: {actual_sha1}')
    target = TOOLS / 'android-ndk-r28c'
    if not target.exists():
        extract_zip(path, TOOLS)
    # Preserve and repair symlink payload files from a prior Python ZIP extraction.
    # No files are deleted: the previous payload remains beside each repaired link.
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            if not stat.S_ISLNK(member.external_attr >> 16):
                continue
            destination = TOOLS / member.filename
            link_target = archive.read(member).decode()
            if not (destination.parent / link_target).resolve().is_relative_to(TOOLS.resolve()):
                raise RuntimeError('NDK symlink escapes isolated tools directory')
            if destination.is_symlink():
                if os.readlink(destination) != link_target:
                    raise RuntimeError('Existing NDK symlink differs from the verified archive')
                continue
            if destination.exists():
                if destination.read_bytes() != archive.read(member):
                    raise RuntimeError(f'Cannot repair unexpected NDK file: {destination}')
                destination.rename(destination.with_name(destination.name + f'.symlink-payload-preserved-{time.time_ns()}'))
            destination.symlink_to(link_target)
    report = {'url': URL, 'bytes': path.stat().st_size, 'sha1': actual_sha1,
              'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'version': '28.2.13676358', 'directory': str(target),
              'clang': str(target / 'toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang++'),
              'source': 'https://github.com/android/ndk/wiki/Unsupported-Downloads#r28c'}
    (ROOT / 'artifacts/android/toolchain/ndk.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2), flush=True)

if __name__ == '__main__':
    main()
