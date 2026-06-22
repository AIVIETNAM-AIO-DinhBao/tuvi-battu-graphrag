import json
from pathlib import Path
from typing import List

def load_gold_sections(jsonl_path: Path) -> List[Dict]:
    """Đọc file gold_sections.jsonl chứa các span gốc."""
    pass

def find_matching_chunks(doc_id: str, span_text: str, chunk_database: Dict) -> List[str]:
    """
    Tìm kiếm và map nguyên văn quote vào danh sách chunk_ids tương ứng.
    """
    pass

def create_mapped_release(input_jsonl: Path, output_jsonl: Path) -> None:
    """Tạo file gold_with_chunk_map.jsonl hoàn chỉnh."""
    pass

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    ANNOTATIONS_DIR = BASE_DIR / "annotations"
    RELEASE_DIR = BASE_DIR / "release"