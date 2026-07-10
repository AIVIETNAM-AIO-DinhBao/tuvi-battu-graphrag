r"""
GD-QA-04 — Generate candidate Tử Vi benchmark questions with Gemini.

This script reads the sample plan, compact chart_repr/chart_semantic inputs, builds a
strict prompt per QA slot, calls Gemini, validates/parses 2-3 candidate questions, and
writes JSONL drafts for review in GD-QA-05.

Default output:
  benchmark/tuvi_golden_dataset/annotations/drafts_questions.jsonl

Important:
- The script does NOT run automatically. Run it manually after reviewing config.
- It expects GEMINI_API_KEY in either repo/.env, workspace .env, or environment vars.
- It uses the Gemini REST API through urllib, so no extra SDK install is required.

Từ thư mục workspace hiện tại `d:\UNI_STUDY\Year3\Semester3\TextMining`, chạy thử 1 slot trước:

```cmd
python tuvi-battu-graphrag/benchmark/tuvi_golden_dataset/scripts/generate_draft_questions.py --slot-id TVQA-001 --include-images
```

Nếu output ổn, chạy một batch nhỏ (ví dụ 10 slot):

```cmd
python tuvi-battu-graphrag/benchmark/tuvi_golden_dataset/scripts/generate_draft_questions.py --limit 10 --include-images
```

Nếu batch nhỏ ổn, chạy toàn bộ 100 slot:

```cmd
python tuvi-battu-graphrag/benchmark/tuvi_golden_dataset/scripts/generate_draft_questions.py --include-images
```

Output chính sau khi chạy thật sẽ nằm ở:

```text
tuvi-battu-graphrag/benchmark/tuvi_golden_dataset/annotations/drafts_questions.jsonl
```

Prompt audit log nằm ở:

```text
tuvi-battu-graphrag/benchmark/tuvi_golden_dataset/reports/gd_qa_04_prompts.jsonl
```

Nếu muốn không gửi ảnh chart để tiết kiệm token/API, bỏ `--include-images`:

```cmd
python tuvi-battu-graphrag/benchmark/tuvi_golden_dataset/scripts/generate_draft_questions.py
```

Nếu muốn append vào file output hiện có thay vì ghi lại từ đầu:

```cmd
python tuvi-battu-graphrag/benchmark/tuvi_golden_dataset/scripts/generate_draft_questions.py --append --include-images
```

Bạn cũng có thể điều chỉnh thời gian nghỉ giữa các lần gọi bằng `--rate-limit-sleep X.X` nếu cần.

Ngoài ra:
python tuvi-battu-graphrag/benchmark/tuvi_golden_dataset/scripts/generate_draft_questions.py --start-index 0 --end-index 50 --include-images

python tuvi-battu-graphrag/benchmark/tuvi_golden_dataset/scripts/generate_draft_questions.py --start-index 50 --end-index 100 --append --include-images
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


PROMPT_VERSION = "v3"
DEFAULT_MODEL = "gemini-3.1-flash-lite"
FALLBACK_MODEL = "gemini-2.0-flash-lite"
DEFAULT_MAX_RETRIES = 2
DEFAULT_SLEEP_SECONDS = 1.2
DEFAULT_RATE_LIMIT_SLEEP_SECONDS = 7.0

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLE_PLAN = BASE_DIR / "samples" / "sample_plan.csv"
DEFAULT_QUESTION_SLOTS = BASE_DIR / "samples" / "question_slots.csv"
DEFAULT_REGISTRY = BASE_DIR / "charts" / "registry" / "chart_registry.json"
DEFAULT_OUTPUT = BASE_DIR / "annotations" / "drafts_questions.jsonl"
DEFAULT_PROMPT_LOG = BASE_DIR / "reports" / "gd_qa_04_prompts.jsonl"
DEFAULT_ENV_FILES = [
    BASE_DIR.parents[1] / ".env",  # tuvi-battu-graphrag/.env
    BASE_DIR.parents[2] / ".env",  # TextMining/.env
]


class GDQA04Error(RuntimeError):
    """GD-QA-04 controlled failure."""


def load_dotenv(paths: Iterable[Path]) -> None:
    """Minimal .env loader; does not override existing environment variables."""
    for path in paths:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def load_chart_registry(registry_path: Path) -> Dict[str, Dict[str, Any]]:
    registry = read_json(registry_path)
    if not isinstance(registry, list):
        raise GDQA04Error(f"Registry must be a list: {registry_path}")
    return {item["chart_id"]: item for item in registry}


def resolve_chart_path(registry_path: Path, registry_item: Dict[str, Any], key: str) -> Optional[Path]:
    rel = registry_item.get(key)
    if not rel:
        return None
    charts_dir = registry_path.parent.parent
    return charts_dir / rel


def star_label(star: Dict[str, Any]) -> str:
    name = star.get("name")
    status = star.get("status")
    if not name:
        return ""
    return f"{name}({status})" if status else str(name)


def split_focus(value: str) -> List[str]:
    return [part.strip() for part in (value or "").split("|") if part.strip()]


def compact_chart_repr(chart_repr: Dict[str, Any]) -> Dict[str, Any]:
    """Extract minimal chart_repr fields needed for prompt grounding."""
    houses = []
    for house in chart_repr.get("houses", []):
        major_stars = [star_label(s) for s in house.get("major_stars", []) if star_label(s)]
        aux_stars = [star_label(s) for s in house.get("aux_stars", []) if star_label(s)]

        notable_aux = []
        for aux in aux_stars:
            # Keep prompt compact while preserving real chart signals.
            if len(notable_aux) >= 8:
                break
            notable_aux.append(aux)

        houses.append(
            {
                "house_name": house.get("house_name"),
                "earthly_branch": house.get("earthly_branch"),
                "is_than_resident": bool(house.get("is_than_resident")),
                "trang_sinh": house.get("trang_sinh"),
                "tuan_khong": bool(house.get("tuan_khong")),
                "triet_khong": bool(house.get("triet_khong")),
                "major_stars": major_stars,
                "notable_aux_stars": notable_aux,
            }
        )

    return {
        "schema_role": chart_repr.get("schema_role"),
        "schema_version": chart_repr.get("schema_version"),
        "menh_position": chart_repr.get("menh_position"),
        "than_position": chart_repr.get("than_position"),
        "ban_menh": chart_repr.get("ban_menh"),
        "ngu_hanh_ban_menh": chart_repr.get("ngu_hanh_ban_menh"),
        "cuc": chart_repr.get("cuc"),
        "am_duong_nam_nu": chart_repr.get("am_duong_nam_nu"),
        "houses": houses,
    }


def relevant_house_names(slot: Dict[str, str], chart_repr: Dict[str, Any]) -> List[str]:
    focus_terms = set(split_focus(slot.get("primary_focus", "")) + split_focus(slot.get("secondary_focus", "")))
    topic = (slot.get("topic") or "").lower()

    houses = chart_repr.get("houses", [])
    names = {h.get("house_name") for h in houses if h.get("house_name")}

    selected = set()
    for term in focus_terms:
        if term in names:
            selected.add(term)
        if term == "Mệnh":
            selected.add("Mệnh")
        if term == "Thân":
            for h in houses:
                if h.get("is_than_resident") and h.get("house_name"):
                    selected.add(h["house_name"])

    topic_map = {
        "marriage": "Phu Thê",
        "relationship": "Phu Thê",
        "career": "Quan Lộc",
        "mobility": "Thiên Di",
        "wealth": "Tài Bạch",
        "health": "Tật Ách",
        "family": "Phụ Mẫu",
        "property": "Điền Trạch",
        "children": "Tử Tức",
        "friends": "Nô Bộc",
        "siblings": "Huynh Đệ",
        "fortune": "Phúc Đức",
    }
    for needle, house_name in topic_map.items():
        if needle in topic and house_name in names:
            selected.add(house_name)

    return sorted(selected)


def compact_chart_semantic(
    chart_semantic: Optional[Dict[str, Any]],
    slot: Dict[str, str],
    chart_repr: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Extract semantic hints only; these are not answer sources by themselves."""
    if not chart_semantic:
        return None

    focus_houses = set(relevant_house_names(slot, chart_repr))
    focus_terms = set(split_focus(slot.get("primary_focus", "")) + split_focus(slot.get("secondary_focus", "")))

    palace_subset = []
    for palace in chart_semantic.get("palace_semantics", []):
        house_name = palace.get("house_name")
        include = house_name in focus_houses
        include = include or ("Mệnh" in focus_terms and palace.get("is_menh"))
        include = include or ("Thân" in focus_terms and palace.get("is_than_resident"))
        if include:
            palace_subset.append(
                {
                    "house_name": house_name,
                    "earthly_branch": palace.get("earthly_branch"),
                    "is_menh": bool(palace.get("is_menh")),
                    "is_than_resident": bool(palace.get("is_than_resident")),
                    "house_relations": palace.get("house_relations"),
                    "major_stars": [star_label(s) for s in palace.get("major_stars", []) if star_label(s)],
                    "state_flags": {
                        "trang_sinh": palace.get("trang_sinh"),
                        "tuan_khong": bool(palace.get("tuan_khong")),
                        "triet_khong": bool(palace.get("triet_khong")),
                    },
                }
            )

    return {
        "core_identity": chart_semantic.get("core_identity"),
        "focus_relations": chart_semantic.get("focus_relations"),
        "relevant_palaces": palace_subset[:6],
        "notable_patterns": chart_semantic.get("notable_patterns", [])[:12],
    }


