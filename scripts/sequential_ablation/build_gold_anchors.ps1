param()

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Python = Join-Path $RepoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw "Missing Python environment: $Python" }

Push-Location $RepoRoot
try {
    $env:PYTHONPATH = 'backend'
    & $Python 'benchmark\tuvi_golden_dataset\scripts\map_gold_spans_to_chunks.py' --min-mapping-coverage 0.80
    if ($LASTEXITCODE -ne 0) { throw "Gold anchor build failed with exit code $LASTEXITCODE" }
    & $Python -m pytest 'backend\tests\test_gold_evidence.py' -q -p no:cacheprovider
    if ($LASTEXITCODE -ne 0) { throw "Gold evidence tests failed with exit code $LASTEXITCODE" }
}
finally {
    Pop-Location
}
