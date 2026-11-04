param([switch]$NoInstall)
$ErrorActionPreference = 'Stop'
$AppRoot = $PSScriptRoot
$Config = Get-Content -LiteralPath (Join-Path $AppRoot 'emulator-settings.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $Config.apk_file) { throw 'The local emulator configuration must identify the packaged APK.' }
$Apk = (Resolve-Path -LiteralPath (Join-Path $AppRoot $Config.apk_file)).Path
if ((Get-FileHash -LiteralPath $Apk -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Config.apk_sha256) { throw 'APK SHA256 does not match the packaged signed app. Refusing to launch or install.' }
$RunDir = Join-Path $AppRoot 'run'
New-Item -ItemType Directory -Path $RunDir -Force | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$Log = Join-Path $RunDir "launch-$Stamp.log"
function Record([string]$Message) { $Line = "$(Get-Date -Format o) $Message"; Write-Host $Message; Add-Content -LiteralPath $Log -Value $Line -Encoding UTF8 }
function Invoke-Adb([string[]]$Command) {
    # Windows PowerShell can turn harmless native stderr into a terminating error.
    # Capture it and let ADB's actual exit code decide whether the command failed.
    $PreviousErrorPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $Output = & wsl.exe -d $Config.distribution --exec $Config.adb -s $Config.serial @Command 2>&1
        $AdbExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $PreviousErrorPreference
    }
    if ($AdbExitCode -ne 0) { throw "Emulator ADB operation failed: $($Command[0]). $Output" }
    return ($Output -join "`n").Trim()
}
function Quote-ProcessArgument([string]$Value) {
    # Start-Process flattens ArgumentList. Quote each value for Windows argv parsing,
    # including the copied directory name, which contains spaces.
    if ($Value.Length -gt 0 -and $Value -notmatch '[\s"]') { return $Value }
    $Escaped = $Value -replace '(\\*)"', '$1$1\"'
    $Escaped = $Escaped -replace '(\\+)$', '$1$1'
    return '"' + $Escaped + '"'
}
Record 'WiseMessage: actual Android application in a visible Android Emulator window.'
Record "SDK: $($Config.sdk); AVD: $($Config.avd); serial: $($Config.serial); WSLg display."
$Avds = & wsl.exe -d $Config.distribution --exec $Config.emulator -list-avds 2>&1
if ($LASTEXITCODE -ne 0 -or -not ($Avds -contains $Config.avd)) { throw 'The configured project AVD is unavailable. No emulator data will be removed or recreated.' }
try { $Current = & wsl.exe -d $Config.distribution --exec $Config.adb -s $Config.serial get-state 2>$null } catch { $Current = 'offline' }
$AlreadyRunning = ($LASTEXITCODE -eq 0 -and ($Current -join '').Trim() -eq 'device')
if (-not $AlreadyRunning) {
    $WindowsRoot = $AppRoot.Replace('\','/')
    $LinuxRoot = & wsl.exe -d $Config.distribution --exec /usr/bin/wslpath -a -u $WindowsRoot
    if ($LASTEXITCODE -ne 0 -or -not $LinuxRoot) { throw 'Unable to resolve the application path inside WSL.' }
    $GuiLibraries = $LinuxRoot.Trim() + '/dependencies/linux-root/usr/lib/x86_64-linux-gnu'
    $OutLog = Join-Path $RunDir "emulator-$Stamp.log"
    $ErrorLog = Join-Path $RunDir "emulator-$Stamp-error.log"
    $Arguments = @('-d', $Config.distribution, '--exec', '/usr/bin/env', 'QT_QPA_PLATFORM=xcb', ('LD_LIBRARY_PATH=' + $GuiLibraries), "ANDROID_SDK_ROOT=$($Config.sdk)", $Config.emulator, '-avd', $Config.avd, '-no-audio', '-no-boot-anim', '-no-snapshot', '-gpu', 'swiftshader_indirect', '-feature', '-Vulkan', '-cores', '4', '-memory', '4096', '-port', "$($Config.port)", '-skin', '1080x2400')
    $ArgumentLine = ($Arguments | ForEach-Object { Quote-ProcessArgument ([string]$_) }) -join ' '
    $EmulatorProcess = Start-Process -FilePath 'wsl.exe' -ArgumentList $ArgumentLine -WindowStyle Hidden -PassThru -RedirectStandardOutput $OutLog -RedirectStandardError $ErrorLog
    Record 'Starting the emulator window. Initial boot can take up to two minutes.'
    $Deadline = (Get-Date).AddSeconds(180)
    do {
        Start-Sleep -Seconds 1
        $EmulatorProcess.Refresh()
        if ($EmulatorProcess.HasExited) { throw "The emulator exited. Inspect $ErrorLog" }
        try { $Current = & wsl.exe -d $Config.distribution --exec $Config.adb -s $Config.serial shell getprop sys.boot_completed 2>$null } catch { $Current = '' }
    } while (($LASTEXITCODE -ne 0 -or ($Current -join '').Trim() -ne '1') -and (Get-Date) -lt $Deadline)
    if (($Current -join '').Trim() -ne '1') { throw 'Emulator boot timed out. The AVD and all files are preserved. Inspect the run logs.' }
} else { Record 'Reusing the configured emulator; other devices are not accessed.' }
$ActualAvd = Invoke-Adb @('emu','avd','name')
if (-not ($ActualAvd -split "`n" | Where-Object { $_.Trim() -eq $Config.avd })) { throw 'The selected emulator does not match the project AVD. Refusing to install.' }
$Abis = Invoke-Adb @('shell','getprop','ro.product.cpu.abilist')
if ($Abis -notmatch 'arm64-v8a') { throw 'The configured emulator does not offer the ARM64 translation required by this APK.' }
if ($Config.dedicated_windows_demo) {
    Invoke-Adb @('shell','svc','wifi','disable') | Out-Null
    Invoke-Adb @('shell','svc','data','disable') | Out-Null
    Record 'Dedicated demo Wi-Fi and mobile data are off. SMS simulation and local inference remain available.'
}
if (-not $NoInstall) {
    $WindowsApk = $Apk.Replace('\','/')
    $LinuxApk = & wsl.exe -d $Config.distribution --exec /usr/bin/wslpath -a -u $WindowsApk
    if ($LASTEXITCODE -ne 0 -or -not $LinuxApk) { throw 'Unable to resolve the APK path in WSL.' }
    Record 'Installing/updating the verified signed APK; existing app data is preserved.'
    $Installed = Invoke-Adb @('install','-r',$LinuxApk.Trim())
    if ($Installed -notmatch 'Success') { throw "APK installation failed: $Installed" }
}
$Started = Invoke-Adb @('shell','am','start','-n',"$($Config.package)/.MainActivity")
Record 'WiseMessage is open in the Android emulator. Grant SMS access and enable protection in its Settings when you want incoming SMS checks.'
Record 'No web interface, HTTP model server, training, phone access, or network inference is used.'
$State = [ordered]@{status='running';updated_at=(Get-Date -Format o);distribution=$Config.distribution;avd=$Config.avd;serial=$Config.serial;package=$Config.package;apk_sha256=$Config.apk_sha256;abis=$Abis;visible_emulator_requested=$true;existing_avd_preserved=$true;user_phone_accessed=$false;files_deleted=0;log=$Log}
$State | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $RunDir 'emulator-session.json') -Encoding UTF8
