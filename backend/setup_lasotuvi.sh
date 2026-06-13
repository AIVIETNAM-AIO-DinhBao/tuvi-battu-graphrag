#!/bin/bash
# =============================================================================
# Lasotuvi Installation Script
# =============================================================================
# Script này cài đặt lasotuvi engine đúng cách cho dự án tuvi-battu-graphrag
#
# CÁCH SỬ DỤNG:
#   chmod +x setup_lasotuvi.sh
#   ./setup_lasotuvi.sh
#
# LƯU Ý: Chạy script này TRƯỚC KHI chạy ứng dụng
# =============================================================================

set -e  # Exit on error

echo "=============================================="
echo "  Lasotuvi Installation Script"
echo "=============================================="
echo ""

# Check Python version
echo "[1/4] Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $PYTHON_VERSION"

# Install ephem first (required dependency)
echo ""
echo "[2/4] Installing ephem dependency..."
pip install "ephem>=3.7.6.0"
echo "  ✓ ephem installed"

# Install lasotuvi with --no-deps to avoid broken dependencies
echo ""
echo "[3/4] Installing lasotuvi (with --no-deps)..."
pip install --no-deps lasotuvi
echo "  ✓ lasotuvi installed"

# Verify installation
echo ""
echo "[4/4] Verifying installation..."
python3 -c "
from lasotuvi.DiaBan import diaBan
from lasotuvi.App import lapDiaBan
print('  ✓ lasotuvi import successful')
print('  ✓ All modules available')
"

echo ""
echo "=============================================="
echo "  ✓ Lasotuvi installation completed!"
echo "=============================================="
echo ""
echo "Tiếp theo, bạn có thể:"
echo "  1. Chạy: pip install -r requirements.txt"
echo "  2. Chạy: uvicorn app.main:app --reload"
echo ""