def collect_allowed_chart_signals(
    chart_repr_summary: Dict[str, Any],
    chart_semantic_summary: Optional[Dict[str, Any]],
) -> List[str]:
    signals = set()
    for key in ["menh_position", "than_position", "ban_menh", "ngu_hanh_ban_menh", "cuc", "am_duong_nam_nu"]:
        value = chart_repr_summary.get(key)
        if value:
            signals.add(str(value))

    for literal in ["Mệnh", "Thân", "Thân cư", "Bản Mệnh", "Cục", "Tuần", "Triệt", "Tràng Sinh"]:
        signals.add(literal)

    for house in chart_repr_summary.get("houses", []):
        if house.get("is_than_resident") and house.get("house_name"):
            signals.add(f"Thân cư {house['house_name']}")
        for key in ["house_name", "earthly_branch", "trang_sinh"]:
            value = house.get(key)
            if value:
                signals.add(str(value))
        for star in house.get("major_stars", []) + house.get("notable_aux_stars", []):
            signals.add(re.sub(r"\([^)]*\)", "", star).strip())

    if chart_semantic_summary:
        core = chart_semantic_summary.get("core_identity") or {}
        for value in core.values():
            if isinstance(value, str) and value:
                signals.add(value)
        for relation in (chart_semantic_summary.get("focus_relations") or {}).values():
            if isinstance(relation, dict):
                for value in relation.values():
                    if isinstance(value, str):
                        signals.add(value)
                    elif isinstance(value, list):
                        signals.update(str(v) for v in value)

    return sorted(s for s in signals if s)


