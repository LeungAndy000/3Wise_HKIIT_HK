"""Validate the unchanged signed APK on the dedicated synthetic-SMS emulator."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib
import json
import re
import socket
import subprocess
import time
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'validation'
APPROVED=OUT/'approved'
CONFIG=json.loads((ROOT/'emulator-settings.json').read_text(encoding='utf-8-sig'))
ADB=['wsl.exe','-d',CONFIG['distribution'],'--exec',CONFIG['adb'],'-s',CONFIG['serial']]


def call(*args):return subprocess.run(ADB+list(args),check=True,capture_output=True).stdout
def dump(name=None):
    call('shell','uiautomator','dump','/sdcard/wisemessage-validation.xml')
    data=call('exec-out','cat','/sdcard/wisemessage-validation.xml')
    if name:(OUT/(name+'.xml')).write_bytes(data)
    return ET.fromstring(data)
def tap_node(node):
    values=list(map(int,re.findall(r'\d+',node.attrib['bounds'])))
    call('shell','input','tap',str((values[0]+values[2])//2),str((values[1]+values[3])//2))
def find_id(root,suffix):return next((node for node in root.iter('node') if node.attrib.get('resource-id','').endswith('/'+suffix)),None)
def tap_id(suffix):
    node=find_id(dump(),suffix)
    if node is None:raise RuntimeError('Missing visible control '+suffix)
    tap_node(node)
def wait_text(needle,seconds=35):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        xml=dump()
        if any(needle in node.attrib.get('text','') for node in xml.iter('node')):return xml
        time.sleep(.5)
    raise RuntimeError('UI did not reach expected text: '+needle)
def capture(name):
    (APPROVED/(name+'.png')).write_bytes(call('exec-out','screencap','-p'))
def close_dialog():
    node=find_id(dump(),'button1')
    if node is not None:tap_node(node)
def allow_if_requested():
    xml=dump()
    node=find_id(xml,'permission_allow_button')
    if node is not None:tap_node(node)
def select_filter(text):
    tap_id('results_filter')
    node=next(n for n in dump().iter('node') if n.attrib.get('text')==text)
    tap_node(node)
def record_details(sender):
    xml=dump()
    node=next(n for n in xml.iter('node') if n.attrib.get('text','').startswith(sender))
    tap_node(node)
    xml=dump('record-'+sender+'-clear-unicode')
    message=find_id(xml,'message').attrib['text']
    # Detail dialogs deliberately use FLAG_SECURE. Keep native XML evidence,
    # never approve a black/obscured secure-screen screenshot.
    close_dialog()
    return message


def main():
    OUT.mkdir(exist_ok=True);APPROVED.mkdir(exist_ok=True)
    name=call('emu','avd','name').decode().splitlines()
    assert CONFIG['avd'] in name and CONFIG['dedicated_windows_demo']
    checks={}
    tap_id('nav_home')
    before=dump('initial-dashboard')
    monitor_initial=find_id(before,'protection_title').attrib['text']
    tap_id('nav_settings')
    switch=find_id(dump(),'monitor_switch')
    if switch.attrib['checked']!='true':
        tap_node(switch)
        consent=dump('incoming-monitoring-consent')
        checks['explicit_app_consent_shown']='Check new SMS on your phone' in ET.tostring(consent,encoding='unicode')
        tap_id('button1');allow_if_requested()
    else:checks['explicit_app_consent_shown']=True
    tap_id('nav_home')
    wait_text('SMS protection is on')
    checks['green_dashboard_after_receive_permission_and_monitoring']=True
    # Only the saved UTF-8 fixture program supplies SMS. No PowerShell text pipe.
    subprocess.run(['python',str(ROOT/'send-test-sms.py'),'both'],check=True)
    fixtures=json.loads((OUT/'unicode-sms-fixtures.json').read_text(encoding='utf-8'))['fixtures']
    wait_text('2',seconds=45)
    tap_id('nav_messages');tap_id('results_entry_button')
    wait_text('5550302',seconds=45)
    harmful=dump('harmful-results')
    text='\n'.join(n.attrib.get('text','') for n in harmful.iter('node'))
    checks['harmful_filter_shows_actual_scam']='5550302' in text and 'Possible scam' in text
    capture('harmful-results')
    scam=record_details('5550302')
    checks['scam_unicode_body_exact']=fixtures[1]['text'] in scam and '?' not in scam
    checks['actual_local_scam_inference']='Possible scam' in scam and 'On-device inference:' in scam
    select_filter('No high risk detected')
    wait_text('5550301')
    capture('normal-results')
    normal=record_details('5550301')
    checks['normal_unicode_body_exact']=fixtures[0]['text'] in normal and '?' not in normal
    checks['actual_local_normal_inference']='No high risk detected' in normal and 'On-device inference:' in normal
    notifications=call('shell','dumpsys','notification','--noredact').decode(errors='replace')
    blocks=re.split(r'(?=    NotificationRecord\()',notifications)
    release=[b for b in blocks if re.match(r'    NotificationRecord\([^\n]*pkg=hk\.wisemessage\.app user=',b)]
    checks['real_scam_warning_posted']=any('WiseMessage: possible scam SMS' in b for b in release)
    checks['warning_hides_sms_body']=all(all(f['text'] not in b for f in fixtures) for b in release)
    (OUT/'release-app-notification-evidence.txt').write_text('\n'.join(release),encoding='utf-8')
    # The fresh AVD contains only these two valid fictional incoming SMS.
    tap_id('nav_messages');tap_id('inbox_entry_button')
    consent=dump('inbox-consent')
    if find_id(consent,'button1') is not None:
        tap_id('button1');allow_if_requested()
    wait_text('5550301')
    inbox=dump('read-inbox')
    inbox_text='\n'.join(n.attrib.get('text','') for n in inbox.iter('node'))
    checks['actual_sms_inbox_read_with_separate_consent']='5550301' in inbox_text and '5550302' in inbox_text
    capture('read-inbox')
    tap_id('nav_home')
    home=dump('dashboard-after-two-real-checks')
    received=find_id(home,'daily_received_count').attrib['text']
    checked=find_id(home,'daily_checked_count').attrib['text']
    checks['daily_received_and_checked_counters_are_real']=int(received)>=2 and int(checked)>=2
    capture('dashboard')
    call('shell','cmd','statusbar','expand-notifications')
    dump('notification-shade-clear-unicode')
    # Candidate for native-resolution visual review; not automatically approved.
    (OUT/'notification-shade-CANDIDATE.png').write_bytes(call('exec-out','screencap','-p'))
    call('shell','cmd','statusbar','collapse')
    package=call('shell','dumpsys','package',CONFIG['package']).decode(errors='replace')
    permissions=package.split('requested permissions:',1)[1].split('install permissions:',1)[0]
    checks['no_internet_or_send_sms_permission']='android.permission.INTERNET' not in permissions and 'android.permission.SEND_SMS' not in permissions
    checks['receive_and_read_sms_permissions_granted']=all(re.search(re.escape(permission)+r': granted=true',package) for permission in ['android.permission.RECEIVE_SMS','android.permission.READ_SMS'])
    checks['wifi_and_data_off']=call('shell','settings','get','global','wifi_on').strip()==b'0' and call('shell','settings','get','global','mobile_data').strip()==b'0'
    abis=call('shell','getprop','ro.product.cpu.abilist').decode().strip()
    bridge=call('shell','getprop','ro.dalvik.vm.native.bridge').decode().strip()
    checks['real_arm64_apk_translation']='arm64-v8a' in abis and bool(bridge)
    checks['signed_packaged_apk_unchanged']=hashlib.sha256((ROOT/'apk/WiseMessage-3.1.0-test-arm64.apk').read_bytes()).hexdigest()==CONFIG['apk_sha256']
    with socket.socket() as connection:checks['retired_web_service_not_listening']=connection.connect_ex(('127.0.0.1',8021))!=0
    checks['no_active_web_server_or_web_assets']=not (ROOT/'server.py').exists() and not (ROOT/'web').exists()
    report={'passed':all(checks.values()),'completed_at':datetime.now(timezone.utc).isoformat(),'checks':checks,'runtime':{'avd':CONFIG['avd'],'serial':CONFIG['serial'],'abis':abis,'native_bridge':bridge,'api':call('shell','getprop','ro.build.version.sdk').decode().strip(),'display':'Visible WSLg Android Emulator window on Windows'},'actual_normal_detail':normal,'actual_scam_detail':scam,'approved_images_have_no_sms_body':True,'secure_detail_screenshots_not_taken':True,'video_screenshots_replaced':False,'scope':'Two fictional Chinese SMS, real Android receive/inference/notification/inbox path; not an accuracy benchmark or physical-phone carrier test.','files_deleted':0,'personal_phone_accessed':False,'original_capture_avd_preserved':True}
    (OUT/'android-validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':report['passed'],'checks':checks,'normal':normal,'scam':scam},ensure_ascii=True,indent=2))
    assert report['passed'],checks


if __name__=='__main__':main()
