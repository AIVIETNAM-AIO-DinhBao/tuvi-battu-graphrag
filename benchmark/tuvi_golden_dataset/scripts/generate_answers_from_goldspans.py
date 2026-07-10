"""
Generate answers for QA pairs using Gemini API based on chart semantic and goldspans.

This script reads the consolidated goldspan file, extracts chart_semantic and goldspan contexts,
builds prompts, calls Gemini API to generate answers, and saves results.

It writes two outputs:
- full output JSONL with all slot metadata plus the generated answer
- minimal output JSONL with only slot_id, chart_id, question, and generated_answer

Usage:
    python tuvi-battu-graphrag/benchmark/tuvi_golden_dataset/scripts/generate_answers_from_goldspans.py

Options:
    --input: Path to consolidated goldspan file (default: annotations/goldspan/processed_goldspans/final_consolidated/goldspan_final_consolidated.jsonl)
    --output: Path to full output file (default: annotations/answer/final_answers.jsonl)
    --slot-id: Process only a specific slot ID (for testing)
    --limit: Limit number of slots to process
    --start-index: Start from this index
    --end-index: End at this index (exclusive)
    --append: Append to existing output file instead of overwriting
    --rate-limit-sleep: Sleep seconds between API calls (default: 7.0)
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_MODEL = "gemini-3.1-flash-lite"
FALLBACK_MODEL = "gemini-1.5-flash"
DEFAULT_MAX_RETRIES = 2
DEFAULT_SLEEP_SECONDS = 1.5
DEFAULT_RATE_LIMIT_SLEEP = 6.0

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = BASE_DIR / "annotations" / "goldspan" / "processed_goldspans" / "final_consolidated" / "goldspan_final_consolidated.jsonl"
DEFAULT_OUTPUT = BASE_DIR / "annotations" / "answer" / "final_answers.jsonl"
DEFAULT_CHARTS_DIR = BASE_DIR / "charts"
DEFAULT_QUESTIONS_PATH = BASE_DIR / "annotations" / "final_questions.jsonl"
DEFAULT_ENV_FILES = [
    BASE_DIR.parents[1] / ".env",  # tuvi-battu-graphrag/.env
    BASE_DIR.parents[2] / ".env",  # TextMining/.env
]


class AnswerGenError(Exception):
    """Custom exception for answer generation errors."""
    pass


def load_env_file(path: Path) -> None:
    """Load environment variables from a .env file."""
    if not path.exists():
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and value:
                    os.environ.setdefault(key, value)


def get_api_key() -> Optional[str]:
    """Get Gemini API key from environment."""
    for env_file in DEFAULT_ENV_FILES:
        load_env_file(env_file)
    return os.environ.get("GEMINI_API_KEY")


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Read a JSONL file and return a list of objects."""
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def load_final_questions(questions_path: Path) -> Dict[str, str]:
    """Load final_questions.jsonl and return a mapping slot_id -> question."""
    questions = {}
    for row in read_jsonl(questions_path):
        slot_id = row.get("slot_id")
        question = row.get("question")
        if slot_id and question:
            questions[slot_id] = question
    return questions


def load_chart_semantic(chart_id: str, charts_dir: Path) -> Optional[Dict[str, Any]]:
    """Load chart semantic file for a given chart ID."""
    candidate_paths = [
        charts_dir / f"{chart_id}.semantic.json",
        charts_dir / "chart_semantic" / f"{chart_id}.semantic.json",
        charts_dir / chart_id / f"{chart_id}.semantic.json",
    ]
    for chart_path in candidate_paths:
        if chart_path.exists():
            try:
                with open(chart_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"  Warning: Could not load chart semantic for {chart_id} from {chart_path}: {e}")
                return None
    return None


def format_star_list(stars: List[Dict[str, Any]]) -> str:
    return ", ".join(
        f"{star.get('name')}{' (' + star['status'] + ')' if star.get('status') else ''}"
        for star in stars or []
        if star.get('name')
    )


