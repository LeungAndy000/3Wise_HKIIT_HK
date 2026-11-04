"""Recover completed evidence after restoring an originally unset font preference."""
import json
import re
import time
import validate_ui as ui


def main():
    directory = ui.HERE / 'run-20261025T083909Z'
    ui.EVIDENCE = directory
    report = json.loads((directory / 'progress.json').read_text(encoding='utf-8'))
    assert len(report['cases']) == 6, 'All six matrix cases must have completed'
    for fixture in ui.FIXTURES:
        driver = (directory / (fixture['id'] + '-fixture-driver.txt')).read_text(encoding='utf-8')
        assert 'WISEMESSAGE_UNICODE_FIXTURE_EXACT=true' in driver and 'FAILURES' not in driver
        input_tree = ui.ET.fromstring((directory / (fixture['id'] + '-manual-input.xml')).read_bytes())
        assert ui.find(input_tree, 'manual_input').get('text') == fixture['text']
        tree = ui.ET.fromstring((directory / (fixture['id'] + '-manual-result-0.xml')).read_bytes())
        result = ui.find(tree, 'result_text').get('text')
        assert '%' in result and 'minirbt' not in ui.text(tree).lower()
        report['manual_fixtures'].append({'exact_input': fixture['text'], 'actual_result_text': result, 'unicode_exact': True, 'real_ui_inference': True, 'raw_model_id_absent': True, 'evidence_recovered_from_saved_native_xml': True})
    after_rows = {}
    for file in directory.glob('after-two-fictional-manual-checks-statistics-*.xml'):
        tree = ui.ET.fromstring(file.read_bytes())
        for key in ui.ROWS:
            row = ui.find(tree, 'stats_' + key + '_row')
            if row is not None and len(list(row)) == 3:
                cells = [{'text': n.get('text', ''), 'bounds': ui.bounds(n)} for n in list(row)]
                height = ui.bounds(row)[3] - ui.bounds(row)[1]
                if key not in after_rows or height > after_rows[key]['height']:
                    after_rows[key] = {'cells': cells, 'height': height}
    assert set(after_rows) == set(ui.ROWS)
    before = int(report['cases']['en-font-1.0']['statistics']['rows']['checked']['cells'][2]['text'])
    after = int(after_rows['checked']['cells'][2]['text'])
    assert before == 2 and after == 4, 'Preserved baseline plus exactly two fictional manual records expected'
    ui.restore_font('null')
    time.sleep(.7)
    original_picker = ui.ET.fromstring((directory / 'original-language-picker.xml').read_bytes())
    language = next(n.get('text') for n in ui.nodes(original_picker) if n.get('checked') == 'true')
    ui.select_language(language)
    ui.tap_id('nav_home')
    restored = ui.capture('restored-home')
    original = ui.ET.fromstring((directory / 'before-home.xml').read_bytes())
    assert ui.find(restored, 'protection_title').get('text') == ui.find(original, 'protection_title').get('text')
    assert ui.shell('settings', 'get', 'system', 'font_scale') == 'null'
    permissions = dict(re.findall(r'(android\.permission\.(?:RECEIVE_SMS|READ_SMS|POST_NOTIFICATIONS)): granted=(true|false)', ui.shell('dumpsys', 'package', ui.PACKAGE)))
    earlier = json.loads((ui.ROOT / 'windows-app/validation/android-validation-report.json').read_text(encoding='utf-8'))
    assert earlier['checks']['receive_and_read_sms_permissions_granted']
    assert all(permissions['android.permission.' + name] == 'true' for name in ['RECEIVE_SMS', 'READ_SMS'])
    report.update({'passed': True, 'original_font_scale': 'null', 'restored_font_scale': 'null', 'restored_original_language': language, 'protection_unchanged': True, 'runtime_permissions_preserved': True, 'runtime_permissions': permissions, 'runtime_permissions_baseline_source': 'windows-app/validation/android-validation-report.json', 'preserved_record_count_before_manual': before, 'preserved_record_count_after_manual': after, 'after_manual_statistics': {'rows': after_rows}, 'evidence_directory': str(directory.relative_to(ui.ROOT)), 'completed_at_utc': ui.datetime.now(ui.timezone.utc).isoformat(), 'harness_recovery': 'All six UI cases and both manual checks completed. Initial finalizer tried settings put font_scale null; Android rejected the unset value. Corrected helper removes only the temporary font-scale override with settings delete system font_scale, restores original English selection, confirms protection and SMS permissions unchanged, and reconstructs manual/count evidence from saved native XML without repeating any inference.'})
    (directory / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ui.HERE / 'latest-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': True, 'records': after, 'font_scale': 'null', 'language': language}, ensure_ascii=True))


if __name__ == '__main__':
    main()
