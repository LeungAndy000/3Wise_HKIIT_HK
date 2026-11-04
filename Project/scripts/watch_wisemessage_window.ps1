[CmdletBinding()]
param(
    [string]$RunDir = 'artifacts\runs\domain_v2_20261023_1050',
    [ValidateRange(1, 3600)][int]$RefreshSeconds = 3
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class WiseMessageMonitorWindow {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr window, int command);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr window);
}
'@
[System.Windows.Forms.Application]::EnableVisualStyles()
$renderer = Join-Path $PSScriptRoot 'watch_wisemessage.ps1'
if (-not (Test-Path -LiteralPath $renderer -PathType Leaf)) { throw 'The read-only status renderer is missing.' }

$form = New-Object System.Windows.Forms.Form
$form.Text = 'WiseMessage Live Training Monitor'
$form.Size = New-Object System.Drawing.Size(1250, 850)
$form.MinimumSize = New-Object System.Drawing.Size(850, 450)
$form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
$form.ShowInTaskbar = $true

$display = New-Object System.Windows.Forms.TextBox
$display.Multiline = $true
$display.ReadOnly = $true
$display.WordWrap = $false
$display.ScrollBars = [System.Windows.Forms.ScrollBars]::Both
$display.Dock = [System.Windows.Forms.DockStyle]::Fill
$display.BackColor = [System.Drawing.Color]::FromArgb(20, 25, 34)
$display.ForeColor = [System.Drawing.Color]::FromArgb(230, 237, 243)
$display.Font = New-Object System.Drawing.Font('Consolas', 10)
$display.AccessibleName = 'Live training progress and validation results'
$form.Controls.Add($display)

$refresh = {
    try {
        $rendered = (& $renderer -RunDir $RunDir -Once *>&1 | Out-String).TrimEnd()
        if ($display.Text -ne $rendered) {
            $display.Text = $rendered
            $display.SelectionStart = 0
            $display.SelectionLength = 0
            $display.ScrollToCaret()
        }
    } catch {
        $display.Text = "WiseMessage monitor could not read the current status.`r`n" + $_.Exception.Message + "`r`nClosing this window does not stop training."
    }
}
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = $RefreshSeconds * 1000
$timer.Add_Tick($refresh)
$form.Add_Shown({
    & $refresh
    $timer.Start()
    [WiseMessageMonitorWindow]::ShowWindow($form.Handle, 9) | Out-Null
    [WiseMessageMonitorWindow]::SetForegroundWindow($form.Handle) | Out-Null
    $form.Activate()
    $form.BringToFront()
})
$form.Add_FormClosed({ $timer.Stop(); $timer.Dispose() })
try { [System.Windows.Forms.Application]::Run($form) }
finally { $display.Font.Dispose(); $form.Dispose() }
