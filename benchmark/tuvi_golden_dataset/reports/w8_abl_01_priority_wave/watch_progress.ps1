param([int]$RefreshSeconds = 15, [switch]$Once)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunDir = Join-Path $Root "full100"
$SummaryPath = Join-Path $RunDir "checkpoint\checkpoint_summary.json"
$ProcessPath = Join-Path $RunDir "process.json"
$MonitorPath = Join-Path $RunDir "monitor_status.json"
$ReportPath = Join-Path $RunDir "evaluation_report.json"
$ExitPath = Join-Path $RunDir "exit_code.txt"
$milestones = @(
    @{ End = 100; Name = "sparse_only_rrf" },
    @{ End = 200; Name = "dense_sparse_rrf" },
    @{ End = 300; Name = "baseline_no_reranker" },
    @{ End = 400; Name = "baseline_weighted_sum" }
)

do {
    Clear-Host
    Write-Host "W8-ABL-01 priority wave progress" -ForegroundColor Cyan
    Write-Host "Time: $((Get-Date).ToString('o'))"
    $meta = $null
    if (Test-Path $ProcessPath) { try { $meta = Get-Content $ProcessPath -Raw | ConvertFrom-Json } catch {} }
    $running = $false
    if ($meta -and $meta.pid) { $running = [bool](Get-Process -Id $meta.pid -ErrorAction SilentlyContinue) }
    Write-Host "Supervisor PID: $($meta.pid) | running: $running | status: $($meta.status)"

    if (Test-Path $SummaryPath) {
        try {
            $s = Get-Content $SummaryPath -Raw | ConvertFrom-Json
            $percent = [math]::Round(100 * $s.processed_pair_count / $s.expected_pair_count, 1)
            Write-Host "Progress: $($s.processed_pair_count)/$($s.expected_pair_count) ($percent%)" -ForegroundColor Green
            Write-Host "Current config: $($s.current_config) | item: $($s.current_item)"
            Write-Host "Executed: $($s.executed_pair_count) | Resumed: $($s.resumed_pair_count) | Failed: $($s.failed_pair_count)"
            Write-Host "Remaining: $($s.remaining_pair_count) | Updated UTC: $($s.updated_at)"
            foreach ($m in $milestones) {
                $state = if ($s.processed_pair_count -ge $m.End) { "DONE" } else { "pending" }
                Write-Host ("[{0}] {1} ({2}/400)" -f $state, $m.Name, $m.End)
            }
        } catch { Write-Host "Checkpoint is being atomically replaced; retrying." -ForegroundColor Yellow }
    } else { Write-Host "Checkpoint summary not created yet." -ForegroundColor Yellow }

    Write-Host "Heartbeat file: $(Test-Path $MonitorPath) | Final report: $(Test-Path $ReportPath)"
    if (Test-Path $ReportPath) {
        try {
            $r = Get-Content $ReportPath -Raw | ConvertFrom-Json
            Write-Host "Canonical report status: $($r.status); completed=$($r.execution_summary.completed_pair_count)/$($r.execution_summary.expected_pair_count); failed=$($r.execution_summary.failed_pair_count)" -ForegroundColor Green
        } catch {}
    }
    if (Test-Path $ExitPath) { Write-Host "Supervisor exit code: $((Get-Content $ExitPath -Raw).Trim())" }
    Write-Host "Press Ctrl+C to stop watching; this does not stop the benchmark."
    if (-not $Once) { Start-Sleep -Seconds $RefreshSeconds }
} while (-not $Once)