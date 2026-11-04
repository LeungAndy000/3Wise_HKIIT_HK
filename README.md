# WiseMessage

**Authors:** MA, YEUNG, LEUNG, LI (2026)

WiseMessage detects normal, advertising/spam and scam SMS with an on-device BERT-family model using MindSpore Lite. The Android application checks messages on the phone without uploading SMS content. It does not request Internet permission.

## Get started

| Resource | Location |
| --- | --- |
| Repository guide | [START-HERE.md](START-HERE.md) |
| Android and HarmonyOS packages | [release](release/README.md) |
| Android installation and permissions | [Android guide](Project/android/README.md#install-for-a-controlled-phone-test) |
| Android build instructions | [Build guide](Project/android/BUILDING.md) |
| Android emulator on Windows | [Windows guide](Project/windows-app/README.md) |
| Model code, inference and tests | [Project guide](Project/README.md) |
| Detection workflow | [SMS detection overview](Project/docs/SMS_DETECTION_OVERVIEW.md) |
| Model evaluation | [Validation results](Project/docs/VALIDATION_RESULTS.md) |
| Application checks | [Validation evidence](<Validation Evidence/README.md>) |

## Download model and application files

This repository uses Git LFS for models, application packages, datasets and binary dependencies. Install Git LFS before cloning:

```bash
git lfs install
git clone https://github.com/LeungAndy000/3Wise_HKIIT_HK.git
cd 3Wise_HKIIT_HK
git lfs pull
```

## Platform and evaluation scope

The Android interface supports Traditional Chinese, Simplified Chinese and English. English interface support does not establish English-message detection accuracy. The included Android package is a signed test build. The HarmonyOS package is an unsigned debug build for emulator testing; automatic phone SMS integration is not established.

Model evaluation, converted-runtime consistency and interface tests have separate scopes. Dataset qualifications and source terms are documented with the model and datasets. A warning is a reason to pause and verify a request through independently obtained official contact details.
