import json
from pathlib import Path

def validate_against_schema(data_file: Path, schema_file: Path) -> bool:
    """
    Kiểm tra JSONL có đúng cấu trúc schema_release.json không.
    (Khuyến nghị sử dụng thư viện jsonschema)
    """
    pass

def audit_dataset_rules(data_file: Path) -> dict:
    """
    Kiểm tra các luật cứng:
    - Đủ 100 sample (10 Direct, 40 One-hop, 50 Two-hop)
    - Không duplicate IDs
    - Direct sample có gold_context_spans rỗng
    """
    pass

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    SCHEMA_FILE = BASE_DIR / "guideline" / "schema_release.json"
    RELEASE_FILE = BASE_DIR / "release" / "golden_v1_release.jsonl"