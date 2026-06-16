# Lasotuvi Installation Script for Windows PowerShell
#
# Usage:
#   cd tuvi-battu-graphrag\backend
#   .\setup_lasotuvi.ps1

$ErrorActionPreference = "Stop"

Write-Host "=============================================="
Write-Host "  Lasotuvi Installation Script (PowerShell)"
Write-Host "=============================================="
Write-Host ""

Write-Host "[1/4] Checking Python version..."
python --version

Write-Host ""
Write-Host "[2/4] Installing required dependencies..."
python -m pip install "ephem>=3.7.6.0" vnlunar
Write-Host "  Dependencies installed"

Write-Host ""
Write-Host "[3/4] Installing lasotuvi with --no-deps..."
$backendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Split-Path -Parent $backendDir
$workspaceDir = Split-Path -Parent $repoDir
$localLasotuvi = Join-Path $workspaceDir "lasotuvi"

if (Test-Path (Join-Path $localLasotuvi "setup.py")) {
    Write-Host "  Found local lasotuvi checkout: $localLasotuvi"
    python -m pip install --no-deps $localLasotuvi
} else {
    Write-Host "  Local lasotuvi checkout not found; installing from PyPI"
    python -m pip install --no-deps lasotuvi
}
Write-Host "  lasotuvi installed"

Write-Host ""
Write-Host "[4/4] Verifying installation..."
python -c "from lasotuvi.DiaBan import diaBan; from lasotuvi.App import lapDiaBan; print('  lasotuvi import successful'); print('  all modules available')"

Write-Host ""
Write-Host "=============================================="
Write-Host "  Lasotuvi installation completed"
Write-Host "=============================================="
