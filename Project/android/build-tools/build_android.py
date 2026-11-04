#!/usr/bin/env python3
"""Build and inspect WiseMessage APKs with isolated WSL tools; never installs."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
ANDROID = ROOT / 'android'
ARTIFACTS = ROOT / 'artifacts/android'

def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def run(command, env, log_file, check=True):
    print('Run:', ' '.join(str(x) for x in command), flush=True)
    result = subprocess.run([str(x) for x in command], cwd=ANDROID, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(result.stdout)
    print(result.stdout[-6000:], flush=True)
    if check and result.returncode:
        raise subprocess.CalledProcessError(result.returncode, command, result.stdout)
    return result

def ensure_wrapper(gradle_sha, offline=False):
    urls = {
        'gradlew': 'https://raw.githubusercontent.com/gradle/gradle/v8.13.0/gradlew',
        'gradlew.bat': 'https://raw.githubusercontent.com/gradle/gradle/v8.13.0/gradlew.bat',
        'gradle/wrapper/gradle-wrapper.jar': 'https://raw.githubusercontent.com/gradle/gradle/v8.13.0/gradle/wrapper/gradle-wrapper.jar',
    }
    for relative, url in urls.items():
        destination = ANDROID / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            if offline:
                raise RuntimeError(f'Offline build requires the existing Gradle wrapper: {destination}')
            urllib.request.urlretrieve(url, destination)
    if offline:
        previous = json.loads((ARTIFACTS / 'latest_build.json').read_text())
        expected = json.loads((ROOT / previous['report']).read_text())['wrapper_jar_sha256']
    else:
        expected = urllib.request.urlopen('https://services.gradle.org/distributions/gradle-8.13-wrapper.jar.sha256').read().decode().strip()
    actual = sha256(ANDROID / 'gradle/wrapper/gradle-wrapper.jar')
    if expected != actual:
        raise RuntimeError('Gradle wrapper JAR checksum mismatch')
    (ANDROID / 'gradlew').chmod(0o755)
    (ANDROID / 'gradle/wrapper/gradle-wrapper.properties').write_text(
        'distributionBase=GRADLE_USER_HOME\n'
        'distributionPath=wrapper/dists\n'
        'distributionUrl=https\\://services.gradle.org/distributions/gradle-8.13-bin.zip\n'
        f'distributionSha256Sum={gradle_sha}\n'
        'networkTimeout=120000\nvalidateDistributionUrl=true\n'
        'zipStoreBase=GRADLE_USER_HOME\nzipStorePath=wrapper/dists\n')
    return actual

def ensure_signing(jdk, environment, logs):
    configured = environment.get('WISEMESSAGE_SIGNING_DIR')
    if not configured:
        raise RuntimeError('Set WISEMESSAGE_SIGNING_DIR to the existing private signing directory. No new signing identity will be created.')
    signing = Path(configured).expanduser()
    if not signing.is_absolute():
        raise RuntimeError('WISEMESSAGE_SIGNING_DIR must be an absolute path outside the submission folder.')
    signing = signing.resolve(strict=True)
    if signing.is_relative_to(ROOT.parent.resolve()):
        raise RuntimeError('Keep the private signing directory outside the submission folder.')
    props = signing / 'test-signing.properties'
    key_file = signing / 'wisemessage-test.jks'
    if not key_file.is_file() or not props.is_file():
        raise RuntimeError('The existing signing key and matching properties are required. Restore the preserved pair; no new identity will be created.')
    environment['WISEMESSAGE_SIGNING_DIR'] = str(signing)

def elf_segments(data):
    if data[:4] != b'\x7fELF' or data[4] != 2 or data[5] != 1:
        raise RuntimeError('Expected little-endian ELF64 ARM64 library')
    machine = struct.unpack_from('<H', data, 18)[0]
    if machine != 183:
        raise RuntimeError(f'Expected ARM64 machine 183, got {machine}')
    offset = struct.unpack_from('<Q', data, 32)[0]
    size, count = struct.unpack_from('<HH', data, 54)
    segments = []
    for index in range(count):
        segment = struct.unpack_from('<IIQQQQQQ', data, offset + index * size)
        if segment[0] == 1:
            _, flags, file_offset, vaddr, _, _, _, alignment = segment
            segments.append({'flags': flags, 'offset': file_offset, 'vaddr': vaddr, 'alignment': alignment,
                             'compatible_16kb': alignment >= 16384 and file_offset % 16384 == vaddr % 16384})
    return segments

def inspect_apk(apk, environment, sdk, logs):
    build_tools = sdk / 'build-tools/36.0.0'
    signature = run([build_tools / 'apksigner', 'verify', '--verbose', '--print-certs', apk], environment,
                    logs / (apk.stem + '-signature.log'))
    alignment = run([build_tools / 'zipalign', '-c', '-P', '16', '-v', '4', apk], environment,
                    logs / (apk.stem + '-zipalign.log'))
    badging = run([build_tools / 'aapt', 'dump', 'badging', apk], environment,
                  logs / (apk.stem + '-badging.log'))
    permissions = run([build_tools / 'aapt', 'dump', 'permissions', apk], environment,
                      logs / (apk.stem + '-permissions.log'))
    libraries = []
    assets = []
    with zipfile.ZipFile(apk) as archive:
        for item in archive.infolist():
            if item.filename.endswith('.so'):
                native_data = archive.read(item)
                segments = elf_segments(native_data)
                if not all(segment['compatible_16kb'] for segment in segments):
                    raise RuntimeError(f'Native library does not support 16 KB pages: {item.filename}: {segments}')
                if not item.filename.startswith('lib/arm64-v8a/'):
                    raise RuntimeError(f'Unexpected ABI: {item.filename}')
                libraries.append({'path': item.filename, 'bytes': item.file_size,
                                  'sha256': hashlib.sha256(native_data).hexdigest(), 'load_segments': segments,
                                  'compressed': item.compress_type != zipfile.ZIP_STORED})
            if item.filename.startswith('assets/'):
                assets.append({'path': item.filename, 'bytes': item.file_size,
                               'sha256': hashlib.sha256(archive.read(item)).hexdigest()})
    if not libraries:
        raise RuntimeError('No ARM64 native inference libraries packaged')
    if not any(item['path'].endswith(('.ms', '.mindir')) for item in assets):
        raise RuntimeError('No local model asset packaged')
    if 'android.permission.INTERNET' in permissions.stdout:
        raise RuntimeError('WiseMessage must not request Internet permission')
    cert = re.search(r'certificate SHA-256 digest: ([0-9a-f]+)', signature.stdout)
    return {'apk': str(apk.relative_to(ROOT)), 'bytes': apk.stat().st_size, 'sha256': sha256(apk),
            'signature_verified': signature.returncode == 0, 'certificate_sha256': cert.group(1) if cert else None,
            'zipalign_16kb_passed': alignment.returncode == 0, 'elf_16kb_passed': True,
            'native_libraries': libraries, 'assets': assets,
            'permissions': permissions.stdout.splitlines(),
            'badging_log': str((logs / (apk.stem + '-badging.log')).relative_to(ROOT))}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-tests', action='store_true')
    parser.add_argument('--skip-lint', action='store_true')
    parser.add_argument('--compile-only', action='store_true', help='Run Java, JVM tests and lint before native packaging')
    parser.add_argument('--offline', action='store_true', help='Use existing verified tools and Gradle caches without network access')
    parser.add_argument('--reuse-native', action='store_true', help='Preserve the verified JNI runtime for UI-only updates')
    args = parser.parse_args()
    gradle_source = (ANDROID / 'app/build.gradle').read_text()
    version = re.search(r"versionName\s+'([0-9A-Za-z.-]+)'", gradle_source).group(1)
    version_code = int(re.search(r'versionCode\s+(\d+)', gradle_source).group(1))
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    logs = ARTIFACTS / 'builds' / stamp
    logs.mkdir(parents=True)
    toolchain_file = ARTIFACTS / 'toolchain/toolchain.json'
    if not toolchain_file.exists():
        if args.offline: raise RuntimeError('Offline build needs the existing Android toolchain')
        subprocess.run(['python3', str(ANDROID / 'build-tools/bootstrap_toolchain.py')], check=True)
    if not (ARTIFACTS / 'toolchain/windows-adb.json').exists():
        if args.offline: raise RuntimeError('Offline build needs the existing Windows ADB tools')
        subprocess.run(['python3', str(ANDROID / 'build-tools/prepare_windows_adb.py')], check=True)
    toolchain = json.loads(toolchain_file.read_text())
    jdk, sdk = Path(toolchain['jdk']), Path(toolchain['android_sdk'])
    environment = os.environ.copy()
    environment.update(JAVA_HOME=str(jdk), ANDROID_HOME=str(sdk), ANDROID_SDK_ROOT=str(sdk),
                       GRADLE_USER_HOME=os.environ.get('WISEMESSAGE_GRADLE_CACHE', str(Path.home() / '.cache/wisemessage-gradle')))
    environment['PATH'] = str(jdk / 'bin') + ':' + str(sdk / 'platform-tools') + ':' + environment['PATH']
    gradle_sha = next(x['sha256'] for x in toolchain['downloads'] if x['file'] == 'gradle-8.13-bin.zip')
    wrapper_sha = ensure_wrapper(gradle_sha, args.offline)
    ensure_signing(jdk, environment, logs)
    (ANDROID / 'local.properties').write_text(f'sdk.dir={sdk}\n')
    run(['python3', ANDROID / 'build-tools/verify_locale_resources.py', '--report', logs / 'localization_audit.json'],
        environment, logs / 'localization-audit.log')
    if args.compile_only:
        command = [Path(toolchain['gradle']) / 'bin/gradle', '--console=plain', '--stacktrace',
                   ':app:compileReleaseJavaWithJavac', ':app:compileDebugAndroidTestJavaWithJavac', ':app:testDebugUnitTest', ':app:lintRelease']
        if args.offline: command.append('--offline')
        run(command, environment, logs / 'java-preflight.log')
        (logs / 'preflight_report.json').write_text(json.dumps({'java_compiled': True, 'unit_tests_requested': True,
                                                              'lint_requested': True, 'apk_created': False}, indent=2) + '\n')
        return
    ndk_file = ARTIFACTS / 'toolchain/ndk.json'
    if not ndk_file.exists():
        if args.offline: raise RuntimeError('Offline build needs the existing native toolchain')
        subprocess.run(['python3', str(ANDROID / 'build-tools/prepare_native_toolchain.py')], check=True)
    ndk = json.loads(ndk_file.read_text())
    environment['WISEMESSAGE_NDK'] = ndk['directory']
    preservation = None
    if args.reuse_native:
        previous_pointer = json.loads((ARTIFACTS / 'latest_build.json').read_text())
        previous_report = json.loads((ROOT / previous_pointer['report']).read_text())
        previous_release = next(item for item in previous_report['apks'] if item['apk'].endswith('-release.apk'))
        native = ANDROID / 'app/src/main/jniLibs/arm64-v8a/libwisemessage_native.so'
        previous_native = next(item for item in previous_release['native_libraries'] if item['path'].endswith(native.name))
        # AGP strips the source ELF before packaging; compare source to its native-link report,
        # then compare the final stripped APK bytes to the previous release below.
        native_link = json.loads((ARTIFACTS / 'native_relink_latest.json').read_text())
        if sha256(native) != native_link['sha256']:
            raise RuntimeError('UI-only update must preserve the verified native runtime')
        for asset in previous_release['assets']:
            local = ANDROID / 'app/src/main' / asset['path']
            if sha256(local) != asset['sha256']:
                raise RuntimeError(f"UI-only update changed an inference asset: {asset['path']}")
        preservation = {'previous_report': previous_pointer['report'], 'certificate_sha256': previous_release['certificate_sha256'],
                        'native_sha256': previous_native['sha256'], 'all_inference_asset_hashes_unchanged': True}
        (logs / 'preserved_runtime.json').write_text(json.dumps(preservation, indent=2) + '\n')
    else:
        run(['python3', ANDROID / 'model-tools/build_android_native.py', '--ndk', ndk['directory']], environment,
            logs / 'native-build.log')
    command = [Path(toolchain['gradle']) / 'bin/gradle', '--console=plain', '--stacktrace',
               ':app:assembleRelease', ':app:assembleDebug', ':app:assembleDebugAndroidTest']
    if args.offline: command.append('--offline')
    if not args.skip_tests:
        command.append(':app:testDebugUnitTest')
    if not args.skip_lint:
        command.append(':app:lintRelease')
    run(command, environment, logs / 'gradle-build.log')
    apks = []
    for variant in ('release', 'debug'):
        original = ANDROID / f'app/build/outputs/apk/{variant}/app-{variant}.apk'
        destination = logs / f'WiseMessage-{version}-arm64-{variant}.apk'
        shutil.copyfile(original, destination)
        apks.append(inspect_apk(destination, environment, sdk, logs))
    release = next(item for item in apks if item['apk'].endswith('-release.apk'))
    if preservation and release['certificate_sha256'] != preservation['certificate_sha256']:
        raise RuntimeError('Update certificate differs from the previous release; do not install over the existing app')
    if preservation and release['native_libraries'][0]['sha256'] != preservation['native_sha256']:
        raise RuntimeError('UI-only update changed the packaged inference runtime')
    test_apk = ANDROID / 'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk'
    test_destination = logs / f'WiseMessage-{version}-instrumentation.apk'
    shutil.copyfile(test_apk, test_destination)
    run([sdk / 'build-tools/36.0.0/apksigner', 'verify', '--verbose', '--print-certs', test_destination],
        environment, logs / 'instrumentation-signature.log')
    run([sdk / 'build-tools/36.0.0/zipalign', '-c', '4', test_destination],
        environment, logs / 'instrumentation-zipalign.log')
    test_results = []
    test_log_dir = logs / 'unit-tests'
    test_log_dir.mkdir()
    for result_path in (ANDROID / 'app/build/test-results/testDebugUnitTest').glob('*.xml'):
        shutil.copyfile(result_path, test_log_dir / result_path.name)
        suite = ET.parse(result_path).getroot()
        test_results.append({key: suite.attrib.get(key) for key in ('name', 'tests', 'failures', 'errors', 'skipped', 'time')})
    lint_path = ANDROID / 'app/build/reports/lint-results-release.xml'
    lint_issues = []
    if lint_path.exists():
        shutil.copyfile(lint_path, logs / lint_path.name)
        lint_issues = [{'id': issue.attrib.get('id'), 'severity': issue.attrib.get('severity')}
                       for issue in ET.parse(lint_path).getroot().findall('issue')]
    adb = run([sdk / 'platform-tools/adb', 'devices', '-l'], environment, logs / 'adb-devices.log', check=False)
    windows_adb_path = ARTIFACTS / 'toolchain/windows-platform-tools/platform-tools/adb.exe'
    windows_adb = run([windows_adb_path, 'devices', '-l'], environment, logs / 'windows-adb-devices.log', check=False)
    report = {'created_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'toolchain': toolchain, 'ndk': ndk,
              'wrapper_jar_sha256': wrapper_sha, 'package': 'hk.wisemessage.app', 'target_sdk': 36,
              'version_name': version, 'version_code': version_code, 'offline_build': args.offline,
              'runtime_preservation': preservation,
              'min_sdk': 26, 'abi': 'arm64-v8a', 'signing_purpose': 'Local device testing only; not a production release identity',
              'unit_tests_requested': not args.skip_tests, 'lint_requested': not args.skip_lint,
              'unit_tests': test_results, 'lint_issues': lint_issues,
              'instrumentation_apk': {'path': str(test_destination.relative_to(ROOT)), 'sha256': sha256(test_destination),
                                      'bytes': test_destination.stat().st_size, 'signature_verified': True,
                                      'zipalign_passed': True, 'executed_on_device': False},
              'apks': apks, 'adb_devices': adb.stdout.splitlines(), 'device_installed': False,
              'windows_adb_devices': windows_adb.stdout.splitlines(),
              'hardware_tested': False}
    (logs / 'build_report.json').write_text(json.dumps(report, indent=2) + '\n')
    release = next(item for item in apks if item['apk'].endswith('-release.apk'))
    published_apk = ARTIFACTS / f'WiseMessage-{version}-arm64.apk'
    shutil.copyfile(ROOT / release['apk'], published_apk)
    report['distribution_apk'] = {'path': str(published_apk.relative_to(ROOT)), 'sha256': sha256(published_apk),
                                  'bytes': published_apk.stat().st_size}
    (logs / 'build_report.json').write_text(json.dumps(report, indent=2) + '\n')
    (ARTIFACTS / 'latest_build.json').write_text(json.dumps({'report': str((logs / 'build_report.json').relative_to(ROOT))}, indent=2) + '\n')
    print(json.dumps({'build_report': str(logs / 'build_report.json'), 'apks': [x['apk'] for x in apks]}, indent=2))

if __name__ == '__main__':
    main()
