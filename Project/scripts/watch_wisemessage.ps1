[CmdletBinding()]
param(
    [string]$RunDir = 'artifacts\runs\domain_v2_20261023_1050',
    [ValidateRange(1, 3600)][int]$RefreshSeconds = 3,
    [switch]$Once
)

$ErrorActionPreference = 'Stop'
$projectPath = Split-Path -Parent $PSScriptRoot
if (-not [System.IO.Path]::IsPathRooted($RunDir)) { $RunDir = Join-Path $projectPath $RunDir }
$runPath = [System.IO.Path]::GetFullPath($RunDir)

function Get-WMValue($Object, [string[]]$Names) {
    if ($null -eq $Object) { return $null }
    foreach ($name in $Names) {
        $property = $Object.PSObject.Properties[$name]
        if ($null -ne $property -and $null -ne $property.Value) { return $property.Value }
    }
    return $null
}
function Read-WMJson([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try { return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json } catch { return $null }
}
function Format-WMDuration($Seconds) {
    if ($null -eq $Seconds) { return 'pending' }
    $span = [TimeSpan]::FromSeconds([math]::Max(0, [double]$Seconds))
    return ('{0:00}:{1:00}:{2:00}' -f [math]::Floor($span.TotalHours), $span.Minutes, $span.Seconds)
}
function Write-WMMetrics($Object, [string]$Label, [switch]$Binary) {
    if ($null -eq $Object) { return }
    $nested = Get-WMValue $Object @('metrics', 'validation_metrics')
    if ($nested) { $Object = $nested }
    $parts = @()
    $sampleCount = Get-WMValue $Object @('samples')
    if ($null -ne $sampleCount) { $parts += ('n={0:N0}' -f [double]$sampleCount) }
    $presentClasses = Get-WMValue $Object @('present_classes')
    $macroMetric = if ($presentClasses -and @($presentClasses).Count -lt 3 -and $null -ne (Get-WMValue $Object @('macro_f1_present_classes'))) {
        @('macro_f1_present_classes', 'present-class macro F1')
    } else { @('macro_f1', 'macro F1') }
    $metricNames = if ($Binary) {
        @(@('f1', 'unwanted F1'), @('recall', 'unwanted recall'), @('accuracy', 'accuracy'), @('false_positive_rate', 'normal FPR'))
    } else {
        @($macroMetric, @('accuracy', 'accuracy'), @('scam_recall', 'scam recall'), @('normal_false_positive_rate', 'normal FPR'))
    }
    foreach ($metric in $metricNames) {
        $value = Get-WMValue $Object @($metric[0])
        if ($null -ne $value) { $parts += ('{0} {1:P2}' -f $metric[1], [double]$value) }
    }
    $classes = Get-WMValue $Object @('per_class', 'classes')
    foreach ($name in @('normal', 'spam', 'scam')) {
        $detail = Get-WMValue $classes @($name)
        $support = Get-WMValue $detail @('support')
        if ($null -ne $support -and [double]$support -eq 0) { continue }
        $f1 = Get-WMValue $detail @('f1')
        $recall = Get-WMValue $detail @('recall')
        if ($null -ne $f1) { $parts += ('{0} F1 {1:P2}' -f $name, [double]$f1) }
        if ($name -eq 'scam' -and $null -ne $recall -and $null -eq (Get-WMValue $Object @('scam_recall'))) {
            $parts += ('scam recall {0:P2}' -f [double]$recall)
        }
    }
    if ($parts.Count) { Write-Host ('{0}: {1}' -f $Label, ($parts -join ' | ')) }
}
function Write-WMValidation($Object, [string]$Label) {
    if ($null -eq $Object) { return }
    $metrics = Get-WMValue $Object @('metrics', 'validation_metrics')
    if (-not $metrics) { $metrics = $Object }
    $presentClasses = Get-WMValue $metrics @('present_classes')
    $classDescription = if ($presentClasses -and @($presentClasses).Count -lt 3) {
        'fully labelled: ' + ($presentClasses -join ', ')
    } else { '3-class, fully labelled only' }
    Write-WMMetrics $Object ($Label + ' (' + $classDescription + ')')
    $binaryAll = Get-WMValue $metrics @('binary_unwanted', 'binary_validation', 'binary_validation_metrics')
    $binaryPartial = Get-WMValue $metrics @('partial_binary', 'partial_binary_validation')
    if ($binaryAll) { Write-WMMetrics $binaryAll ($Label + ' (all messages, normal vs unwanted)') -Binary }
    if ($binaryPartial) { Write-WMMetrics $binaryPartial ($Label + ' (normal + partially labelled unwanted)') -Binary }
    $partialCount = Get-WMValue $metrics @('partial_label_samples')
    if ($null -ne $partialCount -and [double]$partialCount -gt 0) {
        Write-Host ('  Partial-label messages: {0:N0}; their spam/scam subtype is unknown and excluded from 3-class metrics.' -f [double]$partialCount)
    }
    $jointPassed = Get-WMValue $metrics @('quality_requirements_passed')
    if ($null -ne $jointPassed) { Write-Host ('  Validation joint internal criteria passed: {0}' -f $jointPassed) }
}
function Test-WMBinaryCriteria($Object) {
    if ($null -eq $Object) { return $null }
    $metrics = Get-WMValue $Object @('metrics')
    if ($metrics) { $Object = $metrics }
    $f1 = Get-WMValue $Object @('f1')
    $recall = Get-WMValue $Object @('recall')
    $fpr = Get-WMValue $Object @('false_positive_rate')
    if ($null -eq $f1 -or $null -eq $recall -or $null -eq $fpr) { return $null }
    return ([double]$f1 -ge 0.8 -and [double]$recall -ge 0.8 -and [double]$fpr -le 0.1)
}
function Format-WMLog([string]$Line) {
    $display = $Line.Trim()
    if ($display.StartsWith('{')) {
        try {
            $entry = $display | ConvertFrom-Json
            $parts = @()
            foreach ($name in @('status', 'phase', 'split', 'epoch', 'global_step', 'rows_completed', 'total_rows', 'loss', 'message', 'error')) {
                $value = Get-WMValue $entry @($name)
                if ($null -ne $value) { $parts += ('{0}={1}' -f $name, $value) }
            }
            if ($parts.Count) { $display = $parts -join ' ' }
        } catch { }
    }
    if ($display.Length -gt 250) { $display = $display.Substring(0, 247) + '...' }
    return $display
}

do {
    $snapshot = Read-WMJson (Join-Path $runPath 'status.json')
    if ($null -eq $snapshot) { $snapshot = [pscustomobject]@{ status = 'waiting'; phase = 'waiting_for_workflow' } }
    $progress = Get-WMValue $snapshot @('progress')
    if (-not $progress) { $progress = $snapshot }
    $status = Get-WMValue $snapshot @('status')
    if ($status -eq 'running') {
        foreach ($fileName in @('training_status.json', 'evaluation_status.json')) {
            $direct = Read-WMJson (Join-Path $runPath $fileName)
            $stamp = Get-WMValue $direct @('updated_at')
            $previousStamp = Get-WMValue $progress @('updated_at')
            if ($stamp) {
                try {
                    if (-not $previousStamp -or [DateTimeOffset]::Parse($stamp) -gt [DateTimeOffset]::Parse($previousStamp)) {
                        $progress = $direct
                    }
                } catch { }
            }
        }
    }
    $phase = Get-WMValue $progress @('phase', 'stage')
    if (-not $phase) { $phase = Get-WMValue $snapshot @('phase', 'stage') }
    if ($status -in @('completed', 'failed', 'interrupted', 'deadline_reached')) { $phase = Get-WMValue $snapshot @('phase', 'stage') }
    if (-not $Once) { Clear-Host }
    Write-Host 'WiseMessage - Chinese SMS training and validation' -ForegroundColor Cyan
    Write-Host 'Native MindSpore | MiniRBT | normal / spam / scam'
    Write-Host 'Read only. Closing this window does not stop the workflow.'
    Write-Host ('Status: {0} | Phase: {1}' -f $status, $phase) -ForegroundColor Yellow
    $description = Get-WMValue $snapshot @('message', 'stage_description', 'description')
    if ($description) { Write-Host $description }
    $model = Get-WMValue $snapshot @('model_name', 'model_id', 'pretrained_model')
    if ($model) { Write-Host ('Model: {0}' -f $model) }
    $epoch = Get-WMValue $progress @('epoch')
    if ($null -ne $epoch) { Write-Host ('Epoch: {0} / {1}' -f $epoch, (Get-WMValue $progress @('epochs', 'max_epochs'))) }
    $split = Get-WMValue $progress @('split', 'script')
    if ($split) { Write-Host ('Split / script: {0}' -f $split) }
    if ($phase -match 'validat|evaluat|prepar|tokeniz') {
        $done = Get-WMValue $progress @('rows_completed', 'completed_rows', 'downloaded_bytes')
        $total = Get-WMValue $progress @('total_rows', 'rows_total', 'total_bytes')
        $progressLabel = 'Split progress'
    } else {
        $done = Get-WMValue $progress @('global_step', 'rows_completed', 'completed_rows', 'step', 'downloaded_bytes')
        $total = Get-WMValue $progress @('total_steps', 'total_rows', 'rows_total', 'steps', 'total_bytes')
        $progressLabel = 'Optimizer updates'
        if ($phase -eq 'training_completed') {
            $completedTrainingResult = Get-WMValue $progress @('result')
            if (-not $completedTrainingResult) { $completedTrainingResult = Read-WMJson (Join-Path $runPath 'training_result.json') }
            $completedUpdates = Get-WMValue $completedTrainingResult @('global_steps_completed')
            if ($null -ne $completedUpdates) { $done = $completedUpdates }
        }
    }
    if ($null -ne $done) {
        if ($null -ne $total -and [double]$total -gt 0) { Write-Host ('{0}: {1:N0} / {2:N0} ({3:P1})' -f $progressLabel, [double]$done, [double]$total, ([double]$done / [double]$total)) }
        else { Write-Host ('{0}: {1:N0}' -f $progressLabel, [double]$done) }
    }
    $examplesSeen = Get-WMValue $progress @('examples_seen')
    if ($null -ne $examplesSeen) {
        Write-Host ('Training examples seen across epochs: {0:N0}' -f [double]$examplesSeen)
        $epochs = Get-WMValue $progress @('epochs', 'max_epochs')
        $trainingRows = Get-WMValue $progress @('total_rows')
        if ($phase -eq 'training' -and $null -ne $epoch -and $epochs -and $trainingRows) {
            $rowsPerEpoch = [double]$trainingRows / [double]$epochs
            $currentEpochRows = [math]::Max(0, [double]$examplesSeen - ([double]$epoch - 1) * $rowsPerEpoch)
            Write-Host ('Current epoch coverage: {0:N0} / {1:N0} ({2:P1})' -f $currentEpochRows, $rowsPerEpoch, ($currentEpochRows / $rowsPerEpoch))
        }
    }
    $loss = Get-WMValue $progress @('loss', 'train_loss')
    if ($null -ne $loss) { Write-Host ('Loss: {0:F6}' -f [double]$loss) }
    $batch = Get-WMValue $progress @('batch_size')
    if ($null -ne $batch) { Write-Host ('Batch size: {0}' -f $batch) }
    $rate = Get-WMValue $progress @('samples_per_second', 'rows_per_second', 'messages_per_second')
    if ($null -ne $rate) { Write-Host ('Speed: {0:N1} messages/s' -f [double]$rate) }
    $elapsed = Get-WMValue $snapshot @('elapsed_seconds')
    $stageElapsed = Get-WMValue $progress @('elapsed_seconds')
    if ($null -eq $elapsed) { $elapsed = $stageElapsed }
    $eta = Get-WMValue $progress @('eta_seconds', 'remaining_seconds')
    Write-Host ('Workflow elapsed: {0} | Current stage elapsed: {1} | Estimated remaining: {2}' -f (Format-WMDuration $elapsed), (Format-WMDuration $stageElapsed), (Format-WMDuration $eta))
    $gpu = Get-WMValue $snapshot @('gpu')
    if ($gpu) { Write-Host ('GPU: {0}' -f ($gpu | ConvertTo-Json -Compress -Depth 4)) }
    $currentMetricLabel = if ($phase -match 'evaluat|^completed$') { 'Latest test evaluation' } else { 'Latest validation' }
    Write-WMValidation (Get-WMValue $progress @('validation_metrics', 'validation', 'metrics')) $currentMetricLabel
    Write-WMMetrics (Get-WMValue $progress @('binary_validation', 'binary_validation_metrics')) 'Latest binary validation (normal vs unwanted)' -Binary
    $results = Get-WMValue $snapshot @('results', 'evaluation')
    $trainingResult = Get-WMValue $results @('training')
    if ($trainingResult) {
        $completedUpdates = Get-WMValue $trainingResult @('global_steps_completed')
        if ($null -ne $completedUpdates) {
            Write-Host ('Training completed: {0:N0} optimizer updates across {1} epochs' -f [double]$completedUpdates, (Get-WMValue $trainingResult @('epochs_completed')))
        }
        Write-WMValidation (Get-WMValue $trainingResult @('validation')) 'Selected checkpoint validation'
    }
    $evaluationResult = Get-WMValue $results @('evaluation')
    $nestedReport = Get-WMValue $evaluationResult @('report', 'performance')
    if ($nestedReport) { $evaluationResult = $nestedReport }
    $datasets = Get-WMValue $evaluationResult @('datasets')
    if (-not $datasets) { $datasets = Get-WMValue $progress @('results') }
    if (-not $datasets) { $datasets = Get-WMValue $results @('datasets') }
    if (-not $datasets -and (Get-WMValue $results @('test'))) { $datasets = $results }
    if ($datasets) {
        Write-Host ''
        Write-Host 'Recorded evaluations:' -ForegroundColor Cyan
        Write-WMValidation (Get-WMValue $datasets @('test')) '  Held-out original messages'
        Write-WMValidation (Get-WMValue $datasets @('test_traditional_converted')) '  Traditional Chinese (script-converted paired test)'
        Write-WMMetrics (Get-WMValue $datasets @('binary_domain_test')) '  Domain-held-out SMS: normal vs unwanted (binary)' -Binary
        Write-WMValidation (Get-WMValue $datasets @('fgrc_test')) '  FGRC held-out labelled messages'
        Write-WMValidation (Get-WMValue $datasets @('fgrc_traditional_converted')) '  FGRC Traditional Chinese (script-converted paired test)'
        Write-WMMetrics (Get-WMValue $datasets @('external_mudou_binary')) '  External SMS: raw class decision, normal vs unwanted' -Binary
        $externalApplicationMetrics = Get-WMValue (Get-WMValue $datasets @('external_mudou_binary')) @('review_decision_metrics')
        if ($externalApplicationMetrics) {
            Write-WMMetrics $externalApplicationMetrics '  External SMS: application review decision, normal vs unwanted' -Binary
        }
        if (Get-WMValue $datasets @('test_traditional_converted')) {
            Write-Host '  Converted Traditional Chinese is a robustness test; native Traditional Chinese validation is pending.' -ForegroundColor Yellow
        }
        $externalMetrics = $null
        if (Get-WMValue $datasets @('external_mudou_binary')) {
            Write-Host '  External binary labels do not distinguish spam from scam.' -ForegroundColor Yellow
            $externalMetrics = if ($externalApplicationMetrics) { $externalApplicationMetrics } else { Get-WMValue (Get-WMValue $datasets @('external_mudou_binary')) @('metrics') }
            $externalRecall = Get-WMValue $externalMetrics @('recall')
            if ($null -ne $externalRecall -and [double]$externalRecall -lt 0.5) {
                Write-Host '  External unwanted-message recall is weak; internal scores do not establish deployment readiness.' -ForegroundColor Red
            }
        }
        $unreviewed = Get-WMValue $datasets @('external_unreviewed')
        if ($unreviewed) { Write-Host ('  Unlabelled external diagnostic: {0} messages; no accuracy measured.' -f (Get-WMValue $unreviewed @('samples'))) }
        $mainPassed = Get-WMValue $evaluationResult @('main_test_requirements_passed')
        $traditionalPassed = Get-WMValue $evaluationResult @('converted_traditional_requirements_passed')
        $internalPassed = if ($null -ne $mainPassed -and $null -ne $traditionalPassed) { [bool]$mainPassed -and [bool]$traditionalPassed } else { $null }
        $externalPassed = Test-WMBinaryCriteria $externalMetrics
        $supplementaryPassed = Get-WMValue $evaluationResult @('supplementary_requirements_passed')
        $supplementaryDatasetRequirements = Get-WMValue $evaluationResult @('supplementary_dataset_requirements')
        if ($null -ne $internalPassed) { Write-Host ('Internal held-out criteria passed: {0}' -f $internalPassed) }
        if ($null -ne $externalPassed) { Write-Host ('External binary criteria passed: {0} (F1 >= 80%, recall >= 80%, normal FPR <= 10%)' -f $externalPassed) }
        if ($null -ne $supplementaryPassed) { Write-Host ('Supplementary dataset criteria passed: {0}' -f $supplementaryPassed) }
        if ($supplementaryDatasetRequirements) {
            foreach ($property in $supplementaryDatasetRequirements.PSObject.Properties) {
                Write-Host ('  {0} criteria passed: {1}' -f $property.Name, $property.Value)
            }
        }
        if ($null -ne $internalPassed -and $null -ne $externalPassed) {
            $supplementaryQualified = $null -eq $supplementaryPassed -or [bool]$supplementaryPassed
            if ($internalPassed -and $externalPassed -and $supplementaryQualified) {
                Write-Host 'Overall dataset criteria: QUALIFIED; independent native Traditional Chinese validation remains pending.' -ForegroundColor Green
            } else {
                Write-Host 'Overall dataset criteria: NOT QUALIFIED; all internal, external and supplementary criteria must pass.' -ForegroundColor Red
            }
        }
    }
    if ($results -and @($results.PSObject.Properties).Count -gt 0 -and -not $datasets -and -not $trainingResult) {
        Write-Host ''
        Write-Host 'Recorded evaluations:' -ForegroundColor Cyan
        foreach ($property in $results.PSObject.Properties) {
            if ($property.Value -is [string] -or $property.Value -is [bool]) { Write-Host ('  {0}: {1}' -f $property.Name, $property.Value) }
            else { Write-WMMetrics $property.Value ('  ' + $property.Name) }
        }
    }
    foreach ($pair in @(@('simplified', 'Simplified Chinese'), @('traditional', 'Traditional Chinese'), @('test', 'Held-out test'), @('external_test', 'External test'))) {
        $metrics = Get-WMValue $snapshot @($pair[0])
        if ($metrics) { Write-WMMetrics $metrics $pair[1] }
    }
    $selected = Get-WMValue $snapshot @('model_dir', 'selected_model_dir')
    if ($selected) { Write-Host ('Model bundle: {0}' -f $selected) -ForegroundColor Green }
    $errorText = Get-WMValue $snapshot @('error')
    if (-not $errorText) { $errorText = Get-WMValue $progress @('error') }
    if ($errorText) { Write-Host ('Error: {0}' -f $errorText) -ForegroundColor Red }
    $updatedText = Get-WMValue $snapshot @('updated_at')
    if ($updatedText) {
        try {
            $updated = [DateTimeOffset]::Parse($updatedText)
            $age = [math]::Max(0, [int]([DateTimeOffset]::UtcNow - $updated).TotalSeconds)
            Write-Host ('Heartbeat: {0} HKT ({1}s ago)' -f $updated.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss'), $age)
        } catch { }
    }
    $workerUpdatedText = Get-WMValue $progress @('updated_at')
    if ($workerUpdatedText -and $workerUpdatedText -ne $updatedText) {
        try {
            $workerUpdated = [DateTimeOffset]::Parse($workerUpdatedText)
            $workerAge = [math]::Max(0, [int]([DateTimeOffset]::UtcNow - $workerUpdated).TotalSeconds)
            Write-Host ('Worker progress: {0} HKT ({1}s ago)' -f $workerUpdated.ToOffset([TimeSpan]::FromHours(8)).ToString('HH:mm:ss'), $workerAge)
        } catch { }
    }
    Write-Host ('Run: {0}' -f $runPath)
    $logDir = Join-Path $runPath 'logs'
    if (-not (Test-Path -LiteralPath $logDir -PathType Container)) { $logDir = $runPath }
    if (Test-Path -LiteralPath $logDir -PathType Container) {
        $latest = Get-ChildItem -LiteralPath $logDir -File -Filter '*.log' | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
        if ($latest) {
            Write-Host ('Recent log: {0}' -f $latest.Name)
            Get-Content -LiteralPath $latest.FullName -Tail 3 -Encoding UTF8 | ForEach-Object { Write-Host ('  ' + (Format-WMLog $_)) }
        }
    }
    if ($Once -or $status -in @('completed', 'failed', 'interrupted', 'deadline_reached')) { break }
    Start-Sleep -Seconds $RefreshSeconds
} while ($true)