def candidate_count_for_complexity(complexity: str) -> int:
    return 2 if (complexity or "").strip().lower() == "direct" else 3


def output_contract(slot: Dict[str, str]) -> Dict[str, Any]:
    count = candidate_count_for_complexity(slot.get("question_complexity", ""))
    return {
        "candidates": [
            {
                "candidate_id": f"{slot['slot_id']}-C{i}",
                "question": "Câu hỏi tiếng Việt, có dấu, không kèm câu trả lời",
                "rationale": "1 câu ngắn giải thích vì sao phù hợp slot",
                "expected_chart_signals": ["chỉ dùng tín hiệu có thật trong Allowed chart signals"],
                "risk_notes": "ghi rủi ro ngắn; nếu thấp ghi 'Thấp'",
            }
            for i in range(1, count + 1)
        ]
    }


def image_part_for_chart(chart_id: str, images_dir: Path) -> Optional[Dict[str, Any]]:
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        path = images_dir / f"{chart_id}{ext}"
        if path.exists():
            mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
            return {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64.b64encode(path.read_bytes()).decode("ascii"),
                }
            }
    return None


def build_prompt(
    slot: Dict[str, str],
    chart_repr: Dict[str, Any],
    chart_semantic: Optional[Dict[str, Any]] = None,
) -> str:
    chart_repr_summary = compact_chart_repr(chart_repr)
    semantic_summary = compact_chart_semantic(chart_semantic, slot, chart_repr)
    allowed_signals = collect_allowed_chart_signals(chart_repr_summary, semantic_summary)
    expected_count = candidate_count_for_complexity(slot.get("question_complexity", ""))

    return f"""Bạn đang hỗ trợ tạo benchmark QA cho hệ thống RAG Tử Vi.

Nhiệm vụ:
Sinh đúng {expected_count} câu hỏi ứng viên bằng tiếng Việt cho đúng slot dưới đây.
Chỉ tạo câu hỏi, không trả lời câu hỏi.

Mục tiêu phong cách:
- Câu hỏi phải nghe giống câu hỏi mà một người dùng bình thường thật sự sẽ hỏi khi nhờ AI xem lá số Tử Vi.
- Người hỏi chủ yếu hỏi về các mảng đời sống: tính cách, nghề nghiệp, thăng tiến, tài lộc, kinh doanh, hôn nhân, người phối ngẫu, cha mẹ/anh em, con cái, sức khỏe, du học/xuất ngoại, định cư, nhà cửa.
- Người hỏi có thể nhắc tên cung phổ biến như Mệnh, Thân, Phu Thê, Tài Bạch, Quan Lộc, Điền Trạch, Tật Ách, Thiên Di nếu cần, nhưng thường KHÔNG đọc vanh vách tên sao hoặc quan hệ kỹ thuật.
- Người hỏi KHÔNG tự nói thành chuỗi kỹ thuật dày đặc như “tam hợp Mệnh”, “xung chiếu”, “hãm địa”, “tọa thủ”, “đồng cung”, “cách cục”.
- Phần reasoning kỹ thuật là việc của hệ thống ở backend; câu hỏi bề mặt phải là nhu cầu đời thực trước, không phải đề bài kỹ thuật.
- Tuy vậy, câu hỏi vẫn phải đủ cụ thể để benchmark có thể chấm được; nên gắn với một chủ đề đời sống hoặc một cung rõ ràng, không hỏi “luận tổng quan”.

Từ/cụm từ KHÔNG được xuất hiện trong field question:
- tam hợp, xung chiếu, cung xung chiếu, cung đối diện, cung đối, nhị hợp
- hãm địa, miếu địa, vượng địa, đắc địa, tọa thủ, đồng cung, cách cục
- vận mệnh, luận cả đời, tổng thể lá số, phân tích toàn diện
Các từ này nếu cần chỉ dùng trong rationale hoặc expected_chart_signals, không đưa lên câu hỏi bề mặt.

Hạn chế mạnh trong field question:
- Không liệt kê nhiều tên sao trong cùng một câu hỏi. Tốt nhất là không nêu tên sao; nếu thật cần thì tối đa 1 tên sao phổ biến.
- Hạn chế nhắc Tuần/Triệt trừ khi slot là special_state_interpretation hoặc câu hỏi tự nhiên thật sự cần.
- Nếu cần nhắc kỹ thuật, ưu tiên tên cung hơn tên sao.

Ví dụ phong cách nên gần tới:
- “Cung Mệnh và cung Thân của lá số này nói gì về tính cách và hậu vận?”
- “Đường công việc của lá số này có gì đáng chú ý?”
- “Tài lộc của người này có sáng không?”
- “Người này có hợp đi xa, ra ngoài làm ăn không?”
- “Dựa vào lá số này, tôi có thể đi du học hoặc xuất ngoại không?”
- “Cung Phu Thê của tôi có tốt không, đường tình duyên có lận đận không?”
- “Bao giờ mình có sự nghiệp ổn định hoặc được thăng chức?”
- “Mệnh này có giàu được không, cung Tài Bạch và Điền Trạch có sáng sủa không?”
- “Mình có nên tự đứng ra kinh doanh hay chỉ nên làm công ăn lương?”
- “Người chồng/vợ tương lai của mình có đặc điểm gì nổi bật?”
- “Mối quan hệ giữa mình và gia đình có tốt không, có được nhờ gia đình không?”
- “Sau này con cái của mình có ngoan ngoãn, hiếu thuận và thành đạt không?”
- “Sức khỏe của mình có điểm gì tiềm ẩn đáng lo không?”
- “Tuần hoặc Triệt trong lá số này ảnh hưởng gì đến công việc / tình duyên?”

Ví dụ rewrite từ TỆ sang TỐT:
- TỆ: “Xét tam hợp Mệnh Dần Ngọ Tuất với sao A, sao B, sao C đồng cung thì sự nghiệp thế nào?”
  TỐT: “Đường công việc của tôi có dễ thăng tiến không?”
- TỆ: “Cung Phu Thê có Thiên Đồng, Thái Âm, Đà La thì hôn nhân ra sao?”
  TỐT: “Cung Phu Thê của tôi có tốt không, chuyện kết hôn có dễ muộn hoặc lận đận không?”
- TỆ: “Cung xung chiếu Thiên Di có Phá Quân hãm địa ảnh hưởng thế nào đến cách cục?”
  TỐT: “Lá số này có hợp đi xa, đi du học hoặc làm ăn xa không?”
- TỆ: “Mệnh có Lộc Tồn bị Triệt thì tài lộc bị phá thế nào?”
  TỐT: “Tài lộc của tôi có sáng không, có dễ tích lũy tiền bạc không?”
- TỆ: “Thân cư Phu Thê có Tham Lang tọa thủ thì hậu vận ra sao?”
  TỐT: “Chuyện hôn nhân có ảnh hưởng nhiều đến cuộc sống sau này của tôi không?”

Ví dụ phong cách cần tránh, tuyệt đối không hỏi:
- “Khi cung Mệnh có Lộc Tồn và bộ sao Thiên Đồng, Thái Âm bị Triệt, việc cung xung chiếu Thiên Di không có chính tinh nhưng có Địa Không (hãm) và Đào Hoa sẽ ảnh hưởng thế nào đến cách cục của lá số?”
- “Xét tam hợp Mệnh Dần Ngọ Tuất với sao A, sao B, sao C đồng cung thì...”
- “Cung Phu Thê có Thiên Cơ, Kình Dương, Đà La, Hóa Kỵ đồng cung thì đường hôn nhân bị phá thế nào?”
- Các câu để lộ quá nhiều reasoning nội bộ khiến người hỏi trông như chuyên gia Tử Vi.

Thông tin slot:
- slot_id: {slot.get("slot_id")}
- chart_id: {slot.get("chart_id")}
- question_complexity: {slot.get("question_complexity")}
- question_family: {slot.get("question_family")}
- topic: {slot.get("topic")}
- primary_focus: {slot.get("primary_focus")}
- secondary_focus: {slot.get("secondary_focus")}
- reasoning_pattern: {slot.get("reasoning_pattern")}
- source_required: {slot.get("source_required")}
- primary_doc_hint: {slot.get("primary_doc_hint")}
- notes: {slot.get("notes")}

Ràng buộc bắt buộc:
- Chỉ viết câu hỏi tiếng Việt, đầy đủ dấu.
- Không trả lời câu hỏi.
- Không trích sách trong câu hỏi.
- Không nhắc Bát Tự, Tứ Trụ, tử bình, can chi năm tháng ngày giờ ngoài dữ kiện chart Tử Vi.
- Không viết câu hỏi quá rộng hoặc quá chung như “hãy phân tích tổng quan toàn diện”, “luận cả đời”, “đánh giá vận mệnh”, “xem giúp mọi mặt”.
- Mỗi câu hỏi phải bám sát dữ kiện chart thật bên dưới.
- Phải bám đúng question_complexity, question_family, topic, primary_focus, secondary_focus.
- expected_chart_signals chỉ được lấy từ Allowed chart signals; không được bịa sao/cung/địa chi/trạng thái.
- expected_chart_signals nên ngắn gọn, ưu tiên 2-4 tín hiệu thật sự cần để map câu hỏi về chart; không nhồi toàn bộ sao/cung liên quan nếu không cần.
- rationale phải ngắn, thực dụng, tối đa 1 câu.
- risk_notes phải ngắn.
- Ưu tiên wording theo mối quan tâm đời thực: tính cách, công việc, tiền bạc, hôn nhân, đi xa/du học/xuất ngoại, gia đình, con cái, sức khỏe, nhà cửa, hậu vận, trở ngại, thuận lợi.
- Tránh nêu thuật ngữ kỹ thuật chuyên sâu trong câu hỏi. Không dùng tên quan hệ cung như tam hợp/xung chiếu ở field question.
- Nếu có thể, hãy để phần kỹ thuật nằm trong expected_chart_signals và rationale, còn câu hỏi bề mặt nên tự nhiên hơn.
- Không biến câu hỏi thành mô tả chart quá rõ như “cung X có sao A, sao B, sao C thì sao?”. Người dùng thường hỏi “cung X có tốt không?” hoặc “mảng đời sống Y có thuận lợi không?”.

Logic theo complexity:
- Direct: câu hỏi phải trả lời được chỉ từ chart_repr/chart image, không cần sách. Đây là các câu fact cơ bản. Field question của Direct KHÔNG được hỏi “ảnh hưởng gì”, “ý nghĩa gì”, “tác động thế nào”, “có tốt/thuận lợi không”, “ra sao”. Direct nên hỏi “ở đâu?”, “là gì?”, “cung nào?”, “có trạng thái nào nổi bật?”.
- One-hop: câu hỏi nên giống nhu cầu thật của người dùng, nhưng để trả lời đúng thì cần 1 fact từ chart + 1 quy tắc/diễn giải từ sách. Không nên phô bày toàn bộ fact kỹ thuật trong câu hỏi.
- Two-hop: câu hỏi bề mặt vẫn phải tự nhiên như câu người dùng hỏi; phần 2 bước suy luận nên ẩn ở backend. Có thể hỏi về một chủ đề đời thực (công việc, tiền bạc, tình duyên, đi xa...) nhưng phải đủ cụ thể để có thể map về 2 bước reasoning trong chart.

Hướng dẫn thêm theo family:
- core_identity: ưu tiên câu fact ngắn, tự nhiên.
- core_identity: chỉ hỏi fact cơ bản. Không hỏi diễn giải, tốt/xấu, ảnh hưởng hoặc ý nghĩa sâu.
- menh_house_interpretation: nên hỏi về tính cách, năng lực, xu hướng sống, điểm mạnh/yếu; không cần liệt kê sao ở Mệnh trong câu hỏi.
- than_cu_interpretation: nên hỏi về hậu vận, cách hành động, môi trường phát triển, mảng đời sống ảnh hưởng mạnh về sau; không cần lộ reasoning “Thân cư...” nếu câu hỏi tự nhiên hơn vẫn giữ được intent.
- menh_cuc_relation: nên hỏi theo kiểu “Mệnh và Cục của lá số này có nâng đỡ nhau không?” hoặc “nền tảng lá số có thuận không?”, không nêu công thức ngũ hành dài dòng.
- special_state_interpretation: có thể nhắc Tuần/Triệt vì đây là thuật ngữ tương đối phổ biến, nhưng vẫn nên hỏi theo tác động thực tế lên một chủ đề cụ thể.
- dai_van_interpretation: nên hỏi về các sự kiện, cơ hội, thách thức trong một giai đoạn đại vận cụ thể, tập trung vào các khía cạnh đời sống như sự nghiệp, tài lộc, tình duyên, sức khỏe. Tránh nhắc trực tiếp tên cung hoặc sao liên quan đến đại vận trong câu hỏi, mà thay vào đó tập trung vào ảnh hưởng của nó.
- menh_tam_hop / menh_xung_chieu / topic_house_plus_relations / synthesis_judgement: reasoning có thể phức tạp bên trong, nhưng field question tuyệt đối không nói “tam hợp”, “xung chiếu”, “cung đối diện”. Hãy chuyển thành câu đời thường về công việc, tiền bạc, tình duyên, đi xa, gia đình, sức khỏe.

Chart context compact từ chart_repr:
{json.dumps(chart_repr_summary, ensure_ascii=False, indent=2)}

Semantic hints compact (nếu có; chỉ dùng để chọn focus đúng hơn, không bịa thêm dữ kiện):
{json.dumps(semantic_summary, ensure_ascii=False, indent=2)}

Allowed chart signals:
{json.dumps(allowed_signals, ensure_ascii=False, indent=2)}

Output bắt buộc:
- Chỉ trả về JSON object parseable, không markdown, không ```json.
- JSON phải có đúng key "candidates".
- Số candidates phải đúng {expected_count}.
- Mỗi candidate nên khác nhau về wording hoặc góc hỏi, nhưng cùng bám đúng slot.
- Ít nhất 1 candidate trong mỗi slot phải có phong cách rất gần câu người dùng thật sẽ hỏi.
- Format:
{json.dumps(output_contract(slot), ensure_ascii=False, indent=2)}
"""


