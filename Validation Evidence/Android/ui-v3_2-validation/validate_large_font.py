"""Focused 150% font check of the actual one-column dashboard layout."""
from datetime import datetime, timezone
import json
import time
import traceback
import validate_ui as ui


def main():
    ui.EVIDENCE = ui.HERE / ('large-font-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    ui.EVIDENCE.mkdir(exist_ok=True)
    assert ui.CONFIG['avd'] in ui.call('emu', 'avd', 'name').decode(), 'Wrong AVD'
    assert 'versionName=3.2.0-test' in ui.shell('dumpsys', 'package', ui.PACKAGE), 'Expected signed 3.2 UI'
    before_font = ui.shell('settings', 'get', 'system', 'font_scale')
    ui.tap_id('nav_home')
    before_protection = ui.find(ui.dump(), 'protection_title').get('text')
    matrix = json.loads((ui.HERE / 'latest-report.json').read_text(encoding='utf-8'))
    before_language = matrix['restored_original_language']
    assert before_protection == 'SMS protection is on', 'Run after the restored matrix in its original English UI'
    report = {'passed': False, 'font_scale': 1.5, 'language': 'en', 'scope': 'Actual one-column adaptive dashboard branch; no model checks or record writes.', 'files_deleted': 0, 'records_added': 0}
    try:
        ui.shell('settings', 'put', 'system', 'font_scale', '1.5')
        time.sleep(.7)
        report['dashboard'] = ui.validate_home('en-font-1.5')
        left_edges = {entry['bounds'][0] for entry in report['dashboard']['cards'].values()}
        assert len(left_edges) == 1, '150% font did not switch all four cards to a single column'
        for suffix, measured in report['dashboard']['cards'].items():
            verified = False
            for file in ui.EVIDENCE.glob('en-font-1.5-home-*.xml'):
                tree = ui.ET.fromstring(file.read_bytes())
                card = ui.find(tree, suffix)
                if card is None or ui.bounds(card) != measured['bounds']:
                    continue
                left, top, right, bottom = ui.bounds(card)
                labels = [n for n in ui.nodes(card) if n.get('class') == 'android.widget.TextView' and n.get('text')]
                assert len(labels) == 2, 'Missing full title/description within adaptive action card: ' + suffix
                assert all(left <= ui.bounds(n)[0] < ui.bounds(n)[2] <= right and top <= ui.bounds(n)[1] < ui.bounds(n)[3] <= bottom for n in labels), 'Card text is clipped by its container: ' + suffix
                verified = True
                break
            assert verified, 'Could not inspect full native card content: ' + suffix
        report['single_column_confirmed'] = True
        report['all_titles_and_descriptions_inside_cards'] = True
        report['passed'] = True
    except Exception:
        report['failure'] = traceback.format_exc()
        raise
    finally:
        ui.restore_font(before_font)
        time.sleep(.7)
        ui.tap_id('nav_home')
        restored = ui.capture('restored-home')
        observed_font = ui.shell('settings', 'get', 'system', 'font_scale')
        report['original_font_scale_setting'] = before_font
        report['restored_font_scale_setting'] = observed_font
        report['font_scale_restored'] = observed_font == before_font or (before_font == 'null' and observed_font == '1.0')
        if before_font == 'null' and observed_font == '1.0':
            report['font_scale_storage_note'] = 'Android materialized its default 1.0 setting after the temporary override was removed; the original effective default font size is restored.'
        report['original_language_restored'] = before_language
        report['protection_unchanged'] = ui.find(restored, 'protection_title').get('text') == before_protection
        report['passed'] = report['passed'] and report['font_scale_restored'] and report['protection_unchanged']
        report['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
        report['evidence_directory'] = str(ui.EVIDENCE.relative_to(ui.ROOT))
        (ui.EVIDENCE / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        (ui.HERE / 'large-font-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
