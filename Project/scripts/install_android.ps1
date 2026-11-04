[CmdletBinding()]
param([string]$Serial)
$ErrorActionPreference = 'Stop'
$WiseMessageRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$Adb = Join-Path $WiseMessageRoot 'artifacts\android\toolchain\windows-platform-tools\platform-tools\adb.exe'
if (-not (Test-Path -LiteralPath $Adb)) {
    throw 'Windows ADB is missing. Run the Android build setup first.'
}
$LatestPath = Join-Path $WiseMessageRoot 'artifacts\android\latest_build.json'
if (-not (Test-Path -LiteralPath $LatestPath)) { throw 'No verified Android build exists. Run scripts\build_android.ps1 first.' }
$Latest = Get-Content -Raw -Encoding UTF8 -LiteralPath $LatestPath | ConvertFrom-Json
$Report = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $WiseMessageRoot $Latest.report) | ConvertFrom-Json
$Release = $Report.apks | Where-Object { $_.apk -match '-release\.apk$' } | Select-Object -First 1
if ($null -eq $Release) { throw 'The verified build report does not contain a release APK.' }
$Apk = Join-Path $WiseMessageRoot $Release.apk
$ActualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Apk).Hash.ToLowerInvariant()
if ($ActualHash -ne $Release.sha256) { throw 'APK hash differs from the verified build report.' }
if (-not $Serial) {
    $Devices = @(& $Adb devices | Where-Object { $_ -match '^([^\s]+)\s+device$' } | ForEach-Object { ($_ -split '\s+')[0] })
    if ($Devices.Count -ne 1) {
        & $Adb devices -l
        throw 'Connect and authorize exactly one Android phone, or pass -Serial. No installation was attempted.'
    }
    $Serial = $Devices[0]
}
Write-Host 'Installing the WiseMessage local test APK. SMS and notification permissions must be granted on the phone.'
& $Adb -s $Serial install -r $Apk
if ($LASTEXITCODE -ne 0) { throw 'APK installation failed. Read the Android installation guide for device authorization and Samsung installer settings.' }
& $Adb -s $Serial shell am start -n 'hk.wisemessage.app/.MainActivity'
if ($LASTEXITCODE -ne 0) { throw 'Installation succeeded but the launch failed. Open WiseMessage on the phone.' }