def normalize_json_text(text: str) -> str:
    value = text.strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?\s*", "", value, flags=re.IGNORECASE)
        value = re.sub(r"\s*```$", "", value)
    start = value.find("{")
    end = value.rfind("}")
    if start >= 0 and end > start:
        value = value[start : end + 1]
    return value


def validate_candidates(
    parsed: Dict[str, Any],
    slot: Dict[str, str],
    allowed_signals: List[str],
) -> List[Dict[str, Any]]:
    if not isinstance(parsed, dict):
        raise GDQA04Error("LLM output is not a JSON object")
    candidates = parsed.get("candidates")
    if not isinstance(candidates, list):
        raise GDQA04Error("LLM output missing candidates list")

    expected_count = candidate_count_for_complexity(slot.get("question_complexity", ""))
    if len(candidates) not in {2, 3}:
        raise GDQA04Error(f"Candidate count must be 2-3, got {len(candidates)}")
    if slot.get("question_complexity") == "Direct" and len(candidates) != 2:
        raise GDQA04Error(f"Direct slot must have exactly 2 candidates, got {len(candidates)}")
    if slot.get("question_complexity") != "Direct" and len(candidates) != expected_count:
        raise GDQA04Error(f"{slot.get('question_complexity')} slot must have {expected_count} candidates")

    allowed = set(allowed_signals)
    normalized = []
    forbidden_terms = ["Bát Tự", "Tứ Trụ", "tử bình", "luận cả đời", "tổng quan toàn diện"]

    for idx, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            raise GDQA04Error(f"Candidate {idx} is not an object")

        candidate_id = candidate.get("candidate_id") or f"{slot['slot_id']}-C{idx}"
        question = str(candidate.get("question", "")).strip()
        rationale = str(candidate.get("rationale", "")).strip()
        risk_notes = str(candidate.get("risk_notes", "")).strip() or "Thấp"
        signals = candidate.get("expected_chart_signals", [])

        if not question.endswith("?"):
            question = question.rstrip(".。") + "?"
        if not question:
            raise GDQA04Error(f"Candidate {candidate_id} missing question")
        if any(term.lower() in question.lower() for term in forbidden_terms):
            raise GDQA04Error(f"Candidate {candidate_id} contains forbidden/generic term")
        if not rationale:
            raise GDQA04Error(f"Candidate {candidate_id} missing rationale")
        if not isinstance(signals, list) or not signals:
            raise GDQA04Error(f"Candidate {candidate_id} missing expected_chart_signals")

        clean_signals = []
        unknown_signals = []
        for signal in signals:
            signal_text = str(signal).strip()
            if not signal_text:
                continue
            if signal_text in allowed:
                clean_signals.append(signal_text)
            else:
                unknown_signals.append(signal_text)

        if unknown_signals:
            raise GDQA04Error(
                f"Candidate {candidate_id} uses signals not found in chart: {unknown_signals}"
            )
        if not clean_signals:
            raise GDQA04Error(f"Candidate {candidate_id} has no valid chart signals")

        normalized.append(
            {
                "candidate_id": candidate_id,
                "question": question,
                "rationale": rationale,
                "expected_chart_signals": clean_signals,
                "risk_notes": risk_notes,
            }
        )

    return normalized