def build_prompt_for_answer(
    slot: Dict[str, Any],
    chart_semantic: Optional[Dict[str, Any]],
    goldspans: List[Dict[str, Any]]
) -> str:
    """Build prompt for Gemini to generate answer based on context."""
    
    question = slot.get("question", "")
    chart_id = slot.get("chart_id", "")
    
    # Format chart semantic summary
    chart_summary = "Không có thông tin lá số."
    if chart_semantic:
        core_identity = chart_semantic.get("core_identity", {})
        menh_position = core_identity.get("lai_nhan_cung") or core_identity.get("menh_branch") or "N/A"
        than_position = core_identity.get("than_cu") or core_identity.get("than_branch") or "N/A"
        menh_house = next(
            (p for p in chart_semantic.get("palace_semantics", []) if p.get("house_name") == "Mệnh"),
            None,
        )
        than_house = next(
            (p for p in chart_semantic.get("palace_semantics", []) if p.get("is_than_resident")),
            None,
        )
        menh_stars = format_star_list(menh_house.get("major_stars", []) if menh_house else [])
        than_stars = format_star_list(than_house.get("major_stars", []) if than_house else [])

        chart_summary = f"""Thông tin lá số (Chart {chart_id}):
- Bản Mệnh: {core_identity.get('ban_menh', 'N/A')}
- Cục: {core_identity.get('cuc', 'N/A')}
- Âm Dương Nam Nữ: {core_identity.get('am_duong_nam_nu', 'N/A')}
- Vị trí Mệnh: {menh_position}
- Vị trí Thân: {than_position}
- Chính tinh tại Mệnh: {menh_stars or 'N/A'}
- Chính tinh tại Thân: {than_stars or 'N/A'}
- Chủ Mệnh: {core_identity.get('chu_menh', 'N/A')}
- Chủ Thân: {core_identity.get('chu_than', 'N/A')}
"""
    
    # Format goldspan contexts
    context_parts = []
    for idx, span in enumerate(goldspans, 1):
        doc_id = span.get("doc_id", "N/A")
        quote = span.get("quote", "")
        relevance = span.get("relevance_note", "")
        context_parts.append(f"""[Trích dẫn {idx} - Sách {doc_id}]
{quote}

(Ghi chú: {relevance})
""")
    
    context_text = "\n".join(context_parts) if context_parts else "Không có trích dẫn."
    
    prompt = f"""Bạn là chuyên gia Tử Vi, hãy trả lời câu hỏi dựa trên thông tin lá số và các trích dẫn từ sách Tử Vi được cung cấp.

{chart_summary}

Câu hỏi: {question}

Các trích dẫn từ sách Tử Vi liên quan:
{context_text}

Yêu cầu:
1. Trả lời câu hỏi một cách chính xác dựa trên thông tin lá số và các trích dẫn được cung cấp.
2. Nếu không có trích dẫn thì chỉ dựa vào thông tin lá số để trả lời.
3. Tổng hợp và diễn giải thông tin từ các trích dẫn một cách mạch lạc
4. Trả lời bằng tiếng Việt, từ 50-170 từ
5. Không đưa ra thông tin không có trong context
6. Nếu các trích dẫn mâu thuẫn nhau, hãy chỉ ra và cân nhắc cả hai quan điểm
7. Chỉ trả lời nội dung câu hỏi, không thêm lời mở đầu như "Dựa trên thông tin được cung cấp..." hay gọi ID lá số.

Format output dưới dạng JSON:
{{
  "answer": "Câu trả lời của bạn ở đây",
  "word_count": số từ trong câu trả lời
}}
"""
    return prompt


