#!/usr/bin/env python3
"""Install pinned local Android build tools without changing system packages."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import urllib.request
import zipfile
import time
import stat

def chunked_download(url, path):
    head = urllib.request.Request(url, method='HEAD')
    with urllib.request.urlopen(head, timeout=30) as response:
        length = int(response.headers['Content-Length'])
        final_url = response.url
    chunk_size = 2 * 1024 * 1024
    chunks = TOOLS / 'download-chunks' / path.name
    chunks.mkdir(parents=True, exist_ok=True)
    def part(start):
        end = min(start + chunk_size, length) - 1
        destination = chunks / f'{start:012d}-{end:012d}.part'
        if destination.exists() and destination.stat().st_size == end - start + 1:
            return destination
        for attempt in range(6):
            try:
                request = urllib.request.Request(final_url, headers={'Range': f'bytes={start}-{end}', 'User-Agent': 'WiseMessage-Android-Build'})
                with urllib.request.urlopen(request, timeout=25) as response:
                    if response.status != 206:
                        raise RuntimeError('Server did not honor byte range')
                    data = response.read(end - start + 2)
                if len(data) != end - start + 1:
                    raise RuntimeError(f'Short chunk: {len(data)}')
                destination.write_bytes(data)
                return destination
            except Exception:
                if attempt == 5:
                    raise
                time.sleep(1 + attempt)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        parts = list(pool.map(part, range(0, length, chunk_size)))
    if path.exists():
        backup = path.with_name(path.name + f'.partial-preserved-{time.time_ns()}')
        path.rename(backup)
    with path.open('wb') as output:
        for source in parts:
            output.write(source.read_bytes())
    print(f'Download complete: {path.name} ({length} bytes)', flush=True)

ROOT = Path(__file__).resolve().parents[2]
TOOLS = Path(os.environ.get('WISEMESSAGE_ANDROID_TOOLS', '/home/victor/.local/share/wisemessage-android'))
DOWNLOADS = ROOT / 'artifacts/android/toolchain/downloads'

def fetch(url, path, expected=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    incomplete_archive = path.suffix == '.zip' and path.exists() and not zipfile.is_zipfile(path)
    if not path.exists() or incomplete_archive or (expected and hashlib.sha256(path.read_bytes()).hexdigest() != expected):
        print('Download', url, flush=True)
        chunked_download(url, path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected and digest != expected:
        raise RuntimeError(f'Checksum mismatch for {path}: {digest}')
    return {'url': url, 'file': path.name, 'sha256': digest}

def extract_zip(source, target):
    with zipfile.ZipFile(source) as archive:
        for member in archive.infolist():
            destination = target / member.filename
            if not destination.resolve().is_relative_to(target.resolve()):
                raise RuntimeError('Archive entry escapes extraction directory')
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode):
                link_target = archive.read(member).decode()
                if not (destination.parent / link_target).resolve().is_relative_to(target.resolve()):
                    raise RuntimeError('Archive symlink escapes extraction directory')
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.symlink_to(link_target)
                continue
            archive.extract(member, target)
            if mode:
                destination.chmod(mode)

def main():
    TOOLS.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    jdk_name = 'OpenJDK17U-jdk_x64_linux_hotspot_17.0.16_8.tar.gz'
    jdk_url = 'https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.16%2B8/' + jdk_name
    checksum = urllib.request.urlopen(jdk_url + '.sha256.txt').read().decode().split()[0]
    jdk_package = {'link': jdk_url, 'name': jdk_name, 'checksum': checksum}
    gradle_url = 'https://services.gradle.org/distributions/gradle-8.13-bin.zip'
    gradle_sha = urllib.request.urlopen(gradle_url + '.sha256').read().decode().strip()
    sdk_url = 'https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip'
    plans = [(jdk_package['link'], DOWNLOADS / jdk_package['name'], jdk_package['checksum']),
             (gradle_url, DOWNLOADS / 'gradle-8.13-bin.zip', gradle_sha),
             (sdk_url, DOWNLOADS / 'commandlinetools-linux-13114758_latest.zip', '7ec965280a073311c339e571cd5de778b9975026cfcbe79f2b1cdcb1e15317ee')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda p: fetch(*p), plans))
    jdk_dir = TOOLS / 'jdk-17.0.16+8'
    if not jdk_dir.exists():
        with tarfile.open(plans[0][1]) as archive:
            archive.extractall(TOOLS, filter='data')
        candidates = sorted(TOOLS.glob('jdk-17*'))
        if len(candidates) != 1:
            raise RuntimeError(f'Ambiguous JDK paths: {candidates}')
        jdk_dir = candidates[0]
    gradle_dir = TOOLS / 'gradle-8.13'
    if not gradle_dir.exists():
        extract_zip(plans[1][1], TOOLS)
    sdk_dir = TOOLS / 'android-sdk'
    cmd_dir = sdk_dir / 'cmdline-tools/19.0'
    if not cmd_dir.exists():
        cmd_dir.mkdir(parents=True)
        with zipfile.ZipFile(plans[2][1]) as archive:
            for member in archive.infolist():
                relative = Path(member.filename).relative_to('cmdline-tools')
                if not str(relative) or str(relative) == '.':
                    continue
                destination = cmd_dir / relative
                if member.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(archive.read(member))
                    mode = member.external_attr >> 16
                    if mode:
                        destination.chmod(mode)
    environment = os.environ.copy()
    environment.update(JAVA_HOME=str(jdk_dir), ANDROID_HOME=str(sdk_dir), ANDROID_SDK_ROOT=str(sdk_dir))
    environment['PATH'] = str(jdk_dir / 'bin') + ':' + environment['PATH']
    sdkmanager = str(cmd_dir / 'bin/sdkmanager')
    for name, command, stdin in [
        ('sdk-license-acceptance.log', [sdkmanager, '--sdk_root=' + str(sdk_dir), '--licenses'], 'y\n' * 100),
        ('sdk-package-installation.log', [sdkmanager, '--sdk_root=' + str(sdk_dir), 'platforms;android-36', 'build-tools;36.0.0', 'platform-tools'], None),
    ]:
        result = subprocess.run(command, input=stdin, text=True, env=environment,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (ROOT / 'artifacts/android/toolchain' / name).write_text(result.stdout)
        if result.returncode:
            raise RuntimeError(f'SDK tool failed; see {name}: {result.stdout[-1500:]}')
    manifest = {'jdk': str(jdk_dir), 'gradle': str(gradle_dir), 'android_sdk': str(sdk_dir), 'downloads': results, 'agp': '8.13.2', 'gradle_version': '8.13', 'compile_sdk': 36, 'build_tools': '36.0.0'}
    (ROOT / 'artifacts/android/toolchain/toolchain.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2), flush=True)

if __name__ == '__main__':
    main()
