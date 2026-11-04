# WiseMessage Android — on-device SMS scam detection

## Version 3.2: aligned dashboard and statistics

Install [`WiseMessage-3.2.0-test-arm64.apk`](../artifacts/android/WiseMessage-3.2.0-test-arm64.apk)
over the existing signed application without uninstalling or clearing data.
The four dashboard action cards now share equal dimensions. Main-screen
wording is shorter, technical explanations remain in Settings, and statistics
use aligned Today / All records columns and a seven-day table. The inbox,
result filters, permissions, consent and detection decisions are preserved.

The offline build passed **28 JVM tests**, **11 synthetic host SQLite checks**
and translation checks for **215 strings per language**. Release lint has
zero errors and 70 warnings. APK signatures and 16 KB ELF/ZIP alignment are
verified; the application ID, signing certificate, model, tokenizer and native
runtime match version 3.1. No Internet or SMS-sending permission was added.
See the [3.2 build and validation report](../artifacts/android/v3_2_upgrade_validation.json)
for the current evidence and test scope. Host checks are separate from Android
emulator execution. The earlier 18 functional emulator checks apply to version
3.1; physical version 3.2 testing on the Samsung S26 Ultra remains pending.

## Version 3.1: shorter lists and result categories

Install `artifacts/android/WiseMessage-3.1.0-test-arm64.apk` over the existing
signed application, without uninstalling or clearing data. Version 3.0 is
confirmed working on the user's phone; version 3.1 needs the separate
[phone checklist](LIST_NAVIGATION_DEVICE_QA.md).

**Messages** now provides two entries: **Read phone SMS** and **Detection
results**. Each destination shows at most **20 rows per page**, with Previous,
Next and Refresh controls. Paging replaces rows instead of growing a long
combined list. Reading a phone SMS still requires separate consent and inbox
permission; detection results use existing private records and do not require
READ_SMS.

Results default to **Harmful · possible spam or scam**. The other filters are
**No high risk detected**, **Review or unfinished**, and **All results**.
Uncertain, pending and failed checks remain separate from reassuring normal
decisions. Filters organise model outputs; they do not establish that a message
is legitimate. The automatic incoming-warning policy still alerts on scam
decisions only. Three UI languages, stored records, offline inference and the
packaged model remain unchanged. This update does not add OCR.

The version 3.1 build passed **28 JVM tests**, **11 host SQLite checks** for
filtering and cursor pagination, and translation checks for **210 strings per
language**. Lint has zero errors. The signed APK passes 16 KB ELF/ZIP checks;
its model, tokenizer and native runtime match version 3 byte for byte. See the
historical report `artifacts/android/v3_1_upgrade_validation.json`, which is not
included in this submission.
Phone instrumentation is compiled but has not been run for v3.1 here.

The [SMS detection overview](../docs/SMS_DETECTION_OVERVIEW.md) describes the
existing input routes, local processing and notification rules. OCR is separate
research and is not included in the current APK.

## Version 3: protection dashboard and settings

Install `artifacts/android/WiseMessage-3.0.0-test-arm64.apk` over the existing
app. The package and signing identity are preserved; do not uninstall first.
The user now confirms that version 3 runs on their phone. The historical
build reports record the host checks performed when it was packaged.

- **Home:** a shield status is green only when incoming monitoring is enabled,
  `RECEIVE_SMS` is granted, app and Android warning notifications are enabled,
  and no scanner failure is recorded. Otherwise it is red and explains why.
  Green indicates enabled protection functions, not guaranteed scam detection.
- **Today:** received counts are queried from accessible SMS currently in the
  phone inbox and dated in the phone's current local day. Without `READ_SMS`,
  the count is an em dash with an access hint. Checked counts use successful
  completion time, including manual checks. An old SMS checked today does not
  become a newly received SMS.
- **Quick actions:** check the complete accessible SMS inbox, read messages,
  check text manually, or open statistics. Bottom navigation provides Home,
  Messages, Statistics and Settings.
- **Read SMS:** separately consent to inbox access; load messages 50 at a time.
  The list shows sender/date; bodies remain hidden until a secure detail opens.
  Links are non-clickable. A selected SMS can be queued without copying it.
- **Check all SMS:** import every accessible inbox row into the local queue,
  deduplicate existing records and retry failed records. There is no 50-message
  scan limit. Progress distinguishes queuing from pending/completed analysis.
  Stop adding SMS halts further imports; already queued checks continue.
  Keep the app open until queuing finishes. Committed pending records survive
  process interruption, but an incomplete import needs another check-all action.
