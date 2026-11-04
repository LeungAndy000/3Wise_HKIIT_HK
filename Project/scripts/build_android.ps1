[CmdletBinding()]
param(
    [string]$Distro = 'Ubuntu',
    [switch]$SkipTests,
    [switch]$SkipLint,
    [switch]$Offline,
    [switch]$ReuseNative
)
$ErrorActionPreference = 'Stop'
$WiseMessageRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$BuildScript = Join-Path $WiseMessageRoot 'android\build-tools\build_android.py'
if (-not (Test-Path -LiteralPath $BuildScript -PathType Leaf)) { throw 'The copied Android build script is missing.' }
$LinuxScript = (& wsl.exe -d $Distro --exec wslpath -a -u $BuildScript).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve the Android build script in WSL.' }
$BuildArguments = @('-d', $Distro, '--exec')
if ($env:WISEMESSAGE_SIGNING_DIR) {
    if ($env:WISEMESSAGE_SIGNING_DIR.StartsWith('/')) {
        $LinuxSigningDirectory = $env:WISEMESSAGE_SIGNING_DIR
    } else {
        $PrivateSigningDirectory = (Resolve-Path -LiteralPath $env:WISEMESSAGE_SIGNING_DIR).Path
        if (-not (Test-Path -LiteralPath $PrivateSigningDirectory -PathType Container)) { throw 'The private signing directory is missing.' }
        $LinuxSigningDirectory = (& wsl.exe -d $Distro --exec wslpath -a -u $PrivateSigningDirectory).Trim()
        if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve the private signing directory in WSL.' }
    }
    $BuildArguments += @('/usr/bin/env', "WISEMESSAGE_SIGNING_DIR=$LinuxSigningDirectory")
}
$BuildArguments += @('python3', $LinuxScript)
if ($SkipTests) { $BuildArguments += '--skip-tests' }
if ($SkipLint) { $BuildArguments += '--skip-lint' }
if ($Offline) { $BuildArguments += '--offline' }
if ($ReuseNative) { $BuildArguments += '--reuse-native' }
& wsl.exe @BuildArguments
if ($LASTEXITCODE -ne 0) { throw "WiseMessage Android build failed with exit code $LASTEXITCODE. Logs are preserved in artifacts\android\builds." }
