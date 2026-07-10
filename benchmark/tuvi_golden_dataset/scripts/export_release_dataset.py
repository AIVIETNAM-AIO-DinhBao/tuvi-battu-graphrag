#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_ANSWERS = BASE_DIR / "annotations" / "answer" / "final_answers.jsonl"
DEFAULT_QUESTIONS = BASE_DIR / "annotations" / "final_questions.jsonl"
DEFAULT_REGISTRY = BASE_DIR / "charts" / "registry" / "chart_registry.json"
DEFAULT_OUTPUT = BASE_DIR / "release" / "golden_v1_release.jsonl"


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        raise FileNotFoundError(f"Missing JSONL file: {path}")
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_final_questions(path: Path) -> Dict[str, Dict[str, Any]]:
    questions = {}
    for row in read_jsonl(path):
        slot_id = row.get("slot_id")
        if not slot_id:
            continue
        questions[slot_id] = row
    return questions


def load_chart_registry(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing chart registry: {path}")
    with path.open("r", encoding="utf-8") as f:
        registry = json.load(f)
    if not isinstance(registry, list):
        raise ValueError(f"Chart registry must be a JSON list: {path}")
    return {item["chart_id"]: item for item in registry if item.get("chart_id")}


def resolve_chart_path(registry_path: Path, registry_item: Dict[str, Any], key: str) -> Optional[Path]:
    rel = registry_item.get(key)
    if not rel:
        return None
    charts_dir = registry_path.parent.parent
    return charts_dir / rel


def normalize_gender(value: Optional[str]) -> Optional[str]:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if normalized in {"nam", "male", "m"}:
        return "Nam"
    if normalized in {"nữ", "nu", "female", "f"}:
        return "Nữ"
    if normalized in {"âm nam", "âm nữ", "dương nam", "dương nữ"}:
        return value.strip().title()
    return value.strip()


def summarize_answer(answer: Optional[str]) -> str:
    if not answer:
        return ""
    text = re.sub(r"\s+", " ", answer.strip())
    sentences = re.split(r"(?<=[.!?。！？])\s+", text)
    if not sentences:
        return text
    summary = sentences[0].strip()
    if len(summary) <= 220:
        return summary
    return summary[:220].rsplit(" ", 1)[0].strip()


def build_release_record(
    answer_row: Dict[str, Any],
    question_row: Optional[Dict[str, Any]],
    registry_row: Dict[str, Any],
    chart_repr: Dict[str, Any],
) -> Dict[str, Any]:
    slot_id = answer_row.get("slot_id") or ""
    question_text = answer_row.get("question") or (question_row or {}).get("question") or ""
    if not question_text:
        raise ValueError(f"Missing question text for slot_id={slot_id}")

    birth_info = registry_row.get("birth_info") or {}
    normalized_birth_info = {
        "date_solar": birth_info.get("birth_date") or birth_info.get("date_solar") or "",
        "time": birth_info.get("birth_time") or birth_info.get("time") or "",
        "timezone": birth_info.get("timezone") or "",
        "gender": normalize_gender(birth_info.get("gender")),
    }

    if not normalized_birth_info["date_solar"] or not normalized_birth_info["time"]:
        raise ValueError(f"Chart registry birth_info missing date or time for chart_id={registry_row.get('chart_id')}")

    labels: Dict[str, Any] = {}
    if question_row:
        topic = question_row.get("topic")
        if topic:
            labels["topic"] = topic
        question_family = question_row.get("question_family")
        if question_family:
            labels["question_family"] = question_family

    return {
        "id": slot_id,
        "chart_id": registry_row.get("chart_id"),
        "birth_info": normalized_birth_info,
        "chart_repr": chart_repr,
        "question": question_text,
        "question_complexity": answer_row.get("question_complexity") or (question_row or {}).get("question_complexity") or "",
        "gold_answer": answer_row.get("generated_answer") or answer_row.get("gold_answer") or "",
        "expected_answer_summary": answer_row.get("expected_answer_summary") or summarize_answer(answer_row.get("generated_answer") or answer_row.get("gold_answer") or ""),
        "gold_context_spans": answer_row.get("gold_context_spans") or [],
        "gold_chunk_ids": answer_row.get("gold_chunk_ids") or [],
        "required_entities": answer_row.get("required_entities") or [],
        "labels": labels,
    }


def assemble_release_dataset(
    answers_path: Path,
    questions_path: Path,
    registry_path: Path,
    output_path: Path,
) -> List[Dict[str, Any]]:
    answers = read_jsonl(answers_path)
    question_map = load_final_questions(questions_path)
    registry_map = load_chart_registry(registry_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    release_rows: List[Dict[str, Any]] = []
    missing_charts: List[str] = []
    missing_questions: List[str] = []

    for answer_row in answers:
        slot_id = answer_row.get("slot_id")
        chart_id = answer_row.get("chart_id")
        if not slot_id or not chart_id:
            raise ValueError(f"Answer row missing slot_id or chart_id: {answer_row}")

        registry_row = registry_map.get(chart_id)
        if not registry_row:
            missing_charts.append(chart_id)
            continue

        chart_path = resolve_chart_path(registry_path, registry_row, "chart_file")
        if not chart_path or not chart_path.exists():
            raise FileNotFoundError(f"Missing chart_repr file for {chart_id}: {chart_path}")

        with chart_path.open("r", encoding="utf-8") as f:
            chart_repr = json.load(f)

        question_row = question_map.get(slot_id)
        if not question_row:
            missing_questions.append(slot_id)

        release_rows.append(build_release_record(answer_row, question_row, registry_row, chart_repr))

    if missing_charts:
        raise ValueError(f"Missing registry entries for charts: {sorted(set(missing_charts))}")
    if missing_questions:
        print(f"Warning: missing question metadata for slots: {sorted(set(missing_questions))}")

    release_rows.sort(key=lambda x: x.get("id") or "")
    with output_path.open("w", encoding="utf-8") as f:
        for row in release_rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ": ")) + "\n")
    return release_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export the final golden release dataset from annotated answers.")
    parser.add_argument("--answers", type=Path, default=DEFAULT_ANSWERS, help="Path to final answers JSONL.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS, help="Path to final questions JSONL.")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY, help="Path to chart registry JSON.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to output release JSONL.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rows = assemble_release_dataset(args.answers, args.questions, args.registry, args.output)
    print(f"Wrote {len(rows)} records to {args.output}")
