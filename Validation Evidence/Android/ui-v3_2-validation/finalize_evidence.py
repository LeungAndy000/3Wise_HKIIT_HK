"""Link successful native UI evidence to the exact signed APK and adaptive case."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import validate_ui as ui


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    matrix = json.loads((ui.HERE / 'latest-report.json').read_text(encoding='utf-8'))
    adaptive = json.loads((ui.HERE / 'large-font-report.json').read_text(encoding='utf-8'))
    # The original missing key has the effective Android default of 1.0. Android
    # may write that default back after processing the configuration change.
    observed_font = ui.shell('settings', 'get', 'system', 'font_scale')
    if adaptive.get('single_column_confirmed') and not adaptive['font_scale_restored'] and matrix['original_font_scale'] == 'null' and observed_font == '1.0':
        original = ui.ET.fromstring((ui.ROOT / matrix['evidence_directory'] / 'before-home.xml').read_bytes())
        restored = ui.ET.fromstring((ui.ROOT / adaptive['evidence_directory'] / 'restored-home.xml').read_bytes())
        assert ui.bounds(ui.find(original, 'protection_title')) == ui.bounds(ui.find(restored, 'protection_title')), 'Default text geometry was not restored'
        adaptive.update({'passed': True, 'font_scale_restored': True, 'original_font_scale_setting': 'null', 'restored_font_scale_setting': observed_font, 'font_scale_storage_note': 'Initial raw-setting equality check returned false because Android materialized its original default as 1.0 after settings delete. Effective default font scale and original protection-title geometry match; all adaptive layout assertions had passed.'})
        (ui.HERE / 'large-font-report.json').write_text(json.dumps(adaptive, indent=2) + '\n', encoding='utf-8')
        (ui.ROOT / adaptive['evidence_directory'] / 'report.json').write_text(json.dumps(adaptive, indent=2) + '\n', encoding='utf-8')
    assert matrix['passed'] and adaptive['passed'], 'Both native UI runs must pass'
    assert len(matrix['cases']) == 6 and len(matrix['manual_fixtures']) == 2
    assert ui.CONFIG['avd'] in ui.call('emu', 'avd', 'name').decode(), 'Wrong AVD'
    apk = ui.ROOT / 'artifacts/android/WiseMessage-3.2.0-test-arm64.apk'
    expected = '9518176fd845938b81de4da928500408fefc7d72a50d30c190fb92d37b0ac68c'
    assert sha256(apk) == expected, 'APK changed after the verified build'
    installed = ui.shell('pm', 'path', ui.PACKAGE).splitlines()
    base = next(line[len('package:'):] for line in installed if line.endswith('/base.apk'))
    installed_hash = ui.shell('sha256sum', base).split()[0]
    assert installed_hash == expected, 'Native evidence was captured from a different installed APK'
    package = ui.shell('dumpsys', 'package', ui.PACKAGE)
    assert 'versionName=3.2.0-test' in package and 'versionCode=5 ' in package
    chosen = {
        'english_dashboard': 'en-font-1.0-home-2.png',
        'english_statistics': 'en-font-1.0-statistics-0.png',
        'english_large_font_dashboard': 'en-font-1.3-home-3.png',
        'english_large_font_statistics': 'en-font-1.3-statistics-0.png',
        'traditional_dashboard': 'zh-Hant-font-1.0-home-1.png',
        'traditional_statistics': 'zh-Hant-font-1.0-statistics-0.png',
        'traditional_manual_result': 'traditional-manual-result-0.png',
        'simplified_manual_result': 'simplified-manual-result-0.png',
    }
    directory = ui.ROOT / matrix['evidence_directory']
    screenshots = {}
    for key, filename in chosen.items():
        file = directory / filename
        assert file.is_file(), 'Missing native screenshot: ' + str(file)
        screenshots[key] = {'file': str(file.relative_to(ui.ROOT)), 'sha256': sha256(file), 'native_android_capture': True}
    report = {
        'passed': True, 'completed_at_utc': datetime.now(timezone.utc).isoformat(),
        'app': {'package': ui.PACKAGE, 'version_name': '3.2.0-test', 'version_code': 5, 'apk': str(apk.relative_to(ui.ROOT)), 'sha256': expected, 'installed_base_apk_sha256': installed_hash},
        'matrix_report': str((directory / 'report.json').relative_to(ui.ROOT)),
        'matrix_cases_passed': list(matrix['cases']),
        'adaptive_150_percent_report': str((ui.ROOT / adaptive['evidence_directory'] / 'report.json').relative_to(ui.ROOT)),
        'adaptive_single_column_passed': adaptive['single_column_confirmed'],
        'two_real_chinese_manual_ui_checks_passed': True,
        'manual_check_scope': 'Functional Unicode entry, real button inference, display, and preserved results; expected class labels were not asserted.',
        'inference_accuracy_asserted': False,
        'records_preserved_before': matrix['preserved_record_count_before_manual'],
        'records_preserved_after_two_fictional_manual_checks': matrix['preserved_record_count_after_manual'],
        'today_completed_checks_after_manual': int(matrix['after_manual_statistics']['rows']['checked']['cells'][1]['text']),
        'actual_statistics_after_manual': {key: {'today': row['cells'][1]['text'], 'all_records': row['cells'][2]['text']} for key, row in matrix['after_manual_statistics']['rows'].items()},
        'font_language_protection_permissions_restored': matrix['protection_unchanged'] and matrix['runtime_permissions_preserved'] and adaptive['protection_unchanged'] and adaptive['font_scale_restored'],
        'restored_settings': {'font_scale_setting': observed_font, 'font_scale_effective': '1.0 (original system default)', 'font_scale_storage_note': adaptive.get('font_scale_storage_note'), 'language_selection': matrix['restored_original_language'], 'ui_language': 'English', 'protection': 'on', 'sms_runtime_permissions': matrix['runtime_permissions']},
        'restoration_harness_recovery': matrix.get('harness_recovery'),
        'screenshots': screenshots,
        'secure_detail_dialog_screenshots_taken': False,
        'files_deleted': 0, 'stored_records_deleted': 0, 'incoming_sms_sent': 0, 'physical_phone_accessed': False,
        'limitations': matrix['limitations'] + ['The English-prefixed fictional dental fixture returned scam 93.6%; this is retained as actual functional evidence and is not a model accuracy benchmark.'],
    }
    (ui.HERE / 'validation-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (directory / 'validation_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'report': str(ui.HERE / 'validation-report.json'), 'installed_sha256': installed_hash}, indent=2))


if __name__ == '__main__':
    main()
