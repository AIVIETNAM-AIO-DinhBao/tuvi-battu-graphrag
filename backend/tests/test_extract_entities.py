import json
import sys
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

import extract_entities  # noqa: E402


CONFIG_PATH = ROOT_DIR / "configs" / "entity_extraction.yaml"


def load_config() -> dict:
    return extract_entities.load_entity_config(CONFIG_PATH)


def make_chunk(
    text: str,
    *,
    chunk_id: str = "TVGM_chunk_structure_parent_child_child_000001",
    strategy_id: str = "chunk_structure_parent_child",
) -> dict:
    return {
        "chunk_hash": f"hash-{chunk_id}",
        "chunk_id": chunk_id,
        "chunk_strategy_id": strategy_id,
        "chunk_text": text,
        "domain": "TUVI",
        "section_id": "TVGM_SEC01",
        "source_id": "TVGM",
        "source_name": "Tử Vi Giảng Minh",
        "source_page": 7,
        "text": text,
    }


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def smoke_dir(name: str) -> Path:
    path = ROOT_DIR / "pytest-cache-files-entity-smoke" / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_canonicalize_core_aliases() -> None:
    config = load_config()

    assert extract_entities.canonicalize_entity("Cung", "Phối", config) == ("Phu Thê", ["Phối"])
    assert extract_entities.canonicalize_entity("Cung", "Bào", config) == ("Huynh Đệ", ["Bào"])
    assert extract_entities.canonicalize_entity("TuHoa", "Hoá Lộc", config) == (
        "Hóa Lộc",
        ["Hoá Lộc"],
    )
    assert extract_entities.canonicalize_entity("CucBanMenh", "Cung Thân", config) == (
        "Cung Thân",
        ["Cung Thân"],
    )
    assert extract_entities.canonicalize_entity("TrangThaiSao", "M", config) == ("Miếu", ["M"])
    assert extract_entities.canonicalize_entity("TrangThaiSao", "V", config) == ("Vượng", ["V"])
    assert extract_entities.canonicalize_entity("TrangThaiSao", "Đ", config) == ("Đắc", ["Đ"])
    assert extract_entities.canonicalize_entity("TrangThaiSao", "H", config) == ("Hãm", ["H"])


def test_validate_rejects_non_tuvi_domain() -> None:
    chunk = make_chunk("Thiên Cơ ở Cung Mệnh.")
    chunk["domain"] = "BATU"

    with pytest.raises(ValueError, match="expected TUVI"):
        extract_entities.validate_chunk(chunk)


def test_validate_rejects_missing_provenance() -> None:
    chunk = make_chunk("Thiên Cơ ở Cung Mệnh.")
    del chunk["chunk_hash"]

    with pytest.raises(ValueError, match="missing required keys: chunk_hash"):
        extract_entities.validate_chunk(chunk)


def test_postprocess_drops_entity_not_present_in_chunk_text() -> None:
    config = load_config()
    chunk = make_chunk("Thiên Cơ ở Cung Mệnh.")
    raw_entities = [
        {
            "entity_type": "Sao",
            "surface_text": "Thái Dương",
            "canonical_name": "Thái Dương",
            "evidence_text": "Thái Dương",
            "confidence": 0.9,
        }
    ]

    records = extract_entities.postprocess_entities(
        raw_entities,
        chunk,
        config,
        extraction_model="mock-dictionary",
    )

    assert records == []


def test_postprocess_preserves_strategy_and_source_provenance() -> None:
    config = load_config()
    chunk = make_chunk("Thiên Mã tại Quan Lộc cho thấy vận động nhiều trong công việc.")
    raw_entities = [
        {
            "char_end": 8,
            "char_start": 0,
            "confidence": 0.9,
            "entity_type": "Sao",
            "evidence_text": "Thiên Mã",
            "surface_text": "Thiên Mã",
        }
    ]

    records = extract_entities.postprocess_entities(
        raw_entities,
        chunk,
        config,
        extraction_model="mock-dictionary",
    )

    assert len(records) == 1
    entity = records[0]
    assert entity["canonical_name"] == "Thiên Mã"
    assert entity["chunk_id"] == chunk["chunk_id"]
    assert entity["chunk_hash"] == chunk["chunk_hash"]
    assert entity["chunk_strategy_id"] == "chunk_structure_parent_child"
    assert entity["source_id"] == "TVGM"
    assert entity["source_page"] == 7
    assert entity["domain"] == "TUVI"


def test_mock_cli_extracts_entities_for_multiple_strategies() -> None:
    chunks = [
        make_chunk(
            "Cung Phối có Hoá Lộc. Gặp Thiên Mã tại Quan Lộc thì cho thấy vận động nhiều trong công việc.",
            chunk_id="TVGM_chunk_structure_parent_child_child_000001",
            strategy_id="chunk_structure_parent_child",
        ),
        make_chunk(
            "Bào có Địa Không Địa Kiếp. Mệnh vô chính diệu cần xét chính chiếu.",
            chunk_id="TVGM_chunk_fixed_256_chunk_000001",
            strategy_id="chunk_fixed_256",
        ),
    ]
    work_dir = smoke_dir("multiple-strategies")
    input_path = work_dir / "chunks.jsonl"
    output_path = work_dir / "entities.jsonl"
    review_path = work_dir / "review.json"
    write_jsonl(input_path, chunks)

    summary = extract_entities.run(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--review-output",
            str(review_path),
            "--mock-llm",
        ]
    )

    records = read_jsonl(output_path)
    canonical_names = {record["canonical_name"] for record in records}
    entity_types = {record["entity_type"] for record in records}
    strategies = {record["chunk_strategy_id"] for record in records}
    review = json.loads(review_path.read_text(encoding="utf-8"))

    assert summary["chunk_count"] == 2
    assert summary["entity_count"] == len(records)
    assert summary["error_count"] == 0
    assert "Phu Thê" in canonical_names
    assert "Hóa Lộc" in canonical_names
    assert "Thiên Mã" in canonical_names
    assert "LuanGiai" in entity_types
    assert strategies == {"chunk_structure_parent_child", "chunk_fixed_256"}
    assert all("entity_id" in record for record in records)
    assert all(record["source_page"] == 7 for record in records)
    assert review["sample_size"] == 2
    assert "excerpt" in review["reviewed_chunks"][0]
    assert "warnings" in review["reviewed_chunks"][0]


def test_mock_cli_filters_by_chunking_strategy() -> None:
    chunks = [
        make_chunk("Thiên Cơ ở Cung Mệnh.", chunk_id="a", strategy_id="chunk_structure_parent_child"),
        make_chunk("Thái Dương ở Cung Ngọ.", chunk_id="b", strategy_id="chunk_fixed_256"),
    ]
    work_dir = smoke_dir("strategy-filter")
    input_path = work_dir / "chunks.jsonl"
    output_path = work_dir / "entities.jsonl"
    write_jsonl(input_path, chunks)

    summary = extract_entities.run(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--chunking-strategy",
            "chunk_fixed_256",
            "--mock-llm",
        ]
    )

    records = read_jsonl(output_path)
    assert summary["chunk_count"] == 1
    assert records
    assert {record["chunk_strategy_id"] for record in records} == {"chunk_fixed_256"}
