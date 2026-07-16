$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
$RunDir = Join-Path $PSScriptRoot "production_full100"
$CheckpointDir = Join-Path $RunDir "checkpoint"
$SummaryPath = Join-Path $CheckpointDir "checkpoint_summary.json"
$ProcessPath = Join-Path $RunDir "process.json"
$MonitorPath = Join-Path $RunDir "monitor_status.json"
$ExitPath = Join-Path $RunDir "exit_code.txt"
$StdoutPath = Join-Path $RunDir "stdout.log"
$StderrPath = Join-Path $RunDir "stderr.log"
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"

New-Item -ItemType Directory -Force -Path $CheckpointDir | Out-Null
Remove-Item $ExitPath -Force -ErrorAction SilentlyContinue
$env:PYTHONPATH = "backend"

$arguments = @(
    "scripts/run_eval.py",
    "--config", "configs/default_production.yaml",
    "--dataset", "benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl",
    "--judge-backend", "gemini",
    "--judge-model", "gemini-3.1-flash-lite-preview",
    "--skip-persistence",
    "--checkpoint-dir", "benchmark/tuvi_golden_dataset/reports/w8_eval_01/production_full100/checkpoint",
    "--output-dir", "benchmark/tuvi_golden_dataset/reports/w8_eval_01/production_full100",
    "--max-item-attempts", "2",
    "--retry-base-seconds", "2"
)

$startedAt = (Get-Date).ToUniversalTime().ToString("o")
$evaluator = Start-Process -FilePath $Python `
    -ArgumentList $arguments `
    -WorkingDirectory $RepoRoot `
    -RedirectStandardOutput $StdoutPath `
    -RedirectStandardError $StderrPath `
    -PassThru

[ordered]@{
    worker_pid = $PID
    pid = $evaluator.Id
    started_at = $startedAt
    status = "running"
    command = "scripts/run_eval.py --config configs/default_production.yaml --dataset [release] --judge-backend gemini --skip-persistence --checkpoint-dir [full100/checkpoint] --output-dir [full100] --max-item-attempts 2 --retry-base-seconds 2"
} | ConvertTo-Json | Set-Content -Encoding utf8 $ProcessPath

while (-not $evaluator.HasExited) {
    $checkpoint = $null
    if (Test-Path $SummaryPath) {
        try { $checkpoint = Get-Content $SummaryPath -Raw | ConvertFrom-Json } catch {}
    }
    [ordered]@{
        status = "running"
        worker_pid = $PID
        evaluator_pid = $evaluator.Id
        heartbeat_at = (Get-Date).ToUniversalTime().ToString("o")
        checkpoint = $checkpoint
    } | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 "$MonitorPath.tmp"
    Move-Item -Force "$MonitorPath.tmp" $MonitorPath
    Start-Sleep -Seconds 15
    $evaluator.Refresh()
}

$evaluator.WaitForExit()
$exitCode = $evaluator.ExitCode
Set-Content -Encoding ascii $ExitPath "$exitCode"

$finalCheckpoint = $null
if (Test-Path $SummaryPath) {
    try { $finalCheckpoint = Get-Content $SummaryPath -Raw | ConvertFrom-Json } catch {}
}
[ordered]@{
    status = if ($exitCode -eq 0) { "completed" } else { "failed" }
    worker_pid = $PID
    evaluator_pid = $evaluator.Id
    heartbeat_at = (Get-Date).ToUniversalTime().ToString("o")
    exit_code = $exitCode
    checkpoint = $finalCheckpoint
} | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 "$MonitorPath.tmp"
Move-Item -Force "$MonitorPath.tmp" $MonitorPath

$processData = Get-Content $ProcessPath -Raw | ConvertFrom-Json
$processData.status = if ($exitCode -eq 0) { "completed" } else { "failed" }
$processData | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 $ProcessPath

exit $exitCode