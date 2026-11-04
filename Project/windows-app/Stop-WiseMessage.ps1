$ErrorActionPreference = 'Stop'
$Config = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'emulator-settings.json') -Raw -Encoding UTF8 | ConvertFrom-Json
try { $State = & wsl.exe -d $Config.distribution --exec $Config.adb -s $Config.serial get-state 2>$null } catch { $State = 'offline' }
if ($LASTEXITCODE -ne 0 -or ($State -join '').Trim() -ne 'device') { Write-Host 'The configured WiseMessage emulator is not running.'; exit 0 }
$Name = & wsl.exe -d $Config.distribution --exec $Config.adb -s $Config.serial emu avd name
if ($LASTEXITCODE -ne 0 -or -not ($Name | Where-Object { $_.Trim() -eq $Config.avd })) { throw 'The emulator does not match the project AVD; refusing to stop it.' }
& wsl.exe -d $Config.distribution --exec $Config.adb -s $Config.serial emu kill
if ($LASTEXITCODE -ne 0) { throw 'The configured emulator did not accept shutdown.' }
$Deadline = (Get-Date).AddSeconds(30)
do {
    Start-Sleep -Milliseconds 500
    try { $Current = & wsl.exe -d $Config.distribution --exec $Config.adb -s $Config.serial get-state 2>$null } catch { $Current = 'offline' }
} while (($Current -join '').Trim() -eq 'device' -and (Get-Date) -lt $Deadline)
$SessionPath = Join-Path $PSScriptRoot 'run\emulator-session.json'
if (Test-Path -LiteralPath $SessionPath) {
    $Session = Get-Content -LiteralPath $SessionPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $Session.status = 'stopped'
    $Session.updated_at = (Get-Date -Format o)
    $Session | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $SessionPath -Encoding UTF8
}
Write-Host 'WiseMessage emulator stopped. The AVD, app records, APK and all files are preserved.'