- **Statistics:** today's and lifetime classification counts plus seven local
  days of completed checks. Uncertain unwanted results are counted as review,
  separately from normal results. Large text also gets a textual chart summary.
- **Settings:** monitoring, app warning opt-out, Android SMS/notification access,
  notification testing and persistent interface language. Inbox permission is
  optional for incoming monitoring. Permission grants alone do not enable it.

The SQLite upgrade adds completion timestamps without removing old rows or
changing predictions. Earlier completion dates were not recorded: those checks
remain in lifetime statistics and are explicitly reported as undated. They
are not invented as today's activity.

Version 3 passed **20 JVM tests**, **11 host SQLite checks** of SQL extracted
from the actual Java source, translation checks for **184 strings per language**,
and signed APK / 16 KB native packaging checks. Android lint reports zero errors;
remaining warnings include preserved unused resources and pinned tool versions.
The historical report `artifacts/android/v3_upgrade_validation.json` records the
APK identity, unchanged inference assets and exact test boundaries; that report
is not included in this submission.
Device instrumentation is compiled, but has not been executed on a phone.

The model, tokenizer, native inference runtime, warning decisions, offline
operation and three UI languages are preserved. No OCR was added in this UI
release. See [device UI checks](DASHBOARD_DEVICE_QA.md). Historical synthetic
design previews are not included in this package and do not establish device
execution.

## Language selection

The persistent **Language / 語言 / 语言** button is now in **Settings**.
Choose **繁體中文**, **简体中文**, **English**, or the
phone language. All app screens, consent dialogs, result labels, future warning
notifications and notification-channel labels use the selected language.
On Android 13 and newer the choice also appears in Android's per-app language
settings. On older supported phones the app stores the selection privately.

This changes the interface language. The AI model, thresholds, local inference,
SMS handling, private history and permissions are unchanged. **English SMS
detection has not been validated**; selecting English does not retrain the
Chinese model. Existing notifications keep the text they had when posted.

The version code increases to 3, so `adb install -r` retains private records,
language and monitoring preferences. Both version 1 and version 2 APKs remain
available. Android normally blocks installing an older APK over a newer version.

For the version 3 phone check, switch through all three languages, reopen the
app, and confirm the choice persists. Test a manual Chinese message and the
explicit notification-test button in each language. Then send a controlled
carrier SMS to check a real incoming prediction and its translated warning.
The language picker does not change any expected model class or probability.
Physical version 3.1 testing is separate from host compilation and lint.

This test Android application packages the trained WiseMessage Chinese message classifier for offline CPU inference with MindSpore Lite. It supports Traditional and Simplified Chinese, receives permitted incoming **SMS**, and raises a separate warning when the classifier predicts **scam**. Advertising/spam remains a separate label. No SMS content or prediction is sent to a server; the manifest deliberately has **no INTERNET permission**.

The intended test phone is the Samsung S26 Ultra (ARM64). Building an APK does not establish compatibility or notification reliability on that physical phone; complete the device checks below. Android 8.0/API 26 is the minimum; compile/target SDK is 36.

The Android wrapper uses the project's small JNI bridge, statically linked to the official MindSpore Lite CPU static library. It does not load the official Java AAR at runtime. APK validation checks the native library's **16 KiB ELF segment alignment** and the APK's native-library ZIP alignment for current Android phones. Successful build inspection is separate from running inference on the physical Samsung phone.

## Install for a controlled phone test

1. Enable Developer options and USB debugging on the test phone, connect it by USB, and accept the device's debugging prompt.
2. Run `adb devices -l` and confirm the correct phone is authorized. Do not silently select a different connected device.
3. Install the signed test APK using `adb -s PHONE_SERIAL install -r PATH_TO_APK`. By default ADB installation allows the requested restricted permissions unless the `--restrict-permissions` installation option is used. The app still asks the user for SMS and notification permissions. Installing with a phone file manager may use a different installer permission allowlist and can prevent SMS access.
4. Open WiseMessage, enter **Settings**, turn on incoming SMS protection, read the local-storage disclosure, and accept the Android SMS permission request. Allow warning notifications when requested. The dashboard reports missing access instead of claiming full protection.
5. Tap **測試警告通知 / 测试警告通知**. This is explicitly a notification test, not a model detection. Verify the alert appears, then tap it to reopen the app.

