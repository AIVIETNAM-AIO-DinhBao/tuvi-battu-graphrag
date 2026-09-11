param(
    [Parameter(Mandatory = $true)][string]$Manifest,
    [Parameter(Mandatory = $true)][string]$FrozenBundle,
    [Parameter(Mandatory = $true)][string]$OutputDir,
    [Parameter(Mandatory = $true)][string]$CheckpointDir,
    [switch]$Resume
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Python = Join-Path $RepoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw "Missing Python environment: $Python" }

$Arguments = @(
    'scripts\run_eval.py',
    '--manifest', $Manifest,
    '--frozen-retrieval-bundle', $FrozenBundle,
    '--judge-backend', 'gemini',
    '--judge-protocol', 'blind-v2',
    '--gold-anchors', 'benchmark\tuvi_golden_dataset\sequential_ablation\gold_span_anchors.jsonl',
    '--skip-persistence',
    '--output-dir', $OutputDir,
    '--checkpoint-dir', $CheckpointDir,
    '--max-item-attempts', '2',
    '--retry-base-seconds', '2'
)
if ($Resume) { $Arguments += @('--resume', '--retry-failed') }

Push-Location $RepoRoot
try {
    $env:PYTHONPATH = 'backend'
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) { throw "P3 frozen prompt phase failed with exit code $LASTEXITCODE" }
}
finally {
    Pop-Location
}
