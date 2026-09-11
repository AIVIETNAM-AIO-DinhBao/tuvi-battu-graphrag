param([switch]$Resume)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Summary = Join-Path $RepoRoot 'benchmark\tuvi_golden_dataset\sequential_ablation\gold_span_anchor_summary.json'
if (-not (Test-Path -LiteralPath $Summary)) { throw 'Gold-span anchors are missing. Run build_gold_anchors.ps1 first.' }
$AnchorSummary = Get-Content -LiteralPath $Summary -Raw | ConvertFrom-Json
if (-not $AnchorSummary.ready_for_official_run) { throw 'Gold-span anchor gate is not ready.' }

$Python = Join-Path $RepoRoot '.venv\Scripts\python.exe'
Push-Location $RepoRoot
try {
    $env:PYTHONPATH = 'backend'
    & $Python 'scripts\check_sequential_preflight.py'
    if ($LASTEXITCODE -ne 0) { throw "P1 preflight failed with exit code $LASTEXITCODE" }
}
finally {
    Pop-Location
}

$Runner = Join-Path $PSScriptRoot 'run_retrieval_phase.ps1'
& $Runner `
    -Manifest 'configs\ablation_sequential\p1_chunking.yaml' `
    -OutputDir 'benchmark\tuvi_golden_dataset\sequential_ablation\results\P1_chunking' `
    -CheckpointDir 'benchmark\tuvi_golden_dataset\sequential_ablation\results\P1_chunking\checkpoints' `
    -Resume:$Resume