def parse_llm_output(text: str, slot: Dict[str, str], allowed_signals: List[str]) -> List[Dict[str, Any]]:
    try:
        parsed = json.loads(normalize_json_text(text))
    except json.JSONDecodeError as exc:
        raise GDQA04Error(f"Cannot parse LLM JSON: {exc}") from exc
    return validate_candidates(parsed, slot, allowed_signals)


def gemini_generate_content(
    prompt: str,
    model: str,
    api_key: str,
    image_part: Optional[Dict[str, Any]] = None,
    timeout: int = 90,
) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    parts: List[Dict[str, Any]] = [{"text": prompt}]
    if image_part:
        parts.append(image_part)

    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "temperature": 0.35,
            "topP": 0.9,
            "maxOutputTokens": 2048,
            "responseMimeType": "application/json",
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GDQA04Error(f"Gemini HTTP {exc.code}: {detail}") from exc

    candidates = result.get("candidates") or []
    if not candidates:
        raise GDQA04Error(f"Gemini returned no candidates: {result}")

    parts_out = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts_out if isinstance(part, dict))
    if not text:
        raise GDQA04Error(f"Gemini returned empty text: {result}")
    return text


def call_llm(
    prompt: str,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    image_part: Optional[Dict[str, Any]] = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    sleep_seconds: float = DEFAULT_SLEEP_SECONDS,
) -> str:
    if not api_key:
        raise GDQA04Error("Missing GEMINI_API_KEY. Put it in .env or export it before running.")

    last_error: Optional[Exception] = None
    models_to_try = [model]
    if model == DEFAULT_MODEL:
        models_to_try.append(FALLBACK_MODEL)

    for model_name in models_to_try:
        for attempt in range(max_retries + 1):
            try:
                return gemini_generate_content(prompt, model_name, api_key, image_part=image_part)
            except Exception as exc:  # retry transient/API format errors
                last_error = exc
                if attempt < max_retries:
                    time.sleep(sleep_seconds * (attempt + 1))
                else:
                    break

    raise GDQA04Error(f"LLM call failed after retries: {last_error}")


