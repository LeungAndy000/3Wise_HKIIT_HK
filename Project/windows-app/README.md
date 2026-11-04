# WiseMessage Android on Windows

Double-click [Launch-WiseMessage.cmd](Launch-WiseMessage.cmd). The launcher starts the configured WSLg Android emulator and runs the signed WiseMessage 3.2 test APK.

1. Wait for Android to boot. The launcher verifies the APK hash and installs or updates it while preserving existing records.
2. Open WiseMessage Settings, enable incoming-SMS protection and grant the required SMS and notification permissions. Reading the inbox is separately optional.
3. Select Traditional Chinese, Simplified Chinese or English. Use the dashboard, inbox, detection results and statistics. Notification Testing is in Settings.

## Prerequisites and configuration

This folder contains the launcher, APK and Ubuntu GUI-library dependencies. Install WSL Ubuntu with WSLg, the Android SDK, an Android system image and an AVD separately. Before launch, check the paths and device settings in [emulator-settings.json](emulator-settings.json) against the target computer.

| Configuration field | Purpose |
| --- | --- |
| `distribution` | WSL distribution containing the Android tools |
| `sdk`, `emulator`, `adb` | Absolute Linux paths to the SDK and its emulator and ADB executables |
| `avd`, `avd_path` | Provisioned AVD name and directory |
| `port`, `serial` | Emulator port and matching ADB device identifier |
| `apk_file`, `apk_sha256` | Application package path and expected checksum |

The recorded demo uses Android 11/API 30 Google APIs x86_64 with ARM64 translation. The launcher uses the configured tools and image; it does not download them.

## Controlled SMS tests

The emulator does not read a physical phone. From a terminal in this folder, `python send-test-sms.py both` injects fictional Chinese SMS into the configured AVD after checking its identity and saves a validation report.

The dedicated demo disables Wi-Fi and mobile data. The APK has no Internet permission and checks SMS locally. Interface language support does not establish message-detection accuracy in that language.

## Evidence and troubleshooting

- [Recorded build and upgrade validation](../artifacts/android/v3_2_upgrade_validation.json).
- [Recorded emulator UI validation](<../../Validation Evidence/Android/ui-v3_2-validation/run-20261025T083909Z/validation_report.json>).
- [Android installation guide](../android/README.md#install-for-a-controlled-phone-test).
- [Source build instructions](../android/BUILDING.md).

If launch fails, inspect the newest `run/emulator-*-error.log`. Check WSLg, the configured AVD and availability of port 5582. The launcher refuses mismatched devices or APK hashes. [Stop-WiseMessage.cmd](Stop-WiseMessage.cmd) closes only this AVD and preserves its files and records.

The two recorded Chinese manual flows verify operation and display. They do not measure detection accuracy or establish physical Samsung version 3.2 performance.
