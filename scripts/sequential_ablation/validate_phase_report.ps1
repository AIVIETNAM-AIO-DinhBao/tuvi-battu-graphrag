param(
    [Parameter(Mandatory = $true)][string]$ReportPath,
    [Parameter(Mandatory = $true)][int]$ExpectedConfigs,
    [Parameter(Mandatory = $true)][int]$ExpectedPairs,
    [Parameter(Mandatory = $true)][ValidateSet('rule-based-gold-evidence-v1', 'rule-based-token-overlap-v2', 'gemini')][string]$Backend
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $ReportPath)) { throw "Missing report: $ReportPath" }
$Report = Get-Content -LiteralPath $ReportPath -Raw | ConvertFrom-Json
if ($Report.status -ne 'completed') { throw "Report status is $($Report.status), expected completed" }
if ($Report.config_count -ne $ExpectedConfigs) { throw "Config count is $($Report.config_count), expected $ExpectedConfigs" }
if ($Report.dataset_item_count -ne 100) { throw "Dataset item count is $($Report.dataset_item_count), expected 100" }
if ($Report.judge_backend -ne $Backend) { throw "Backend is $($Report.judge_backend), expected $Backend" }
if ($Report.execution_summary.completed_pair_count -ne $ExpectedPairs) {
    throw "Completed pairs is $($Report.execution_summary.completed_pair_count), expected $ExpectedPairs"
}
if ($Report.execution_summary.failed_pair_count -ne 0) {
    throw "Report has $($Report.execution_summary.failed_pair_count) failed pair(s)"
}
if (@($Report.configs | Where-Object status -ne 'completed').Count -ne 0) { throw 'At least one config is incomplete.' }
Write-Host "PASS: $ExpectedPairs pairs, $ExpectedConfigs configs, backend=$Backend"
