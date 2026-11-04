"""Native Android UI validation, using the preserved dedicated fictional-SMS AVD.

Run after installing the signed 3.2 APK. No app data clearing, stored-record deletion,
permissions changes, inbox imports, incoming SMS injection, or model benchmark.
"""
from datetime import datetime, timezone
import argparse
import base64
import json
from pathlib import Path
import re
import subprocess
import time
import traceback
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONFIG = json.loads((ROOT / 'windows-app/emulator-settings.json').read_text(encoding='utf-8-sig'))
ADB = ['wsl.exe', '-d', CONFIG['distribution'], '--exec', CONFIG['adb'], '-s', CONFIG['serial']]
PACKAGE = 'hk.wisemessage.app'
CARDS = ['scan_all_button', 'read_sms_button', 'manual_nav_button', 'statistics_button']
ROWS = ['checked', 'normal', 'spam', 'scam', 'review', 'pending', 'failed']
LANGUAGES = {'en': 'English', 'zh-Hant': '繁體中文', 'zh-Hans': '简体中文'}
FIXTURES = [
    {'id': 'traditional', 'text': '[WiseMessage UI 3.2 fictional test] 明天下午三點有牙科預約，請攜帶身分證。', 'language': 'en'},
    {'id': 'simplified', 'text': '[WiseMessage UI 3.2 fictional test] 您的账户异常，请立即登录 https://secure-bank.example.invalid 核实资料，否则冻结账户。', 'language': 'zh-Hans'},
]
EVIDENCE = HERE / ('run-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))


def call(*args):
    return subprocess.run(ADB + list(args), check=True, capture_output=True).stdout


def shell(*args):
    return call('shell', *args).decode('utf-8', errors='replace').strip()


def restore_font(value):
    if value == 'null':
        # Restore an originally absent preference. This only removes our temporary
        # font-scale override; it never removes a file, app record, or SMS.
        shell('settings', 'delete', 'system', 'font_scale')
    else:
        shell('settings', 'put', 'system', 'font_scale', value)


def dump(name=None):
    call('shell', 'uiautomator', 'dump', '/sdcard/wisemessage-ui-v32.xml')
    data = call('exec-out', 'cat', '/sdcard/wisemessage-ui-v32.xml')
    root = ET.fromstring(data)
    if name:
        (EVIDENCE / (name + '.xml')).write_bytes(data)
    return root


def nodes(root):
    return list(root.iter('node'))


def find(root, suffix):
    return next((n for n in nodes(root) if n.get('resource-id', '').endswith('/' + suffix)), None)


def bounds(node):
    return list(map(int, re.findall(r'\d+', node.get('bounds', ''))))


def text(root):
    return '\n'.join(n.get('text', '') for n in nodes(root) if n.get('text'))


def tap(node):
    left, top, right, bottom = bounds(node)
    call('shell', 'input', 'tap', str((left + right) // 2), str((top + bottom) // 2))
    time.sleep(.25)


def swipe(up=True):
    call('shell', 'input', 'swipe', '540', '1750' if up else '750', '540', '750' if up else '1750', '350')
    time.sleep(.25)


def seek(suffix, attempts=9):
    for _ in range(attempts):
        tree = dump()
        node = find(tree, suffix)
        if node is not None and bounds(node)[3] - bounds(node)[1] > 35:
            return node
        swipe()
    raise AssertionError('Control not reachable through real scrolling: ' + suffix)


def tap_id(suffix, scroll=False):
    node = seek(suffix) if scroll else find(dump(), suffix)
    assert node is not None, 'Missing real visible control ' + suffix
    tap(node)


def capture(name):
    tree = dump(name)
    (EVIDENCE / (name + '.png')).write_bytes(call('exec-out', 'screencap', '-p'))
    return tree


def select_language(choice):
    tap_id('nav_settings')
    tap_id('language_button', scroll=True)
    picker = dump()
    node = next((n for n in nodes(picker) if n.get('text') == choice), None)
    if node is None and choice not in LANGUAGES.values():
        # The first choice is the system language. Its caption changes with the
        # currently selected UI language; explicit language names stay unchanged.
        node = next((n for n in nodes(picker) if n.get('checkable') == 'true'), None)
    assert node is not None, 'Language unavailable: ' + choice
    tap(node)
    time.sleep(.6)


def get_original_language():
    tap_id('nav_settings')
    tap_id('language_button', scroll=True)
    picker = capture('original-language-picker')
    selected = next((n.get('text') for n in nodes(picker) if n.get('checked') == 'true'), None)
    assert selected is not None, 'Cannot preserve original language selection'
    call('shell', 'input', 'keyevent', '4')
    return selected


def collect_page(prefix, max_swipes=10):
    samples = []
    previous = None
    for page in range(max_swipes + 1):
        tree = capture(prefix + '-' + str(page))
        signature = ET.tostring(tree)
        if signature == previous:
            break
        samples.append(tree)
        previous = signature
        swipe()
    return samples


def page_text(samples):
    return '\n'.join(text(tree) for tree in samples)


def validate_home(tag):
    tap_id('nav_home')
    samples = collect_page(tag + '-home', 7)
    all_text = page_text(samples)
    assert 'minirbt' not in all_text.lower(), 'Raw model identifier visible on dashboard'
    assert not any(s in all_text for s in ['Works offline', 'No SMS uploads', '離線運作', '不會上傳短訊', '离线运行', '不会上传短信']), 'Explanatory badges remain on home'
    measured = {}
    for suffix in CARDS:
        candidates = []
        for tree in samples:
            node = find(tree, suffix)
            if node is not None:
                left, top, right, bottom = bounds(node)
                # Only use a full card, separated from both scroll edges. A clipped
                # Accessibility rectangle must not be mistaken for the view size.
                scroll = next(n for n in nodes(tree) if n.get('class') == 'android.widget.ScrollView')
                _, scroll_top, _, scroll_bottom = bounds(scroll)
                if top > scroll_top and bottom < scroll_bottom:
                    candidates.append({'bounds': [left, top, right, bottom], 'size': [right-left, bottom-top]})
        assert candidates, 'No full visible geometry for dashboard action ' + suffix
        measured[suffix] = max(candidates, key=lambda row: row['size'][1])
    assert len({tuple(row['size']) for row in measured.values()}) == 1, 'Dashboard action sizes differ: ' + repr(measured)
    return {'equal_card_sizes': True, 'cards': measured, 'home_explanations_removed': True, 'raw_model_id_absent': True}


def validate_settings(tag):
    tap_id('nav_settings')
    samples = collect_page(tag + '-settings', 9)
    found = [find(tree, 'settings_explanations') for tree in samples]
    explanation = '\n'.join(text(node) for node in found if node is not None)
    assert explanation.strip(), 'The Settings explanations are missing'
    assert 'minirbt' not in page_text(samples).lower(), 'Technical model identifier shown in Settings'
    return {'explanations_present_in_settings': True, 'explanation_text': explanation}


def validate_statistics(tag):
    tap_id('nav_statistics')
    samples = collect_page(tag + '-statistics', 9)
    table = {}
    headers = []
    for tree in samples:
        header = find(tree, 'stats_table_header')
        if header is not None:
            cells = [n for n in list(header) if n.get('class') == 'android.widget.TextView']
            if len(cells) == 3:
                headers = [n.get('text') for n in cells]
        for key in ROWS:
            node = find(tree, 'stats_' + key + '_row')
            if node is None:
                continue
            cells = [n for n in list(node) if n.get('class') == 'android.widget.TextView']
            if len(cells) != 3:
                continue
            row_bounds = bounds(node)
            if row_bounds[3] - row_bounds[1] < 70:
                continue
            cells_data = [{'text': n.get('text', ''), 'bounds': bounds(n)} for n in cells]
            previous = table.get(key)
            if previous is None or row_bounds[3]-row_bounds[1] > previous['height']:
                table[key] = {'cells': cells_data, 'height': row_bounds[3]-row_bounds[1]}
    assert len(headers) == 3 and all(headers), 'Readable three-column statistics header missing'
    assert set(table) == set(ROWS), 'Not all seven actual statistics categories were reachable: ' + repr(table.keys())
    columns = [set(), set()]
    for key, row in table.items():
        label, today, lifetime = row['cells']
        assert label['text'], 'Empty statistic category: ' + key
        today_valid = bool(re.fullmatch(r'[\d,]+', today['text'])) or (key in ['pending', 'failed'] and today['text'] == '—')
        assert today_valid and re.fullmatch(r'[\d,]+', lifetime['text']), 'Non-numeric or truncated count: ' + key
        assert label['bounds'][2] <= today['bounds'][0] and today['bounds'][2] <= lifetime['bounds'][0], 'Label/count columns overlap: ' + key
        assert all(c['bounds'][2] > c['bounds'][0] for c in row['cells']), 'Count column is outside the visible table: ' + key
        columns[0].add(tuple(today['bounds'][::2]))
        columns[1].add(tuple(lifetime['bounds'][::2]))
    assert all(len(c) == 1 for c in columns), 'Numeric statistics columns do not align across rows'
    weekly = any(find(tree, 'stats_week_header') is not None for tree in samples)
    assert weekly, 'Weekly table header missing'
    return {'three_readable_headers': headers, 'seven_rows_numeric_and_nonoverlapping': True, 'counts_columns_aligned': True, 'weekly_table_present': weekly, 'rows': table}


def set_fixture_text(message):
    encoded = base64.b64encode(message.encode('utf-8')).decode('ascii')
    process = subprocess.run(ADB + ['shell', 'uiautomator', 'runtest', '/data/local/tmp/wisemessage-unicode-ui-fixture.jar',
                             '/system/framework/android.test.base.jar', '-c', 'hk.wisemessage.qa.UnicodeUiFixture',
                             '-e', 'message_b64', encoded], capture_output=True)
    output = process.stdout.decode('utf-8', errors='replace') + process.stderr.decode('utf-8', errors='replace')
    assert 'WISEMESSAGE_UNICODE_FIXTURE_EXACT=true' in output and 'FAILURES' not in output, output
    return output


def validate_manual(fixture):
    select_language(LANGUAGES[fixture['language']])
    tap_id('nav_home')
    tap_id('manual_nav_button', scroll=True)
    output = set_fixture_text(fixture['text'])
    (EVIDENCE / (fixture['id'] + '-fixture-driver.txt')).write_text(output, encoding='utf-8')
    input_tree = capture(fixture['id'] + '-manual-input')
    assert find(input_tree, 'manual_input').get('text') == fixture['text'], 'Chinese manual text was corrupted'
    tap_id('classify_button', scroll=True)
    deadline = time.monotonic() + 80
    while time.monotonic() < deadline:
        tree = dump()
        node = find(tree, 'result_text')
        result = node.get('text', '') if node is not None else ''
        if '%' in result:
            break
        time.sleep(.5)
    else:
        raise AssertionError('Real manual Chinese inference did not return probabilities/time')
    samples = collect_page(fixture['id'] + '-manual-result', 4)
    actual = page_text(samples)
    assert 'minirbt' not in actual.lower(), 'Raw minirbt identifier remains on the actual manual result'
    assert fixture['text'] in actual, 'Input changed after inference'
    return {'exact_input': fixture['text'], 'actual_result_text': result, 'unicode_exact': True, 'real_ui_inference': True, 'raw_model_id_absent': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe-fixture', action='store_true', help='Only populate a fictional draft on the installed app, without running inference')
    args = parser.parse_args()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    avd = call('emu', 'avd', 'name').decode()
    assert CONFIG['avd'] in avd and CONFIG['dedicated_windows_demo'], 'Wrong AVD; refusing access'
    call('shell', 'am', 'start', '-n', PACKAGE + '/.MainActivity')
    if args.probe_fixture:
        tap_id('nav_home')
        tap_id('manual_nav_button', scroll=True)
        print(set_fixture_text(FIXTURES[0]['text']))
        capture('fixture-probe')
        tap_id('nav_home')
        return
    package = shell('dumpsys', 'package', PACKAGE)
    assert 'versionName=3.2.0-test' in package and 'versionCode=5 ' in package, 'Install the signed 3.2.0-test versionCode 5 upgrade before validation'
    original_font = shell('settings', 'get', 'system', 'font_scale')
    permissions_before = dict(re.findall(r'(android\.permission\.(?:RECEIVE_SMS|READ_SMS|POST_NOTIFICATIONS)): granted=(true|false)', package))
    original_language = None
    tap_id('nav_home')
    before = capture('before-home')
    original_protection = find(before, 'protection_title').get('text')
    report = {'passed': False, 'started_at_utc': datetime.now(timezone.utc).isoformat(), 'runtime': {'avd': CONFIG['avd'], 'serial': CONFIG['serial'], 'api': shell('getprop', 'ro.build.version.sdk'), 'abis': shell('getprop', 'ro.product.cpu.abilist'), 'native_bridge': shell('getprop', 'ro.dalvik.vm.native.bridge'), 'physical_device': False}, 'cases': {}, 'manual_fixtures': [], 'files_deleted': 0, 'stored_records_deleted': 0, 'permissions_changed': False, 'incoming_sms_sent': 0, 'limitations': ['No Samsung physical device is connected; OEM/carrier/battery behavior was not tested.', 'Counts are real existing plus two preserved fictional manual checks; high-volume four-digit counts were not seeded.', 'Geometry and native screenshots cover API 30 ARM64 translation on the dedicated 1080x2400 emulator.']}
    try:
        original_language = get_original_language()
        (EVIDENCE / 'original-settings.json').write_text(json.dumps({'font_scale': original_font, 'language': original_language, 'protection': original_protection, 'permissions': permissions_before}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        for scale in [1.0, 1.3]:
            shell('settings', 'put', 'system', 'font_scale', str(scale))
            time.sleep(.7)
            for language, label in LANGUAGES.items():
                select_language(label)
                tag = language + '-font-' + str(scale)
                report['cases'][tag] = {'dashboard': validate_home(tag), 'settings': validate_settings(tag), 'statistics': validate_statistics(tag)}
                (EVIDENCE / 'progress.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                print('PASS', tag, flush=True)
        shell('settings', 'put', 'system', 'font_scale', '1.0')
        time.sleep(.6)
        for fixture in FIXTURES:
            report['manual_fixtures'].append(validate_manual(fixture))
            print('PASS manual', fixture['id'], flush=True)
        after_stats = validate_statistics('after-two-fictional-manual-checks')
        before_total = int(report['cases']['en-font-1.0']['statistics']['rows']['checked']['cells'][2]['text'].replace(',', ''))
        after_total = int(after_stats['rows']['checked']['cells'][2]['text'].replace(',', ''))
        assert after_total == before_total + len(FIXTURES), 'Two real manual button checks must add exactly two preserved rows'
        report['after_manual_statistics'] = after_stats
        report['preserved_record_count_before_manual'] = before_total
        report['preserved_record_count_after_manual'] = after_total
        report['passed'] = True
    except Exception:
        report['failure'] = traceback.format_exc()
        try:
            capture('failure-screen')
        except Exception:
            pass
        raise
    finally:
        restore_font(original_font)
        time.sleep(.7)
        if original_language:
            select_language(original_language)
        tap_id('nav_home')
        restored = capture('restored-home')
        report['restored_font_scale'] = shell('settings', 'get', 'system', 'font_scale')
        report['original_font_scale'] = original_font
        report['restored_original_language'] = original_language
        report['protection_unchanged'] = find(restored, 'protection_title').get('text') == original_protection
        permissions_after = dict(re.findall(r'(android\.permission\.(?:RECEIVE_SMS|READ_SMS|POST_NOTIFICATIONS)): granted=(true|false)', shell('dumpsys', 'package', PACKAGE)))
        report['runtime_permissions_preserved'] = permissions_before == permissions_after
        report['runtime_permissions'] = permissions_after
        report['passed'] = report['passed'] and report['protection_unchanged'] and report['runtime_permissions_preserved'] and report['restored_font_scale'] == original_font
        report['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
        report['evidence_directory'] = str(EVIDENCE.relative_to(ROOT))
        (EVIDENCE / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (HERE / 'latest-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'passed': report['passed'], 'report': str(EVIDENCE / 'report.json')}, ensure_ascii=True), flush=True)


if __name__ == '__main__':
    main()
