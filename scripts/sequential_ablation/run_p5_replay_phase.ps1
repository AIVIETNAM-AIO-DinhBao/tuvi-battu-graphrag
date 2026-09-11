param(
    [Parameter(Mandatory = $true)][string]$Manifest,
    [Parameter(Mandatory = $true)][string]$Bundle,
    [Parameter(Mandatory = $true)][string]$OutputDir
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Python = Join-Path $RepoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw "Missing Python environment: $Python" }

Push-Location $RepoRoot
try {
    $env:PYTHONPATH = 'backend'
    & $Python 'scripts\run_p5_replay_eval.py' `
        '--manifest' $Manifest `
        '--bundle' $Bundle `
        '--anchors' 'benchmark\tuvi_golden_dataset\sequential_ablation\gold_span_anchors.jsonl' `
        '--output-dir' $OutputDir
    if ($LASTEXITCODE -ne 0) { throw "P5 replay failed with exit code $LASTEXITCODE" }
}
finally {
    Pop-Location
}
