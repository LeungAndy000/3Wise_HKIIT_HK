# Building the WiseMessage Android test package

Run in Windows PowerShell from the `WiseMessage Android\Project` directory:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_android.ps1
```

For a UI-only update with the verified toolchain and cached dependencies:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_android.ps1 -Offline -ReuseNative
```

`-Offline` uses cached Gradle dependencies and the previous verified wrapper
checksum. `-ReuseNative` verifies all inference assets and the existing source
runtime, then requires the APK's stripped native runtime and signing certificate
to match the previous release exactly. No code or APK is submitted to a service.
The version name and version code come from `app/build.gradle`; output names
follow that version and preserve all earlier versioned APKs.

The version 2 language change provides English, Traditional Chinese and
Simplified Chinese **interface** resources. It leaves the Chinese model intact.
Audit complete translations and formatting arguments locally with:

```powershell
python android/build-tools/verify_locale_resources.py
```

The build uses Ubuntu WSL and an isolated Android toolchain. Tool locations are
read from `artifacts/android/toolchain/toolchain.json` and `ndk.json`; these must
point to the SDK, JDK, Gradle and NDK installed in the selected WSL environment.
Android Studio is optional. The first build downloads the official toolchain and
Gradle dependencies; subsequent builds reuse the cache. Building does not install
the application on a phone.

The pinned build is Java 17, Gradle 8.13, Android Gradle Plugin 8.13.2, Android SDK
36, Build Tools 36.0.0, and NDK r28c. The app targets Android 16/API 36, supports API 26 and
above, and packages only `arm64-v8a` for the Samsung S26 Ultra. A newer Android
version on the device is compatible with this target; behavior still needs to be
tested on the actual phone. The compatibility choices follow the
[official AGP compatibility table](https://developer.android.com/build/releases/agp-8-13-0-release-notes).

The script builds a release APK, a separate `.debug` APK, and an instrumentation
test APK. Before packaging, NDK clang/lld links the unchanged official MindSpore
Lite ARM64 static runtime and the small JNI adapter into a new native library
with real 16 KB load segments. It statically links libc++; the upstream 4 KB
shared libraries and Java AAR are not packaged. Both app builds include the
local model. Release signing uses the existing **local test identity**, kept
outside this submission folder. Before rebuilding, set `WISEMESSAGE_SIGNING_DIR`
to the private directory containing both `wisemessage-test.jks` and
`test-signing.properties`. Keep these unchanged to produce updates accepted
over an existing test installation. The build does not create a replacement
identity. This is not a production distribution certificate.

For a PowerShell build, use an existing private Windows directory. The following
path is an example, not a directory included in this package:

```powershell
$env:WISEMESSAGE_SIGNING_DIR = 'F:\Private WiseMessage Signing'
.\scripts\build_android.ps1 -Offline -ReuseNative
```

The wrapper translates the Windows directory for WSL and forwards the variable.
For a direct WSL build, set the equivalent Linux path, for example
`export WISEMESSAGE_SIGNING_DIR='/mnt/f/Private WiseMessage Signing'`.
Installing the already signed APK does not require this variable or the signing
files. Keep signing files private and outside the submission.

Each build keeps a timestamped directory in `artifacts/android/builds/`, including
Gradle output, APKs, package metadata, signature verification, permissions, and
16 KB checks. `artifacts/android/latest_build.json` identifies the latest fully
verified build. A successful build runs JVM unit tests and Android lint, verifies
APK signatures with `apksigner`, checks uncompressed ARM64 libraries with
`zipalign -c -P 16`, and checks every ELF load segment for 16 KB alignment. It also
rejects Internet permission and rejects packages missing a local model asset.
The checks follow [Android's 16 KB page-size guidance](https://developer.android.com/guide/practices/page-sizes).

The verified release APK is also copied to
`artifacts/android/WiseMessage-3.2.0-test-arm64.apk` for installation. The versioned
build directory retains the exact APK and report for each successful build.
Windows ADB is bundled locally so USB installation does not depend on forwarding
the phone into WSL. With USB debugging authorized on the phone, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_android.ps1
```

The installer verifies the APK hash, uses `adb install -r`, and opens onboarding.
It does not grant permissions silently, change the default SMS application, or
read phone messages. In Android, SMS permissions are hard restricted and require
the installer allowlist as well as the user's runtime permission; do not add
`--restrict-permissions` to the ADB installation command. See the
[official SMS permission reference](https://developer.android.com/reference/android/Manifest.permission#RECEIVE_SMS).

Building an instrumentation APK does not execute it. The build report records
whether a physical device has actually been tested; an empty ADB device list
means phone testing remains outstanding. See the project Android installation
guide for on-device permission and incoming-SMS tests. Installation alone does
not grant SMS or notification permissions.

## Environment configuration

The SDK, AVD and Gradle cache are external prerequisites. Check the toolchain
metadata against the current environment before building. Use
`-Offline -ReuseNative` only when the required tools, dependencies and verified native
runtime are already available. The Gradle cache defaults to
`~/.cache/wisemessage-gradle` in WSL; `WISEMESSAGE_GRADLE_CACHE` can override it.

Recorded emulator validation is under `../../Validation Evidence/Android/`
relative to this directory.
