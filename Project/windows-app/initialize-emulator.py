"""Create the dedicated Windows demo AVD once, using the existing cached image."""
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
CONFIG=ROOT/'emulator-settings.json'
config=json.loads(CONFIG.read_text(encoding='utf-8-sig'))
name='wisemessage_windows_20261024'
avd='/home/victor/.local/share/wisemessage-android/avd-windows-20261024'
wsl=['wsl.exe','-d',config['distribution'],'--exec']
exists=subprocess.run(wsl+['/usr/bin/test','-f',avd+'/config.ini']).returncode==0
if not exists:
    jdk='/home/victor/.local/share/wisemessage-android/jdk-17.0.16+8'
    command=wsl+['/usr/bin/env','JAVA_HOME='+jdk,'PATH='+jdk+'/bin:/usr/local/bin:/usr/bin:/bin','ANDROID_SDK_ROOT='+config['sdk'],config['sdk']+'/cmdline-tools/19.0/bin/avdmanager','create','avd','-n',name,'-p',avd,'-k','system-images;android-30;google_apis;x86_64','-d','pixel_4']
    subprocess.run(command,input=b'no\n',check=True)
    # The source is passed as argv, never a shell.
    source="from pathlib import Path\np=Path("+repr(avd+'/config.ini')+")\np.write_text(p.read_text()+"+repr('\nhw.lcd.width=1080\nhw.lcd.height=2400\nhw.lcd.density=440\nhw.ramSize=4096\nshowDeviceFrame=no\n')+")\n"
    subprocess.run(wsl+['/usr/bin/python3','-c',source],check=True)
diagnostics=ROOT/'diagnostics';diagnostics.mkdir(exist_ok=True)
prior=diagnostics/'prior-native-capture-avd-settings.json'
if not prior.exists():prior.write_bytes(CONFIG.read_bytes())
config.update({'avd':name,'avd_path':avd,'serial':'emulator-5582','port':5582,'dedicated_windows_demo':True})
CONFIG.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'avd':name,'created':not exists,'old_avd_preserved':True,'system_image_downloaded':False}))
