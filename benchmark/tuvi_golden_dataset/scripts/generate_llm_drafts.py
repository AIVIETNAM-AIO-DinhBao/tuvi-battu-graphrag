import json
import csv
from pathlib import Path
from typing import List, Dict

def load_question_slots(csv_path: Path) -> List[Dict]:
    """Đọc ma trận phân bổ 100 câu hỏi từ question_slots.csv."""
    pass

def generate_candidate_questions(chart_repr: Dict, complexity: str, topic: str) -> List[Dict]:
    """
    Sử dụng Prompt A để sinh 3 câu hỏi candidate cho mỗi slot.
    """
    pass

def draft_grounded_answer(chart_repr: Dict, context_spans: List[Dict]) -> Dict[str, str]:
    """
    Sử dụng Prompt C để sinh gold_answer_draft dựa trên chart và spans thật.
    """
    pass

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    SLOTS_FILE = BASE_DIR / "samples" / "question_slots.csv"
    DRAFTS_OUT = BASE_DIR / "drafts" / "drafts_questions.jsonl"
    