On Samsung phones, Auto Blocker can prevent installation from an unapproved
source or block USB commands. If the phone reports such a block, review its
Security and privacy settings for this controlled test. This project does not
change those settings automatically. See Samsung's
[Auto Blocker instructions](https://www.samsung.com/us/support/answer/ANS10003636/).

`RECEIVE_SMS` and `READ_SMS` are Android **hard restricted** permissions: the installer must allowlist them and the user must grant them. A runtime prompt or `pm grant` cannot overcome an installer restriction. If SMS access is blocked, check the installation method, app permissions and your phone's restricted settings. Manual text checks work without SMS permission. A test installer may also explicitly allowlist these permissions through Android's `PackageInstaller.SessionParams.setWhitelistedRestrictedPermissions` API.

This companion app does not replace the phone's default messaging application, write to the SMS provider, send SMS, or intercept delivery. It uses the non-abortable `SMS_RECEIVED` broadcast. Google Play SMS-permission policy is a separate distribution requirement; this test APK is not a Play Store publishing approval.

## What the app does

- **Incoming protection:** user-controlled, initially off. Reassembles multipart SMS, stores one local record, and queues CPU inference using Android JobScheduler. A notification is posted only for incoming messages whose model decision is scam, while monitoring is enabled and notifications are allowed.
- **Manual checks:** paste text and run the same packaged model locally without SMS access or a network connection. Probabilities, inference time, and model truncation are displayed.
- **Inbox checks:** after a separate explanation and `READ_SMS` grant, checks all accessible inbox messages. Reading is paginated 50 at a time; full scanning has no 50-message limit. Original SMS are unchanged and old messages do not generate a burst of scam alerts.
- **Private history:** contents and results stay in app-private SQLite, with cloud backup disabled and explicit Android 12+ cloud/device-transfer exclusion rules. Identical sender/timestamp/text records are deduplicated. Notification text never includes the sender, message body, link, password or verification code. The detail dialog blocks screenshots. No application logging includes SMS content.
- **Durable processing:** native inference runs outside the broadcast receiver and UI thread. Per-message jobs are persisted across reboot. Expedited scheduling is attempted on API 31+; normal scheduling is the fallback when expedited quota is unavailable. Opening/refreshing the app retries scheduling pending records.

No classifier can guarantee a message is legitimate. Do not transfer money, reveal credentials, install software, or follow an unfamiliar link based on a model prediction. Independently obtain the sender's official contact information.

## Samsung / current Android limits

- **SMS only:** RCS/chat messages in Google Messages or Samsung Messages, MMS, WhatsApp, email and other app notifications are outside this receiver. For a real test, send an ordinary carrier SMS from a second phone and confirm it did not use RCS.
- Android can restrict SMS containing one-time passwords or an SMS Retriever app hash. The privileged `RECEIVE_SENSITIVE_NOTIFICATIONS` permission is not available to an ordinary sideloaded companion. WiseMessage cannot promise access to these messages and does not try to bypass that protection.
- On Android 17/API 37, WebOTP-format messages can be withheld from non-exempt apps for **three hours**, both from the incoming broadcast and inbox queries, regardless of target SDK. SMS Retriever hash messages already had a similar delay. Additional standard-OTP restrictions apply to apps targeting API 37; this build targets API 36. The app shows an extra delay notice when running on API 37 or newer.
- Samsung sleeping/deep-sleeping apps, power saving, system job quota/load, notification-channel settings and Do Not Disturb can delay or suppress visible alerts. Check Settings → Apps → WiseMessage → Notifications, and Battery → Background usage limits. Where available, add WiseMessage to **Never auto sleeping apps** / choose unrestricted battery use for the test. Menu names depend on the installed One UI version.
- After **Force stop**, open WiseMessage again before expecting broadcasts. The OS also controls delivery before the first unlock after reboot. Disabling SMS permission prevents new-message access; disabling notification permission leaves results in the app without alerts.
- Existing research validation is not a native Hong Kong/Taiwan carrier-SMS benchmark. Alert false positives and false negatives are possible. Test with benign synthetic messages, not sensitive real OTPs or financial credentials.

## Physical-phone validation checklist

Record the APK SHA-256, phone model/Android/One UI versions, model ID and permission state. Then test:

1. Airplane mode: manual Traditional and Simplified Chinese checks still return finite model probabilities; no download is requested.
2. Deny SMS: manual checks still work and protection status clearly shows unavailable access. Deny notifications: SMS checks can be recorded, but the app clearly reports that alerts cannot appear.
3. Send normal, marketing spam, and scam SMS from a second phone. Check the actual predicted label. Only messages the model labels scam should raise a scam alert; do not force expected labels or treat a notification test as inference validation.
4. Send a long multipart Chinese SMS. Confirm the local detail shows a single concatenated message and any model truncation notice.
5. With the app backgrounded and the phone locked, send a scam test SMS. Measure time from receipt to warning; confirm the lockscreen does not expose sender/content. Tap the warning to open the stored result.
6. Repeat after clearing the app from Recents and after reboot/unlock. Force-stop separately to demonstrate Android's expected limitation and restore operation by opening the app.
7. Scan an inbox containing more than 50 SMS with explicit permission. Confirm all accessible records are queued, repeats are deduplicated, original messages stay unchanged and old scam results do not generate repeated alerts.
8. Re-delivery/inbox rescan must not produce a duplicate stored record for the same sender, body and timestamp. Review individual failures rather than declaring a missed alert a safe message.

The device-only integration instrumentation additionally verifies all **120 tokenizer fixtures** and **96 model probability fixtures** against the original reference: exact token arrays, unchanged predicted labels and a maximum absolute probability difference of 0.001. It reports the device's mean warm inference latency. It also verifies the manual UI, private persistence/deduplication, and the manifest's privacy contract. It deliberately does not read/send real SMS or change the default SMS app. Installing an instrumentation APK and running those tests does not replace carrier-SMS and Samsung background tests.

## Android sources

- [Telephony provider and non-default SMS observers](https://developer.android.com/reference/android/provider/Telephony)
- [SMS_RECEIVED and SMS Retriever delivery restrictions](https://developer.android.com/reference/android/provider/Telephony.Sms.Intents)
- [SMS and sensitive-notification permission protection levels](https://developer.android.com/reference/android/Manifest.permission)
- [Installer allowlisting of restricted permissions](https://developer.android.com/reference/android/content/pm/PackageInstaller.SessionParams#setWhitelistedRestrictedPermissions(java.util.Set%3Cjava.lang.String%3E))
- [Notification runtime permission](https://developer.android.com/develop/ui/views/notifications/notification-permission)
- [Expedited JobScheduler guarantees and quota](https://developer.android.com/reference/android/app/job/JobInfo.Builder#setExpedited(boolean))
- [Broadcast receiver timeout guidance](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs)
- [Android 17 SMS OTP protection and three-hour delay](https://developer.android.com/about/versions/17/behavior-changes-all#sms-otp-protection)
- [Android backup and device-transfer exclusion rules](https://developer.android.com/identity/data/autobackup)

## Build and verification

From PowerShell in the `WiseMessage Android\Project` directory:

```powershell
.\scripts\build_android.ps1
.\scripts\install_android.ps1
```

The build script uses an isolated WSL Android SDK/JDK/NDK toolchain. The install
script uses Windows ADB, verifies the APK hash against the build report, and
requires one authorized phone or an explicit `-Serial`. It leaves SMS and
notification grants to the user on the phone.

The stable signed test APK is
`artifacts/android/WiseMessage-3.2.0-test-arm64.apk`. Versioned release, debug,
and device-instrumentation APKs and logs are retained under
`artifacts/android/builds/`. `artifacts/android/latest_build.json` points to
the exact signature, package-permission, model-asset, native ELF, and ZIP
alignment inspection report. The signing key is a persistent local test key,
not a production distribution identity. It is kept outside this submission;
source builds use `WISEMESSAGE_SIGNING_DIR` as described in [BUILDING.md](BUILDING.md).

Historical host checks completed for the initial port:

- The Lite model preserves all class and unwanted-message decisions across
  **9,577** previously evaluated labelled messages. Maximum probability
  difference from the saved MindSpore results is **6.32e-6**.
- The Java tokenizer matches the Python reference tokenizer on **174**
  cases, including Traditional/Simplified Chinese, multipart-length texts,
  special tokens, and adversarial Unicode/control characters.
- The actual Java/JNI bridge passed **96** model cases and four native error
  paths on Linux x86-64.
- Twenty JVM classifier-decision, language and local-day boundary tests passed. Android lint and the signed APK
  inspection results are recorded by the build script.
- The ARM64 library is genuinely linked with NDK r28c using 16 KB ELF load
  segments. The build independently checks the final APK's ELF and ZIP layout.

These checks do not establish physical Samsung performance. Both Windows and
WSL ADB checks found no connected device during initial packaging, so phone-side
tests were unexecuted in that report. See the version 3.2 report above for current
validation. The device instrumentation checks all **120**
bundled tokenizer fixtures and **96** reference probability cases, and reports
the measured average warm inference time. See the physical-phone checklist
above for carrier SMS receipt and background warning behavior.
