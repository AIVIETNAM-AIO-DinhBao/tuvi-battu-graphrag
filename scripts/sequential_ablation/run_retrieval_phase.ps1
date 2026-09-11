param(
    [Parameter(Mandatory = $true)][string]$Manifest,
    [Parameter(Mandatory = $true)][string]$OutputDir,
    [Parameter(Mandatory = $true)][string]$CheckpointDir,
    [switch]$Resume
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Python = Join-Path $RepoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw "Missing Python environment: $Python" }
$PreviousRerankTimeout = [Environment]::GetEnvironmentVariable('TUVI_RERANK_TIMEOUT_SECONDS', 'Process')

$Arguments = @(
    'scripts\run_retrieval_eval.py',
    '--manifest', $Manifest,
    '--anchors', 'benchmark\tuvi_golden_dataset\sequential_ablation\gold_span_anchors.jsonl',
    '--output-dir', $OutputDir,
    '--checkpoint-dir', $CheckpointDir,
    '--max-item-attempts', '2',
    '--retry-base-seconds', '2'
)
if ($Resume) { $Arguments += @('--resume', '--retry-failed') }

Push-Location $RepoRoot
try {
    $env:PYTHONPATH = 'backend'
    $env:TUVI_RERANK_TIMEOUT_SECONDS = '600'
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Retrieval phase failed with exit code $LASTEXITCODE" }
}
finally {
    if ($null -eq $PreviousRerankTimeout) {
        Remove-Item Env:TUVI_RERANK_TIMEOUT_SECONDS -ErrorAction SilentlyContinue
    }
    else {
        $env:TUVI_RERANK_TIMEOUT_SECONDS = $PreviousRerankTimeout
    }
    Pop-Location
}
