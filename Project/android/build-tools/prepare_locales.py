"""Maintain complete Android UI translations; no model or SMS-processing changes."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "app/src/main/res"

ENGLISH = {
    "tagline": "SMS scam detection · AI on your phone",
    "local_badge": "Works offline · No SMS uploads",
    "language_title": "App language",
    "language_button": "Language / 語言 / 语言",
    "language_system": "Use phone language",
    "language_help": "Choose the interface language. The unchanged AI model checks Traditional and Simplified Chinese SMS; English message detection has not been validated.",
    "protection_title": "Incoming SMS protection",
    "monitor_toggle": "Check newly received SMS",
    "monitor_off": "Protection is off. You can still paste an SMS for an on-device check.",
    "monitor_ready": "Incoming SMS checks are enabled and scam warning notifications are available.",
    "monitor_no_notifications": "Incoming SMS checks are enabled, but notifications are denied or disabled. Results appear only in local history.",
    "monitor_no_sms": "SMS access is unavailable. Check system permissions and how the app was installed.",
    "monitor_model_error": "The last on-device check failed. Protection may be unavailable. Try a manual check and review the history.",
    "monitor_limits": "Checks only SMS that Android allows this app to access. RCS, WhatsApp and some protected verification codes are excluded. Battery saving or system scheduling may delay alerts.",
    "otp_delay": "Android 17 may delay access to certain verification-code SMS by three hours. This app cannot check those messages immediately.",
    "allow_notifications": "Allow warning notifications",
    "app_settings": "Open system settings",
    "consent_title": "Check new SMS on your phone",
    "consent_body": "WiseMessage reads new SMS, analyses them on this phone, and saves their contents and results in private app storage. Only messages meeting the scam warning condition trigger a notification; notifications do not show SMS contents. You can turn protection off at any time. This app does not send or delete SMS, or upload their contents.",
    "enable": "Agree and enable",
    "cancel": "Cancel",
    "permission_denied": "SMS access was denied or restricted by Android. Manual checks are still available. For this test installation, see the supplied installation guide.",
    "manual_title": "Paste an SMS to check",
    "manual_hint": "Enter a Traditional or Simplified Chinese SMS here…",
    "check_message": "Check on this phone",
    "checking": "Analysing on this phone. Loading the model for the first time may take a moment…",
    "enter_message": "Enter an SMS message first.",
    "too_long": "Enter at most 20,000 characters per check.",
    "scan_failed": "The on-device check did not finish. Try again; do not interpret this as a safe result.",
    "result_scam": "Possible scam · Verify first",
    "result_spam": "Possible advertising or spam",
    "result_normal": "No high risk detected · Still verify",
    "result_review": "Uncertain · Verify independently",
    "probabilities": "Normal %1$.1f%%  ·  Spam %2$.1f%%  ·  Scam %3$.1f%%",
    "model_timing": "On-device inference: %1$d ms",
    "truncated": "This message exceeds the model length. Only the beginning was analysed.",
    "not_guarantee": "AI scores are not a guarantee. Do not reveal passwords, transfer money or install unfamiliar software based on a prediction. Find official contact details independently to verify.",
    "inbox_title": "Phone SMS inbox",
    "scan_inbox": "Check the latest 50 SMS",
    "inbox_consent": "Reads up to the latest 50 inbox SMS and saves their contents and results locally. Original messages are not changed. Old messages do not trigger a series of warning notifications.",
    "scan": "Start checking",
    "inbox_queued": "%1$d SMS queued. Results will appear in local history as each check finishes.",
    "inbox_failed": "Cannot read the SMS inbox. Check SMS permissions. Manual checks are still available.",
    "history_title": "Local check history",
    "history_empty": "No records yet. Incoming SMS and manual check results will appear here.",
    "refresh": "Refresh history",
    "pending": "Waiting for on-device analysis",
    "failed": "Analysis failed · Verify independently",
    "source_incoming": "New incoming SMS",
    "source_inbox": "Inbox SMS",
    "source_manual": "Manual check",
    "unknown_sender": "Sender not provided",
    "details_title": "On-device SMS analysis",
    "close": "Close",
    "notification_channel": "SMS scam warnings",
    "notification_channel_description": "Alerts for SMS classified as possible scams. Notifications do not include SMS contents.",
    "notification_title": "WiseMessage: possible scam SMS",
    "notification_body": "Do not pay or share sensitive information. Tap to review on this phone.",
    "notification_public": "A security reminder was received",
    "notification_test": "Test warning notification",
    "test_notification_title": "WiseMessage: test notification",
    "test_notification_body": "This tests notifications. It is not a model detection result.",
    "notification_blocked": "Notifications are denied or this channel is disabled. Enable them in system settings.",
    "privacy_title": "Your SMS stays on your phone",
    "privacy_body": "The model is included in the app and works entirely offline. Records remain in private app storage with cloud backup disabled. Notifications hide senders and message contents. This is a development test app; notification reliability depends on phone settings.",
    "model_loading": "Local model: loads when you check a message",
    "model_ready": "Local model: %1$s",
}


def write_resources(destination, translations, *, include_name=False):
    destination.parent.mkdir(parents=True, exist_ok=True)
    resources = ET.Element("resources")
    if include_name:
        ET.SubElement(resources, "string", {"name": "app_name", "translatable": "false"}).text = "WiseMessage"
    for key, value in translations.items():
        # Android XML escaping differs from XML itself: apostrophes must be escaped.
        ET.SubElement(resources, "string", {"name": key}).text = value.replace("'", "\\'")
    ET.indent(resources, space="    ")
    ET.ElementTree(resources).write(destination, encoding="utf-8", xml_declaration=True)


def main():
    original = ET.parse(RES / "values/strings.xml").getroot()
    traditional = {row.attrib["name"]: row.text or "" for row in original if row.attrib["name"] != "app_name"}
    # First run takes the original Traditional resources; later runs use the script-qualified set.
    if (RES / "values-b+zh+Hant/strings.xml").exists():
        traditional = {row.attrib["name"]: row.text or "" for row in ET.parse(RES / "values-b+zh+Hant/strings.xml").getroot()}
    simplified = {row.attrib["name"]: row.text or "" for row in ET.parse(RES / "values-zh-rCN/strings.xml").getroot()}
    traditional.update(language_title="應用程式語言", language_button="Language / 語言 / 语言", language_system="跟隨手機語言",
                       language_help="此選項只改變介面語言。AI 模型維持不變，檢查繁體及簡體中文 SMS；英文訊息偵測尚未驗證。",
                       privacy_body="模型隨應用程式安裝，完全離線運作。紀錄只保存在應用程式私人空間，停用雲端備份。通知隱藏寄件者及內容。此應用程式是開發測試版本；通知可靠性取決於手機設定。")
    simplified.update(language_title="应用语言", language_button="Language / 語言 / 语言", language_system="跟随手机语言",
                      language_help="此选项只改变界面语言。AI 模型保持不变，检查繁体及简体中文 SMS；英文消息检测尚未验证。",
                      privacy_body="模型随应用安装，完全离线运行。记录只保存在应用私人空间，停用云端备份。通知隐藏发件人及内容。此应用是开发测试版本；通知可靠性取决于手机设置。")
    if set(ENGLISH) != set(traditional) or set(ENGLISH) != set(simplified):
        raise ValueError("Every supported language must translate every UI string")
    write_resources(RES / "values/strings.xml", ENGLISH, include_name=True)
    write_resources(RES / "values-b+zh+Hant/strings.xml", traditional)
    write_resources(RES / "values-b+zh+Hans/strings.xml", simplified)
    write_resources(RES / "values-zh-rCN/strings.xml", simplified)
    print(f"Prepared {len(ENGLISH)} UI strings in English, Traditional and Simplified Chinese")


if __name__ == "__main__":
    main()