def build_output_row(
    slot: Dict[str, str],
    model: str,
    used_chart_repr: bool,
    used_chart_semantic: bool,
    candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "slot_id": slot["slot_id"],
        "chart_id": slot["chart_id"],
        "question_complexity": slot["question_complexity"],
        "question_family": slot["question_family"],
        "topic": slot["topic"],
        "owner": slot.get("owner", ""),
        "reviewer": slot.get("reviewer", ""),
        "llm_model": model,
        "prompt_version": PROMPT_VERSION,
        "chart_inputs": {
            "used_chart_repr": used_chart_repr,
            "used_chart_semantic": used_chart_semantic,
        },
        "candidates": candidates,
        "status": "draft_generated",
    }


def select_slots(
    slots: List[Dict[str, str]],
    slot_ids: Optional[List[str]],
    limit: Optional[int],
    start_index: Optional[int],
    end_index: Optional[int],
) -> List[Dict[str, str]]:
    selected = slots
    if slot_ids:
        wanted = set(slot_ids)
        selected = [slot for slot in selected if slot.get("slot_id") in wanted]
    start = start_index if start_index is not None else 0
    end = end_index if end_index is not None else None
    selected = selected[start:end]
    if limit is not None:  # apply limit after index selection
        selected = selected[:limit]
    return selected


