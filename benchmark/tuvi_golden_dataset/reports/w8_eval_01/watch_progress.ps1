param(
    [int]$RefreshSeconds = 15,
    [switch]$Once
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunDir = Join-Path $Root "production_full100"
$SummaryPath = Join-Path $RunDir "checkpoint\checkpoint_summary.json"
$ProcessPath = Join-Path $RunDir "process.json"
$ReportPath = Join-Path $RunDir "evaluation_report.json"
$ExitPath = Join-Path $RunDir "exit_code.txt"

do {
    Clear-Host
    Write-Host "W8-EVAL-01 full-100 progress" -ForegroundColor Cyan
    Write-Host "Time: $((Get-Date).ToString('o'))"
    Write-Host "Summary: $SummaryPath"

    $processMeta = $null
    if (Test-Path $ProcessPath) {
        try { $processMeta = Get-Content $ProcessPath -Raw | ConvertFrom-Json } catch {}
    }
    $running = $false
    if ($processMeta -and $processMeta.pid) {
        $running = [bool](Get-Process -Id $processMeta.pid -ErrorAction SilentlyContinue)
    }
    Write-Host "Process PID: $($processMeta.pid) | running: $running"

    if (Test-Path $SummaryPath) {
        try {
            $s = Get-Content $SummaryPath -Raw | ConvertFrom-Json
            $percent = if ($s.expected_pair_count) {
                [math]::Round(100 * $s.processed_pair_count / $s.expected_pair_count, 1)
            } else { 0 }
            Write-Host "Progress: $($s.processed_pair_count)/$($s.expected_pair_count) ($percent%)" -ForegroundColor Green
            Write-Host "Current item: $($s.current_item)"
            Write-Host "Executed: $($s.executed_pair_count) | Resumed: $($s.resumed_pair_count) | Failed: $($s.failed_pair_count)"
            Write-Host "Remaining: $($s.remaining_pair_count) | Updated UTC: $($s.updated_at)"
        } catch {
            Write-Host "Checkpoint summary is being atomically replaced; retry on next refresh." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Checkpoint summary not created yet." -ForegroundColor Yellow
    }

    Write-Host "Final report exists: $(Test-Path $ReportPath)"
    if (Test-Path $ReportPath) {
        try {
            $report = Get-Content $ReportPath -Raw | ConvertFrom-Json
            Write-Host "Canonical report status: $($report.status)" -ForegroundColor Green
            $execution = $report.execution_summary
            Write-Host "Canonical completion: $($execution.completed_pair_count)/$($execution.expected_pair_count), failed=$($execution.failed_pair_count)"
        } catch {
            Write-Host "Final report exists but could not be parsed on this refresh." -ForegroundColor Yellow
        }
    }
    if (Test-Path $ExitPath) {
        $exitText = (Get-Content $ExitPath -Raw).Trim()
        if ($exitText) {
            Write-Host "Worker-recorded exit code: $exitText"
        } else {
            Write-Host "Worker-recorded exit code unavailable; use canonical report and resume verification." -ForegroundColor Yellow
        }
    }
    Write-Host ""
    Write-Host "Press Ctrl+C to stop watching; this does not stop the benchmark."
    if (-not $Once) { Start-Sleep -Seconds $RefreshSeconds }
} while (-not $Once)