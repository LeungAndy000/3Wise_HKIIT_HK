"""Build the small shell UI fixture with cached local SDK tools; no app rebuild."""
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONFIG = json.loads((ROOT / 'windows-app/emulator-settings.json').read_text(encoding='utf-8-sig'))
WSL = ['wsl.exe', '-d', CONFIG['distribution'], '--exec']
SDK = CONFIG['sdk']
JDK = '/home/victor/.local/share/wisemessage-android/jdk-17.0.16+8'


def run(*args):
    process = subprocess.run(WSL + list(args), check=True, capture_output=True)
    return process.stdout.decode('utf-8', errors='replace').strip()


def main():
    linux = run('/usr/bin/wslpath', '-a', '-u', str(HERE))
    (HERE / 'fixture-classes').mkdir(exist_ok=True)
    (HERE / 'fixture-dex').mkdir(exist_ok=True)
    classpath = ':'.join([SDK + '/platforms/android-36/android.jar', SDK + '/platforms/android-36/uiautomator.jar',
                          SDK + '/platforms/android-36/optional/android.test.base.jar'])
    run(JDK + '/bin/javac', '-encoding', 'UTF-8', '-source', '8', '-target', '8', '-cp', classpath,
        '-d', linux + '/fixture-classes', linux + '/UnicodeUiFixture.java')
    run('/usr/bin/env', 'JAVA_HOME=' + JDK, 'PATH=' + JDK + '/bin:/usr/bin:/bin', SDK + '/build-tools/36.0.0/d8', '--min-api', '26',
        '--lib', SDK + '/platforms/android-36/android.jar', '--output', linux + '/fixture-dex',
        linux + '/fixture-classes/hk/wisemessage/qa/UnicodeUiFixture.class')
    run(JDK + '/bin/jar', 'cf', linux + '/unicode-ui-fixture.jar', '-C', linux + '/fixture-dex', 'classes.dex')
    adb = WSL + [CONFIG['adb'], '-s', CONFIG['serial']]
    result = subprocess.run(adb + ['push', linux + '/unicode-ui-fixture.jar', '/data/local/tmp/wisemessage-unicode-ui-fixture.jar'],
                            check=True, capture_output=True)
    print(result.stdout.decode(errors='replace').strip())


if __name__ == '__main__':
    main()