def gemini_generate_content(
    prompt: str,
    model: str,
    api_key: str,
    timeout: int = 120,
) -> str:
    """Call Gemini API to generate content."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "topP": 0.9,
            "maxOutputTokens": 1024,
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
        raise AnswerGenError(f"Gemini HTTP {exc.code}: {detail}") from exc
    
    candidates = result.get("candidates") or []
    if not candidates:
        raise AnswerGenError(f"Gemini returned no candidates: {result}")
    
    parts_out = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts_out if isinstance(part, dict))
    if not text:
        raise AnswerGenError(f"Gemini returned empty text: {result}")
    return text


def call_llm(
    prompt: str,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    sleep_seconds: float = DEFAULT_SLEEP_SECONDS,
) -> str:
    """Call LLM with retries and fallback model."""
    if not api_key:
        raise AnswerGenError("Missing GEMINI_API_KEY")
    
    last_error: Optional[Exception] = None
    models_to_try = [model]
    if model == DEFAULT_MODEL:
        models_to_try.append(FALLBACK_MODEL)
    
    for model_name in models_to_try:
        for attempt in range(max_retries + 1):
            try:
                return gemini_generate_content(prompt, model_name, api_key)
            except Exception as exc:
                last_error = exc
                if attempt < max_retries:
                    time.sleep(sleep_seconds * (attempt + 1))
                else:
                    break
    
    raise AnswerGenError(f"LLM call failed after retries: {last_error}")


def parse_answer_response(text: str) -> Dict[str, Any]:
    """Parse LLM response JSON."""
    try:
        # Try to extract JSON from markdown code blocks if present
        if "```" in text:
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1)
        
        result = json.loads(text.strip())
        if not isinstance(result, dict) or "answer" not in result:
            raise AnswerGenError("Response missing 'answer' field")
        return result
    except json.JSONDecodeError as e:
        raise AnswerGenError(f"Cannot parse LLM JSON: {e}")


def process_slot(
    slot: Dict[str, Any],
    charts_dir: Path,
    api_key: str,
    rate_limit_sleep: float,
) -> Dict[str, Any]:
    """Process a single slot to generate answer."""
    slot_id = slot.get("slot_id", "unknown")
    chart_id = slot.get("chart_id", "")
    
    print(f"  Processing {slot_id}...")
    
    # Load chart semantic
    chart_semantic = load_chart_semantic(chart_id, charts_dir) if chart_id else None
    
    # Get goldspans
    goldspans = slot.get("gold_context_spans", [])
    if not goldspans:
        print(f"    Warning: No goldspans for {slot_id}")
    
    # Build prompt and call API
    prompt = build_prompt_for_answer(slot, chart_semantic, goldspans)
    
    try:
        response_text = call_llm(prompt, api_key=api_key)
        answer_data = parse_answer_response(response_text)
        
        # Update slot with generated answer
        slot["generated_answer"] = answer_data.get("answer", "")
        slot["word_count"] = answer_data.get("word_count", len(answer_data.get("answer", "").split()))
        
        print(f"    ✓ Generated answer ({slot['word_count']} words)")
        
    except Exception as e:
        print(f"    ✗ Error: {e}")
        slot["generated_answer"] = ""
        slot["word_count"] = 0
        slot["error"] = str(e)
    
    # Rate limiting
    time.sleep(rate_limit_sleep)
    
    return slot


def main():
    parser = argparse.ArgumentParser(description="Generate answers using Gemini API")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input goldspan file")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output file")
    parser.add_argument("--charts-dir", default=str(DEFAULT_CHARTS_DIR), help="Charts directory")
    parser.add_argument("--questions", default=str(DEFAULT_QUESTIONS_PATH), help="Final questions JSONL file")
    parser.add_argument("--slot-id", help="Process only this slot ID")
    parser.add_argument("--limit", type=int, help="Limit number of slots to process")
    parser.add_argument("--start-index", type=int, default=0, help="Start from this index")
    parser.add_argument("--end-index", type=int, help="End at this index")
    parser.add_argument("--append", action="store_true", help="Append to existing output")
    parser.add_argument("--rate-limit-sleep", type=float, default=DEFAULT_RATE_LIMIT_SLEEP,
                        help="Sleep seconds between API calls")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment or .env files")
        sys.exit(1)
    
    # Load input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    questions_path = Path(args.questions)
    if not questions_path.exists():
        print(f"Error: Questions file not found: {questions_path}")
        sys.exit(1)

    print(f"Loading slots from {input_path}")
    print(f"Loading questions from {questions_path}")
    # Load input file contents and extract individual JSON objects using brace-depth tracking
    slots = []
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    object_strings = []
    start = None
    depth = 0
    in_string = False
    escape = False
    
    for idx, ch in enumerate(content):
        if start is None:
            if ch == "{":
                start = idx
                depth = 1
                in_string = False
                escape = False
            continue
        
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                object_strings.append(content[start : idx + 1])
                start = None
    
    # Parse each JSON object
    for obj_str in object_strings:
        try:
            slots.append(json.loads(obj_str))
        except json.JSONDecodeError:
            continue
    
    print(f"Loaded {len(slots)} slots")
    
    question_map = load_final_questions(questions_path)
    if not question_map:
        print(f"Warning: No questions loaded from {questions_path}")

    # Filter slots
    if args.slot_id:
        slots = [s for s in slots if s.get("slot_id") == args.slot_id]
        print(f"Filtered to slot {args.slot_id}: {len(slots)} slots")
    else:
        end_idx = args.end_index if args.end_index else len(slots)
        slots = slots[args.start_index:end_idx]
        if args.limit:
            slots = slots[:args.limit]
        print(f"Processing slots {args.start_index} to {args.start_index + len(slots)}")

    # Add question text from final_questions.jsonl if missing
    for slot in slots:
        slot_id = slot.get("slot_id")
        if slot_id and not slot.get("question"):
            slot_question = question_map.get(slot_id)
            if slot_question:
                slot["question"] = slot_question
            else:
                print(f"  Warning: question not found for {slot_id} in {questions_path}")
    
    if not slots:
        print("No slots to process")
        sys.exit(0)
    
    # Process slots
    charts_dir = Path(args.charts_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    mode = "a" if args.append else "w"
    print(f"\nProcessing {len(slots)} slots...")
    print(f"Output will be {'appended to' if args.append else 'written to'} {output_path}\n")
    
    minimal_output_path = output_path.with_name(f"{output_path.stem}_minimal{output_path.suffix}")
    print(f"Minimal output will also be written to {minimal_output_path}")

    mode = "a" if args.append else "w"
    with open(output_path, mode, encoding="utf-8") as outfile, \
            open(minimal_output_path, mode, encoding="utf-8") as minimal_out:
        for idx, slot in enumerate(slots, 1):
            print(f"[{idx}/{len(slots)}]", end=" ")
            processed_slot = process_slot(slot, charts_dir, api_key, args.rate_limit_sleep)
            json.dump(processed_slot, outfile, ensure_ascii=False)
            outfile.write("\n")
            outfile.flush()

            minimal_row = {
                "slot_id": processed_slot.get("slot_id"),
                "chart_id": processed_slot.get("chart_id"),
                "question": processed_slot.get("question"),
                "generated_answer": processed_slot.get("generated_answer", ""),
            }
            json.dump(minimal_row, minimal_out, ensure_ascii=False)
            minimal_out.write("\n")
            minimal_out.flush()
    
    print(f"\n✓ Done! Full results saved to {output_path}")
    print(f"✓ Minimal results saved to {minimal_output_path}")


if __name__ == "__main__":
    main()