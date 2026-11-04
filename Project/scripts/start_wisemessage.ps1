<#
Start a separate WiseMessage run in the verified WSL MindSpore environment.
Prior run directories and model artifacts are preserved.
Example: .\scripts\start_wisemessage.ps1 -BudgetMinutes 45
#>
[CmdletBinding()]
param(
    [string]$RunDir = '',
    [ValidateRange(10, 90)][int]$BudgetMinutes = 45,
    [string]$DataDir = 'data\prepared',
    [string]$InitModelDir = '',
    [ValidateRange(1, 12)][int]$Epochs = 6,
    [ValidateScript({ $_ -gt 0 -and $_ -le 0.001 })][double]$LearningRate = 0.00005,
    [string]$WslPython = $env:WISEMESSAGE_WSL_PYTHON,
    [string]$WslDistribution = $env:WISEMESSAGE_WSL_DISTRIBUTION,
    [switch]$NoMonitor
)

$ErrorActionPreference = 'Stop'
$projectPath = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
if ([string]::IsNullOrWhiteSpace($WslPython)) {
    $WslPython = '/home/victor/.venvs/urlbert-ms/bin/python'
}
if ([string]::IsNullOrWhiteSpace($WslDistribution)) {
    $WslDistribution = 'Ubuntu'
}
if (-not $WslPython.StartsWith('/') -or $WslPython.Contains([char]0)) {
    throw 'WslPython must be an absolute Linux path to the Python interpreter inside WSL.'
}
$monitorPath = Join-Path $PSScriptRoot 'watch_wisemessage_window.ps1'

function Convert-WiseMessageWslPath([string]$WindowsPath) {
    if ($WindowsPath -notmatch '^([A-Za-z]):[\\/](.*)$') {
        throw "The WSL launcher requires a local Windows drive path: $WindowsPath"
    }
    return '/mnt/' + $Matches[1].ToLowerInvariant() + '/' + $Matches[2].Replace('\', '/')
}
function Resolve-WiseMessageInputDirectory([string]$Path, [string]$Label) {
    $resolved = if ([System.IO.Path]::IsPathRooted($Path)) {
        [System.IO.Path]::GetFullPath($Path)
    } else {
        [System.IO.Path]::GetFullPath((Join-Path $projectPath $Path))
    }
    $prefix = $projectPath.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if (-not $resolved.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label must be a directory inside the WiseMessage workspace."
    }
    if (-not (Test-Path -LiteralPath $resolved -PathType Container)) {
        throw "$Label does not exist: $resolved"
    }
    $item = Get-Item -LiteralPath $resolved -Force
    while ($item.FullName -ne $projectPath -and $item.Parent) {
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            throw "$Label cannot traverse a junction or symbolic link outside the checked workspace paths."
        }
        $item = $item.Parent
    }
    return $resolved
}

if ([string]::IsNullOrWhiteSpace($RunDir)) {
    $stamp = [DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyyMMdd_HHmmss')
    $RunDir = 'artifacts\runs\wisemessage_' + $stamp
}
$windowsRunPath = if ([System.IO.Path]::IsPathRooted($RunDir)) {
    [System.IO.Path]::GetFullPath($RunDir)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $projectPath $RunDir))
}
$projectPrefix = $projectPath.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
if (-not $windowsRunPath.StartsWith($projectPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'RunDir must be a new directory inside the WiseMessage workspace.'
}
if (Test-Path -LiteralPath $windowsRunPath) {
    if (-not (Test-Path -LiteralPath $windowsRunPath -PathType Container)) {
        throw "RunDir points to a file: $windowsRunPath"
    }
    if (Get-ChildItem -LiteralPath $windowsRunPath -Force | Select-Object -First 1) {
        throw "RunDir already contains files. Select a new directory to preserve existing runs: $windowsRunPath"
    }
}
if (-not $NoMonitor -and -not (Test-Path -LiteralPath $monitorPath -PathType Leaf)) {
    throw "Live monitor script is missing: $monitorPath"
}
if (-not (Get-Command 'wsl.exe' -ErrorAction SilentlyContinue)) {
    throw 'WSL is unavailable. This launcher uses the existing Ubuntu MindSpore environment.'
}

$linuxProjectPath = Convert-WiseMessageWslPath $projectPath
$linuxRunPath = Convert-WiseMessageWslPath $windowsRunPath
$windowsDataPath = Resolve-WiseMessageInputDirectory $DataDir 'DataDir'
$linuxDataPath = Convert-WiseMessageWslPath $windowsDataPath
$launchArgs = @('-d', $WslDistribution, '--cd', $linuxProjectPath, '--', $WslPython,
                '-m', 'wisemessage.workflow', '--background',
                '--budget-minutes', [string]$BudgetMinutes, '--run-dir', $linuxRunPath,
                '--data-dir', $linuxDataPath, '--epochs', [string]$Epochs,
                '--learning-rate', $LearningRate.ToString('R', [System.Globalization.CultureInfo]::InvariantCulture))
if (-not [string]::IsNullOrWhiteSpace($InitModelDir)) {
    $windowsInitPath = Resolve-WiseMessageInputDirectory $InitModelDir 'InitModelDir'
    $launchArgs += @('--init-model-dir', (Convert-WiseMessageWslPath $windowsInitPath))
}

Write-Host ('Starting WiseMessage with a {0}-minute training budget.' -f $BudgetMinutes)
Write-Host ('Run: {0}' -f $windowsRunPath)
& wsl.exe @launchArgs
if ($LASTEXITCODE -ne 0) {
    throw 'The WiseMessage workflow could not start. Existing files have been preserved.'
}
if (-not $NoMonitor) {
    $monitorArgs = @('-NoProfile', '-STA', '-ExecutionPolicy', 'Bypass',
                     '-File', ('"{0}"' -f $monitorPath),
                     '-RunDir', ('"{0}"' -f $windowsRunPath))
    Start-Process -FilePath 'powershell.exe' -ArgumentList $monitorArgs `
        -WorkingDirectory $projectPath -WindowStyle Hidden | Out-Null
    Write-Host 'The live monitor is open. Closing it does not stop training.'
}
