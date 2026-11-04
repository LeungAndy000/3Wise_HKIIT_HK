# WiseMessage dashboard: device verification

This checklist applies to the redesigned native Android dashboard. Host-side
compilation, JVM tests, APK inspection and lint do not establish that the new
screens have run on a phone. The previously released v1/v2 APKs and signing key
must remain available, and updating must not require uninstalling the app.

## Historical execution record

On 2026-10-23, Windows ADB and WSL ADB both reported no connected devices.
The existing WSL SDK had no emulator executable or Android system image; no
AVD was found in the existing WSL or conventional Windows Android locations.
At that time, `/dev/kvm` existed but no emulator was configured for execution.

The `AppFlowInstrumentation` checks include navigation and app notification
opt-out. Compilation alone does not establish device execution; use the report
for the specific application version to confirm which checks were run.

## Install and identify

1. Record APK SHA-256, version code, certificate fingerprint, phone model,
   Android version and One UI version.
2. Update the existing signed installation with `adb install -r APK_PATH`.
   Do not uninstall or clear app data. Confirm earlier private records and
   selected language remain available after the update.
3. Confirm all screens work in airplane mode. There must be no model download
   and no Internet permission in the manifest.

## Dashboard and navigation

Test Traditional Chinese, Simplified Chinese and English separately, including
after reopening the app and after changing Android's per-app language. On each:

- Home shows protection state, received-today count and checked-today count.
- Global scan, read SMS, manual check and statistics actions open the intended
  screen. The bottom navigation returns to Home, Messages, Statistics or Settings.
- Language, monitoring, notifications, permission-management and test-alert
  controls belong in Settings.
- Back navigation, display cutouts, system bars, keyboard and 200% system font
  do not hide controls. Confirm both light and dark system settings and a narrow
  phone layout; the app's own palette must remain readable.
- Red/green status includes readable text and a status icon so color is not the
  only way to interpret it.

## Protection truthfulness

Start with monitoring off: protection is red. Enable monitoring using the app's
consent flow and accept Android RECEIVE_SMS permission; verify the switch reflects
the actual grant. Denying permission must not produce a green state.

Repeat with each condition unavailable: app notification toggle off, Android
notification permission off, warning channel blocked, SMS permission revoked,
and a model-load/inference failure. The dashboard must remain red with an
explanation. Restore each setting through the normal user flow.

Green requires incoming monitoring, SMS access, app warning preference, system
notification/channel access and a ready model. Green describes configured
protection; it cannot guarantee carrier delivery, background execution or scam
classification accuracy. READ_SMS is a separate permission for optional inbox
reading and scanning, not a prerequisite for receiving new SMS broadcasts.

## Daily counters and statistics

- A manual check increments checked-today after a successful persisted
  classification, but never received-today.
- A newly received carrier SMS appears once. Incoming receipt followed by inbox
  scanning must not duplicate the same sender/body/timestamp record.
- Scan an older SMS today: checked-today increases after classification, but
  received-today does not increase for an SMS received on a previous day.
- A failed or pending check does not count as complete. Retrying/completing
  the same pending record must not add two completions.
- Calendar days use the phone's local timezone and an exclusive next-midnight
  boundary. Check midnight rollover; changing timezone should recalculate dates.
- Seven-day chart values, label totals, pending/failed counts and Home counters
  agree with the underlying records. Existing v1/v2 completed records with no
  completion date remain historical totals; their check day must not be invented.
- If READ_SMS is denied, distinguish app-observed SMS from the phone-wide inbox
  count. SMS received while monitoring was off must not be silently presented
  as a complete phone-wide count when no inbox access is available.

## Global/inbox scan

Use an inbox containing more than 50 benign synthetic SMS, duplicates and old
messages. Confirm the UI's stated scan scope matches what is read, progress
updates do not freeze navigation, and old scam classifications do not create a
burst of incoming-message alerts. Deny READ_SMS to verify a clear permission
state. Repeat the scan and verify deduplication. Original phone SMS must remain
unchanged: no deleting, sending or writing to the system SMS provider.

## Notifications and model parity

The app warning toggle must suppress both ordinary incoming scam alerts and
explicit test alerts while off. Test alerts must say they are tests; they do
not establish a model prediction. Restore the toggle and test the channel.
Confirm alerts expose no sender, body, URL, OTP or credentials on the lockscreen.

Run the instrumentation APK against its matching debug app to verify all 120
tokenizer fixtures, 96 model fixtures, manifest restrictions, three localized
notification labels, record deduplication, completion-day statistics, a
non-destructive in-memory schema migration, screen navigation, app notification
opt-out and a manual model inference. The instrumentation stores synthetic test
rows in the debug app's private database and deliberately preserves them. It
does not send SMS, grant SMS permissions, clear history or change the default
messaging application.

Carrier SMS, locked-screen warnings, Samsung sleeping-app behavior and restricted
permission installer behavior still require the physical-phone checklist in
`README.md`. Do not label those tests as passed based on host checks.
