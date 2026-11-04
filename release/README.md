# WiseMessage application packages

Current application packages are stored by platform:

| Platform | Package | Version | Build status |
| --- | --- | --- | --- |
| Android | [WiseMessage Android APK](Android/WiseMessage-3.2.0-test-arm64.apk) | 3.2.0-test, code 5 | Signed ARM64 test APK |
| HarmonyOS | [WiseMessage HarmonyOS HAP](HarmonyOS/WiseMessage-HarmonyOS-debug-unsigned.hap) | 1.0.0, code 1000000 | Unsigned debug HAP for emulator testing |

Both packages include the model for on-device detection. The `release` folder groups the application packages; their test/debug status is shown above.

## Android

Use the [Android installation guide](../Project/android/README.md#install-for-a-controlled-phone-test). For Windows emulation, follow the [emulator guide](../Project/windows-app/README.md).

## HarmonyOS

This native HarmonyOS 6.0.1 / API 21 package supports on-device message-text analysis. Automatic phone SMS integration and physical HarmonyOS phone testing are not established. Installation requires a compatible emulator and the appropriate development configuration. This unsigned debug HAP is not a production-signed phone distribution package.

Package checksums are listed in [SHA256SUMS.txt](SHA256SUMS.txt).
