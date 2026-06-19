import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Cấu hình logging cơ bản
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def load_raw_engine_output(file_path: Path) -> Dict[str, Any]:
    """Đọc dữ liệu thô từ Tuvi_Engine."""
    pass

def standardize_star_names(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chuẩn hóa tên sao (Title Case, có dấu) và phân loại chính tinh/phụ tinh.
    """
    pass

def build_chart_registry(chart_folder: Path, output_file: Path) -> None:
    """
    Quét qua các file CHART-*.json, gán coverage tags và xuất ra chart_registry.json.
    """
    pass

if __name__ == "__main__":
    # TODO: 
    BASE_DIR = Path(__file__).resolve().parent.parent
    CHARTS_DIR = BASE_DIR / "charts"
    REGISTRY_OUTPUT = CHARTS_DIR / "chart_registry.json"
    
    logging.info("Bắt đầu build chart registry...")
    # build_chart_registry(CHARTS_DIR, REGISTRY_OUTPUT)
    logging.info("Hoàn tất!")