def run_generation(args: argparse.Namespace) -> Dict[str, Any]:
    load_dotenv(DEFAULT_ENV_FILES + [Path(args.env_file)] if args.env_file else DEFAULT_ENV_FILES)

    slots = read_csv(Path(args.sample_plan))
    slots = select_slots(slots, args.slot_id, args.limit, args.start_index, args.end_index)
    registry = load_chart_registry(Path(args.registry))
    api_key = os.environ.get("GEMINI_API_KEY")

    rows = []
    missing_chart_repr = []
    missing_chart_semantic = []
    parse_errors = []
    llm_errors = []

    output_path = Path(args.output)
    prompt_log = Path(args.prompt_log)
    if output_path.exists() and not args.append and not args.dry_run:
        output_path.unlink()
    if prompt_log.exists() and not args.append:
        prompt_log.unlink()

    for index, slot in enumerate(slots, start=1):
        slot_id = slot["slot_id"]
        chart_id = slot["chart_id"]
        print(f"[{index}/{len(slots)}] Start {slot_id} ({chart_id})", flush=True)

        registry_item = registry.get(chart_id)
        if not registry_item:
            missing_chart_repr.append(slot_id)
            print(f"[{index}/{len(slots)}] SKIP {slot_id}: missing chart registry entry", flush=True)
            continue

        chart_repr_path = resolve_chart_path(Path(args.registry), registry_item, "chart_file")
        chart_semantic_path = resolve_chart_path(Path(args.registry), registry_item, "semantic_file")

        if not chart_repr_path or not chart_repr_path.exists():
            missing_chart_repr.append(slot_id)
            print(f"[{index}/{len(slots)}] SKIP {slot_id}: missing chart_repr", flush=True)
            continue

        chart_repr = read_json(chart_repr_path)
        chart_semantic = None
        used_semantic = False
        if chart_semantic_path and chart_semantic_path.exists():
            chart_semantic = read_json(chart_semantic_path)
            used_semantic = True
        else:
            missing_chart_semantic.append(slot_id)

        prompt = build_prompt(slot, chart_repr, chart_semantic)
        chart_repr_summary = compact_chart_repr(chart_repr)
        semantic_summary = compact_chart_semantic(chart_semantic, slot, chart_repr)
        allowed_signals = collect_allowed_chart_signals(chart_repr_summary, semantic_summary)

        image_part = None
        if args.include_images:
            image_part = image_part_for_chart(chart_id, Path(args.images_dir))

        append_jsonl(
            prompt_log,
            {
                "slot_id": slot_id,
                "chart_id": chart_id,
                "prompt_version": PROMPT_VERSION,
                "has_image": bool(image_part),
                "prompt": prompt,
            },
        )

        if args.dry_run:
            print(
                f"[{index}/{len(slots)}] DRY-RUN {slot_id}: prompt logged; "
                f"image={'yes' if image_part else 'no'}; semantic={'yes' if used_semantic else 'no'}",
                flush=True,
            )
            continue

        try:
            text = call_llm(
                prompt,
                model=args.model,
                api_key=api_key,
                image_part=image_part,
                max_retries=args.max_retries,
                sleep_seconds=args.sleep_seconds,
            )
        except Exception as exc:
            llm_errors.append({"slot_id": slot_id, "error": str(exc)})
            print(f"[{index}/{len(slots)}] LLM_ERROR {slot_id}: {exc}", flush=True)
            if args.rate_limit_sleep > 0 and index < len(slots):
                print(f"[{index}/{len(slots)}] Rest {args.rate_limit_sleep:.1f}s for Gemini rate limit", flush=True)
                time.sleep(args.rate_limit_sleep)
            continue

        try:
            candidates = parse_llm_output(text, slot, allowed_signals)
        except Exception as exc:
            parse_errors.append({"slot_id": slot_id, "error": str(exc), "raw_text": text})
            print(f"[{index}/{len(slots)}] PARSE_ERROR {slot_id}: {exc}", flush=True)
            if args.rate_limit_sleep > 0 and index < len(slots):
                print(f"[{index}/{len(slots)}] Rest {args.rate_limit_sleep:.1f}s for Gemini rate limit", flush=True)
                time.sleep(args.rate_limit_sleep)
            continue

        row = build_output_row(
            slot=slot,
            model=args.model,
            used_chart_repr=True,
            used_chart_semantic=used_semantic,
            candidates=candidates,
        )
        rows.append(row)
        append_jsonl(output_path, row)

        print(
            f"[{index}/{len(slots)}] DONE {slot_id}: "
            f"{len(candidates)} candidates -> {output_path}",
            flush=True,
        )
        if args.rate_limit_sleep > 0 and index < len(slots):
            print(f"[{index}/{len(slots)}] Rest {args.rate_limit_sleep:.1f}s for Gemini rate limit", flush=True)
            time.sleep(args.rate_limit_sleep)

    total_candidates = sum(len(row["candidates"]) for row in rows)
    avg_candidates = total_candidates / len(rows) if rows else 0.0

    report = {
        "processed_slots": len(slots),
        "generated_rows": len(rows),
        "missing_chart_repr": missing_chart_repr,
        "missing_chart_semantic": missing_chart_semantic,
        "llm_errors": llm_errors,
        "parse_errors": parse_errors,
        "average_candidates_per_generated_slot": round(avg_candidates, 2),
        "output": str(output_path),
        "prompt_log": str(prompt_log),
        "dry_run": bool(args.dry_run),
    }
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GD-QA-04 generate draft benchmark questions with Gemini")
    parser.add_argument("--sample-plan", default=str(DEFAULT_SAMPLE_PLAN), help="Path to samples/sample_plan.csv")
    parser.add_argument("--question-slots", default=str(DEFAULT_QUESTION_SLOTS), help="Reserved path for question_slots.csv")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY), help="Path to charts/registry/chart_registry.json")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output JSONL path")
    parser.add_argument("--prompt-log", default=str(DEFAULT_PROMPT_LOG), help="Prompt audit JSONL path")
    parser.add_argument("--images-dir", default=str(BASE_DIR / "charts" / "images"), help="Directory with CHART-00x images")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini model name")
    parser.add_argument("--env-file", default=None, help="Optional extra .env file")
    parser.add_argument("--slot-id", action="append", help="Only run one slot_id; repeatable")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of slots (after start_index/end_index)")
    parser.add_argument("--start-index", type=int, default=None, help="Start processing slots from this 0-based index (inclusive)")
    parser.add_argument("--end-index", type=int, default=None, help="Stop processing slots at this 0-based index (exclusive)")
    parser.add_argument("--append", action="store_true", help="Append instead of replacing output/prompt log")
    parser.add_argument("--dry-run", action="store_true", help="Build prompts/report only; do not call Gemini or write drafts")
    parser.add_argument("--include-images", action="store_true", help="Attach chart image CHART-00x.* to Gemini request if present")
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    parser.add_argument("--sleep-seconds", type=float, default=DEFAULT_SLEEP_SECONDS)
    parser.add_argument(
        "--rate-limit-sleep",
        type=float,
        default=DEFAULT_RATE_LIMIT_SLEEP_SECONDS,
        help="Seconds to rest after each Gemini call; default 7s to stay below 10 calls/minute",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        report = run_generation(args)
    except Exception as exc:
        print(f"GD-QA-04 failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.dry_run:
        print("Dry-run only: prompts were written, Gemini was not called, drafts_questions.jsonl was not generated.")
    else:
        print("GD-QA-04 complete. Review drafts_questions.jsonl before GD-QA-05.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())