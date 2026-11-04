#!/usr/bin/env python3
"""Install the pinned SDK CMake package using the isolated Java/SDK."""
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]

def main():
    toolchain = json.loads((ROOT / 'artifacts/android/toolchain/toolchain.json').read_text())
    sdk, jdk = Path(toolchain['android_sdk']), Path(toolchain['jdk'])
    environment = os.environ.copy()
    environment.update(JAVA_HOME=str(jdk), ANDROID_HOME=str(sdk), ANDROID_SDK_ROOT=str(sdk))
    environment['PATH'] = str(jdk / 'bin') + ':' + environment['PATH']
    result = subprocess.run([str(sdk / 'cmdline-tools/19.0/bin/sdkmanager'), '--sdk_root=' + str(sdk), 'cmake;3.22.1'],
                            env=environment, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (ROOT / 'artifacts/android/toolchain/cmake-installation.log').write_text(result.stdout)
    if result.returncode:
        raise RuntimeError(result.stdout[-3000:])
    print(sdk / 'cmake/3.22.1/bin/cmake')

if __name__ == '__main__':
    main()
