# WiseMessage Android

This repository contains Android and HarmonyOS application packages, Android source code, the SMS detection model, datasets and validation evidence.

| Item | Location |
| --- | --- |
| Android and HarmonyOS application packages | [release folder](release/README.md) |
| Install the Android app | [Installation guide](Project/android/README.md#install-for-a-controlled-phone-test) and [signed APK](release/Android/WiseMessage-3.2.0-test-arm64.apk) |
| Run Android on Windows | [Windows emulator guide](Project/windows-app/README.md) |
| Application source and build instructions | [Android source guide](Project/android/README.md) and [build guide](Project/android/BUILDING.md) |
| Model structure, inference and testing | [Project instructions](Project/README.md) |
| Current model | `Project/artifacts/runs/domain_v2_20261023_1050/model/` |
| Training and evaluation data | `Project/data/` |
| Recorded validation | [Model results](Project/docs/VALIDATION_RESULTS.md) and `Validation Evidence/Android/` |
| SMS detection workflow | [Detection overview](Project/docs/SMS_DETECTION_OVERVIEW.md) |

The supplied APK is version **3.2.0-test**, version code **5**, package `hk.wisemessage.app`. Detection runs on the phone through MindSpore Lite. The interface supports Traditional Chinese, Simplified Chinese and English; interface language support does not establish English-message detection accuracy.

Install the supplied APK directly on a compatible Android device. Source builds require a configured private signing directory and the toolchains listed in the build guide. Windows emulation requires WSLg, the Android SDK, an emulator image and a provisioned AVD.

Recorded model evaluation, runtime consistency checks and emulator tests have different scopes. Keep those distinctions when presenting results. Suspicious requests should be verified through independently obtained official contact details.
