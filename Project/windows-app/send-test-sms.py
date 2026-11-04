"""Inject fictional Unicode SMS into the configured project emulator only."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import json
import subprocess

ROOT=Path(__file__).resolve().parent
FIXTURES={
    'normal':('5550301','明天上午十點覆診，請帶同身份證。'),
    'scam':('5550302','我是你朋友，我換電話了。現在急需用錢，請立即轉帳到我的新銀行戶口，不要打電話給我。')
}


def swapped(value):
    if len(value)%2:value+='F'
    return ''.join(value[i+1]+value[i] for i in range(0,len(value),2))


def deliver(sender,text):
    now=datetime.now(timezone(timedelta(hours=8)))
    timestamp=swapped(now.strftime('%y%m%d%H%M%S')+'32')
    data=text.encode('utf-16-be')
    if len(data)>140:raise ValueError('Fixture exceeds one UCS2 SMS')
    return '0004'+f'{len(sender):02X}'+'81'+swapped(sender)+'0008'+timestamp+f'{len(data):02X}'+data.hex().upper()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind',choices=['normal','scam','both'],default='both',nargs='?')
    args=parser.parse_args()
    config=json.loads((ROOT/'emulator-settings.json').read_text(encoding='utf-8-sig'))
    adb=['wsl.exe','-d',config['distribution'],'--exec',config['adb'],'-s',config['serial']]
    name=subprocess.run(adb+['emu','avd','name'],check=True,capture_output=True,text=True).stdout.splitlines()
    if config['avd'] not in name:raise RuntimeError('Refusing a different emulator or physical phone')
    selected=FIXTURES.items() if args.kind=='both' else [(args.kind,FIXTURES[args.kind])]
    records=[]
    for kind,(sender,text) in selected:
        assert '?' not in text and all(ord(c)>127 for c in text)
        pdu=deliver(sender,text)
        result=subprocess.run(adb+['emu','sms','pdu',pdu],check=True,capture_output=True,text=True)
        if 'OK' not in result.stdout:raise RuntimeError('Emulator did not accept the PDU')
        records.append({'kind':kind,'sender':sender,'text':text,'pdu':pdu,'emulator_response':result.stdout.strip()})
    out=ROOT/'validation';out.mkdir(exist_ok=True)
    (out/'unicode-sms-fixtures.json').write_text(json.dumps({'fixtures':records,'transport':'UCS2 SMS-DELIVER PDU, encoded in a UTF-8 source file to avoid PowerShell ASCII pipeline substitution','fictional':True,'personal_phone_accessed':False},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'injected':len(records),'senders':[r['sender'] for r in records],'original_unicode_text_verified_before_injection':True}))


if __name__=='__main__':main()
