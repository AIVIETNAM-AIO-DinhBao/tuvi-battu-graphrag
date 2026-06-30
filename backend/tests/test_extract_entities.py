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
    chunk_type: str | None = None,
) -> dict:
    chunk = {
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
    if chunk_type:
        chunk["chunk_type"] = chunk_type
    return chunk


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


class FakeGeminiClient:
    extraction_model = "fake-gemini"

    def __init__(self, responses: list[object] | None = None) -> None:
        self.responses = list(responses or [[]])
        self.calls = 0

    def extract(self, chunk: dict, config: dict) -> list[dict]:
        self.calls += 1
        response = self.responses.pop(0) if self.responses else []
        if isinstance(response, Exception):
            raise response
        return response  # type: ignore[return-value]


def no_sleep(_: float) -> None:
    return None


def fake_time() -> float:
    return 0.0


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


def test_load_gemini_api_keys_supports_combined_and_numbered_keys() -> None:
    env = {
        "GEMINI_API_KEYS": "key-c, key-a",
        "GEMINI_API_KEY": "key-a",
        "GEMINI_API_KEY_2": "key-b",
        "GEMINI_API_KEY_3": "key-c",
        "GEMINI_API_KEY_10": "key-d",
        "GEMINI_API_KEY_EXTRA": "ignored",
    }

    assert extract_entities.load_gemini_api_keys(env) == ["key-c", "key-a", "key-b", "key-d"]


def test_multi_key_adapter_round_robins_successful_requests() -> None:
    config = load_config()
    chunk = make_chunk("Thien Co o Cung Menh.")
    clients = [FakeGeminiClient([[], []]), FakeGeminiClient([[], []])]
    adapter = extract_entities.MultiKeyGeminiLLMAdapter(
        clients,
        sleep_fn=no_sleep,
        time_fn=fake_time,
    )

    for _ in range(4):
        assert adapter.extract(chunk, config) == []

    assert [client.calls for client in clients] == [2, 2]
    assert adapter.get_usage_summary()["api_key_usage_counts"] == {"key_1": 2, "key_2": 2}


def test_multi_key_adapter_fails_over_on_rate_limit() -> None:
    config = load_config()
    chunk = make_chunk("Thien Co o Cung Menh.")
    clients = [FakeGeminiClient([RuntimeError("429 rate limit")]), FakeGeminiClient([[]])]
    adapter = extract_entities.MultiKeyGeminiLLMAdapter(
        clients,
        max_retries=1,
        retry_base_seconds=1,
        sleep_fn=no_sleep,
        time_fn=fake_time,
    )

    assert adapter.extract(chunk, config) == []
    summary = adapter.get_usage_summary()
    assert [client.calls for client in clients] == [1, 1]
    assert summary["api_key_usage_counts"] == {"key_1": 0, "key_2": 1}
    assert summary["disabled_key_count"] == 0
    assert summary["quota_failover_count"] == 1


def test_multi_key_adapter_disables_daily_quota_key() -> None:
    config = load_config()
    chunk = make_chunk("Thien Co o Cung Menh.")
    clients = [FakeGeminiClient([RuntimeError("requests per day quota")]), FakeGeminiClient([[]])]
    adapter = extract_entities.MultiKeyGeminiLLMAdapter(
        clients,
        sleep_fn=no_sleep,
        time_fn=fake_time,
    )

    assert adapter.extract(chunk, config) == []
    summary = adapter.get_usage_summary()
    assert [client.calls for client in clients] == [1, 1]
    assert summary["disabled_key_count"] == 1
    assert summary["quota_failover_count"] == 1


def test_multi_key_adapter_raises_when_all_keys_unavailable() -> None:
    config = load_config()
    chunk = make_chunk("Thien Co o Cung Menh.")
    clients = [
        FakeGeminiClient([RuntimeError("requests per day quota")]),
        FakeGeminiClient([RuntimeError("daily quota exhausted")]),
    ]
    adapter = extract_entities.MultiKeyGeminiLLMAdapter(
        clients,
        sleep_fn=no_sleep,
        time_fn=fake_time,
    )

    with pytest.raises(extract_entities.GeminiKeysUnavailableError):
        adapter.extract(chunk, config)
    assert adapter.get_usage_summary()["disabled_key_count"] == 2


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
    assert entity["extraction_run_id"] == "manual"
    assert entity["extraction_source"] == "llm"


def _draft_dictionary_output_is_kept_when_llm_returns_empty_mojibake() -> None:
    config = load_config()
    chunk = make_chunk("ThiÃªn CÆ¡ á»Ÿ Cung Má»‡nh.")
    adapter = FakeGeminiClient([[]])

    records = extract_entities.extract_chunk_entities(
        chunk,
        config,
        adapter=adapter,
        llm_augmentation_enabled=True,
        extraction_run_id="run-dict-first",
    )

    canonical_names = {record["canonical_name"] for record in records}
    assert "ThiÃªn CÆ¡" in canonical_names
    assert "Má»‡nh" in canonical_names
    assert all(record["extraction_run_id"] == "run-dict-first" for record in records)
    assert any(record["extraction_source"] == "dictionary" for record in records)


def _draft_llm_augmentation_adds_only_entities_with_evidence_span_mojibake() -> None:
    config = load_config()
    chunk = make_chunk("Äoáº¡n nÃ y nÃ³i vá» Ä‘áº·c cÃ¡ch trong luáº­n giáº£i.")
    adapter = FakeGeminiClient(
        [
            [
                {
                    "confidence": 0.8,
                    "entity_type": "KhaiNiem",
                    "evidence_text": "Ä‘áº·c cÃ¡ch",
                    "surface_text": "Ä‘áº·c cÃ¡ch",
                },
                {
                    "confidence": 0.9,
                    "entity_type": "Sao",
                    "evidence_text": "ThiÃªn MÃ£",
                    "surface_text": "ThiÃªn MÃ£",
                },
            ]
        ]
    )

    records = extract_entities.extract_chunk_entities(
        chunk,
        config,
        adapter=adapter,
        llm_augmentation_enabled=True,
        extraction_run_id="run-llm-span",
    )

    assert any(record["canonical_name"] == "Ä‘áº·c cÃ¡ch" for record in records)
    assert all(record["canonical_name"] != "ThiÃªn MÃ£" for record in records)
    assert any(record["extraction_source"] == "llm" for record in records)


def _draft_dictionary_and_llm_duplicates_are_deduped_by_canonical_span_mojibake() -> None:
    config = load_config()
    chunk = make_chunk("ThiÃªn CÆ¡ á»Ÿ Cung Má»‡nh.")
    adapter = FakeGeminiClient(
        [
            [
                {
                    "char_end": 8,
                    "char_start": 0,
                    "confidence": 0.8,
                    "entity_type": "Sao",
                    "evidence_text": "ThiÃªn CÆ¡",
                    "surface_text": "ThiÃªn CÆ¡",
                }
            ]
        ]
    )

    records = extract_entities.extract_chunk_entities(
        chunk,
        config,
        adapter=adapter,
        llm_augmentation_enabled=True,
        extraction_run_id="run-dedupe",
    )

    thien_co = [record for record in records if record["canonical_name"] == "ThiÃªn CÆ¡"]
    assert len(thien_co) == 1
    assert thien_co[0]["extraction_source"] == "dictionary"


def _draft_dictionary_output_is_kept_when_llm_returns_empty_canonical() -> None:
    config = load_config()
    chunk = make_chunk("Thien Co o Cung Menh.")
    adapter = FakeGeminiClient([[]])

    records = extract_entities.extract_chunk_entities(
        chunk,
        config,
        adapter=adapter,
        llm_augmentation_enabled=True,
        extraction_run_id="run-dict-first",
    )

    canonical_names = {record["canonical_name"] for record in records}
    assert "ThiÃªn CÆ¡" in canonical_names
    assert all(record["extraction_run_id"] == "run-dict-first" for record in records)
    assert any(record["extraction_source"] == "dictionary" for record in records)


def test_llm_augmentation_adds_only_entities_with_evidence_span() -> None:
    config = load_config()
    chunk = make_chunk("Doan nay noi ve dac cach trong luan giai.")
    adapter = FakeGeminiClient(
        [
            [
                {
                    "confidence": 0.8,
                    "entity_type": "KhaiNiem",
                    "evidence_text": "dac cach",
                    "surface_text": "dac cach",
                },
                {
                    "confidence": 0.9,
                    "entity_type": "Sao",
                    "evidence_text": "Thien Ma",
                    "surface_text": "Thien Ma",
                },
            ]
        ]
    )

    records = extract_entities.extract_chunk_entities(
        chunk,
        config,
        adapter=adapter,
        llm_augmentation_enabled=True,
        extraction_run_id="run-llm-span",
    )

    assert any(record["canonical_name"] == "dac cach" for record in records)
    assert all(record["canonical_name"] != "Thien Ma" for record in records)
    assert any(record["extraction_source"] == "llm" for record in records)


def _draft_dictionary_and_llm_duplicates_are_deduped_by_canonical_span_canonical() -> None:
    config = load_config()
    chunk = make_chunk("Thien Co o Cung Menh.")
    adapter = FakeGeminiClient(
        [
            [
                {
                    "char_end": 8,
                    "char_start": 0,
                    "confidence": 0.8,
                    "entity_type": "Sao",
                    "evidence_text": "Thien Co",
                    "surface_text": "Thien Co",
                }
            ]
        ]
    )

    records = extract_entities.extract_chunk_entities(
        chunk,
        config,
        adapter=adapter,
        llm_augmentation_enabled=True,
        extraction_run_id="run-dedupe",
    )

    thien_co = [record for record in records if record["canonical_name"] == "ThiÃªn CÆ¡"]
    assert len(thien_co) == 1
    assert thien_co[0]["extraction_source"] == "dictionary"


def test_dictionary_output_is_kept_when_llm_returns_empty() -> None:
    config = load_config()
    chunk = make_chunk("Thien Co o Cung Menh.")
    adapter = FakeGeminiClient([[]])

    records = extract_entities.extract_chunk_entities(
        chunk,
        config,
        adapter=adapter,
        llm_augmentation_enabled=True,
        extraction_run_id="run-dict-first",
    )

    assert any(record["surface_text"] == "Thien Co" for record in records)
    assert all(record["extraction_run_id"] == "run-dict-first" for record in records)
    assert any(record["extraction_source"] == "dictionary" for record in records)


def test_dictionary_and_llm_duplicates_are_deduped_by_canonical_span() -> None:
    config = load_config()
    chunk = make_chunk("Thien Co o Cung Menh.")
    adapter = FakeGeminiClient(
        [
            [
                {
                    "char_end": 8,
                    "char_start": 0,
                    "confidence": 0.8,
                    "entity_type": "Sao",
                    "evidence_text": "Thien Co",
                    "surface_text": "Thien Co",
                }
            ]
        ]
    )

    records = extract_entities.extract_chunk_entities(
        chunk,
        config,
        adapter=adapter,
        llm_augmentation_enabled=True,
        extraction_run_id="run-dedupe",
    )

    thien_co = [record for record in records if record["surface_text"] == "Thien Co"]
    assert len(thien_co) == 1
    assert thien_co[0]["extraction_source"] == "dictionary"


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
    assert review["strategy_counts"] == {"chunk_fixed_256": 1, "chunk_structure_parent_child": 1}
    assert review["source_counts"] == {"TVGM": 2}
    assert "dictionary" in review["extraction_source_counts"]
    assert "Sao" in review["entity_type_counts"]


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


def _draft_parent_child_extraction_skips_parent_chunks_by_default_mojibake() -> None:
    chunks = [
        make_chunk(
            "ThiÃªn CÆ¡ á»Ÿ Cung Má»‡nh.",
            chunk_id="TVGM_chunk_structure_parent_child_parent_000001",
            chunk_type="parent",
        ),
        make_chunk(
            "ThiÃªn CÆ¡ á»Ÿ Cung Má»‡nh.",
            chunk_id="TVGM_chunk_structure_parent_child_child_000001",
            chunk_type="child",
        ),
    ]
    work_dir = smoke_dir("parent-child-default")
    input_path = work_dir / "chunks.jsonl"
    output_path = work_dir / "entities.jsonl"
    write_jsonl(input_path, chunks)

    summary = extract_entities.run(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--mock-llm",
            "--llm-augmentation",
            "off",
        ]
    )

    records = read_jsonl(output_path)
    assert summary["input_chunk_count"] == 2
    assert summary["chunk_count"] == 1
    assert summary["parent_skipped_count"] == 1
    assert summary["processed_chunk_count"] == 1
    assert {record["chunk_id"] for record in records} == {"TVGM_chunk_structure_parent_child_child_000001"}


def _draft_include_parent_chunks_processes_parent_child_parent_chunks_mojibake() -> None:
    chunks = [
        make_chunk(
            "ThiÃªn CÆ¡ á»Ÿ Cung Má»‡nh.",
            chunk_id="TVGM_chunk_structure_parent_child_parent_000001",
            chunk_type="parent",
        ),
        make_chunk(
            "ThÃ¡i DÆ°Æ¡ng á»Ÿ Cung Ngá».",
            chunk_id="TVGM_chunk_structure_parent_child_child_000001",
            chunk_type="child",
        ),
    ]
    work_dir = smoke_dir("parent-child-include-parent")
    input_path = work_dir / "chunks.jsonl"
    output_path = work_dir / "entities.jsonl"
    write_jsonl(input_path, chunks)

    summary = extract_entities.run(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--include-parent-chunks",
            "--mock-llm",
            "--llm-augmentation",
            "off",
        ]
    )

    records = read_jsonl(output_path)
    assert summary["parent_skipped_count"] == 0
    assert summary["processed_chunk_count"] == 2
    assert {record["chunk_id"] for record in records} == {
        "TVGM_chunk_structure_parent_child_parent_000001",
        "TVGM_chunk_structure_parent_child_child_000001",
    }


def _draft_resume_skips_completed_chunks_and_preserves_existing_output_mojibake() -> None:
    done_chunk = make_chunk("ThiÃªn CÆ¡ á»Ÿ Cung Má»‡nh.", chunk_id="done", strategy_id="chunk_fixed_256")
    todo_chunk = make_chunk("ThÃ¡i DÆ°Æ¡ng á»Ÿ Cung Ngá».", chunk_id="todo", strategy_id="chunk_fixed_256")
    work_dir = smoke_dir("resume-state")
    input_path = work_dir / "chunks.jsonl"
    output_path = work_dir / "entities.jsonl"
    state_path = work_dir / "state.json"
    existing_entity = {
        "canonical_name": "Existing",
        "chunk_id": "done",
        "chunk_hash": "hash-done",
        "chunk_strategy_id": "chunk_fixed_256",
        "entity_id": "existing",
        "entity_type": "KhaiNiem",
        "extraction_run_id": "old-run",
        "extraction_source": "dictionary",
        "source_id": "TVGM",
        "source_page": 7,
    }
    write_jsonl(input_path, [done_chunk, todo_chunk])
    write_jsonl(output_path, [existing_entity])
    state_path.write_text(
        json.dumps({"completed_chunks": {"hash-done": {"chunk_id": "done"}}}),
        encoding="utf-8",
    )

    summary = extract_entities.run(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--state-output",
            str(state_path),
            "--resume",
            "--mock-llm",
            "--llm-augmentation",
            "off",
        ]
    )

    records = read_jsonl(output_path)
    assert summary["resume_skipped_count"] == 1
    assert summary["processed_chunk_count"] == 1
    assert any(record["entity_id"] == "existing" for record in records)
    assert any(record["chunk_id"] == "todo" for record in records)


def test_parent_child_extraction_skips_parent_chunks_by_default() -> None:
    chunks = [
        make_chunk(
            "Thien Co o Cung Menh.",
            chunk_id="TVGM_chunk_structure_parent_child_parent_000001",
            chunk_type="parent",
        ),
        make_chunk(
            "Thien Co o Cung Menh.",
            chunk_id="TVGM_chunk_structure_parent_child_child_000001",
            chunk_type="child",
        ),
    ]
    work_dir = smoke_dir("parent-child-default")
    input_path = work_dir / "chunks.jsonl"
    output_path = work_dir / "entities.jsonl"
    write_jsonl(input_path, chunks)

    summary = extract_entities.run(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--mock-llm",
            "--llm-augmentation",
            "off",
        ]
    )

    records = read_jsonl(output_path)
    assert summary["input_chunk_count"] == 2
    assert summary["chunk_count"] == 1
    assert summary["parent_skipped_count"] == 1
    assert summary["processed_chunk_count"] == 1
    assert {record["chunk_id"] for record in records} == {"TVGM_chunk_structure_parent_child_child_000001"}


def test_include_parent_chunks_processes_parent_child_parent_chunks() -> None:
    chunks = [
        make_chunk(
            "Thien Co o Cung Menh.",
            chunk_id="TVGM_chunk_structure_parent_child_parent_000001",
            chunk_type="parent",
        ),
        make_chunk(
            "Thai Duong o Cung Ngo.",
            chunk_id="TVGM_chunk_structure_parent_child_child_000001",
            chunk_type="child",
        ),
    ]
    work_dir = smoke_dir("parent-child-include-parent")
    input_path = work_dir / "chunks.jsonl"
    output_path = work_dir / "entities.jsonl"
    write_jsonl(input_path, chunks)

    summary = extract_entities.run(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--include-parent-chunks",
            "--mock-llm",
            "--llm-augmentation",
            "off",
        ]
    )

    records = read_jsonl(output_path)
    assert summary["parent_skipped_count"] == 0
    assert summary["processed_chunk_count"] == 2
    assert {record["chunk_id"] for record in records} == {
        "TVGM_chunk_structure_parent_child_parent_000001",
        "TVGM_chunk_structure_parent_child_child_000001",
    }


def test_resume_skips_completed_chunks_and_preserves_existing_output() -> None:
    done_chunk = make_chunk("Thien Co o Cung Menh.", chunk_id="done", strategy_id="chunk_fixed_256")
    todo_chunk = make_chunk("Thai Duong o Cung Ngo.", chunk_id="todo", strategy_id="chunk_fixed_256")
    work_dir = smoke_dir("resume-state")
    input_path = work_dir / "chunks.jsonl"
    output_path = work_dir / "entities.jsonl"
    state_path = work_dir / "state.json"
    existing_entity = {
        "canonical_name": "Existing",
        "chunk_id": "done",
        "chunk_hash": "hash-done",
        "chunk_strategy_id": "chunk_fixed_256",
        "entity_id": "existing",
        "entity_type": "KhaiNiem",
        "extraction_run_id": "old-run",
        "extraction_source": "dictionary",
        "source_id": "TVGM",
        "source_page": 7,
    }
    write_jsonl(input_path, [done_chunk, todo_chunk])
    write_jsonl(output_path, [existing_entity])
    state_path.write_text(
        json.dumps({"completed_chunks": {"hash-done": {"chunk_id": "done"}}}),
        encoding="utf-8",
    )

    summary = extract_entities.run(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--state-output",
            str(state_path),
            "--resume",
            "--mock-llm",
            "--llm-augmentation",
            "off",
        ]
    )

    records = read_jsonl(output_path)
    assert summary["resume_skipped_count"] == 1
    assert summary["processed_chunk_count"] == 1
    assert any(record["entity_id"] == "existing" for record in records)
    assert any(record["chunk_id"] == "todo" for record in records)


def test_resume_ignores_existing_output_without_completed_state() -> None:
    first_chunk = make_chunk("Thien Co o Cung Menh.", chunk_id="first", strategy_id="chunk_fixed_256")
    second_chunk = make_chunk("Thai Duong o Cung Ngo.", chunk_id="second", strategy_id="chunk_fixed_256")
    work_dir = smoke_dir("resume-empty-state")
    input_path = work_dir / "chunks.jsonl"
    output_path = work_dir / "entities.jsonl"
    state_path = work_dir / "state.json"
    stale_entity = {
        "canonical_name": "Stale",
        "chunk_id": "first",
        "chunk_hash": "hash-first",
        "chunk_strategy_id": "chunk_fixed_256",
        "entity_id": "stale",
        "entity_type": "KhaiNiem",
        "extraction_run_id": "dry-run",
        "extraction_source": "dictionary",
        "source_id": "TVGM",
        "source_page": 7,
    }
    write_jsonl(input_path, [first_chunk, second_chunk])
    write_jsonl(output_path, [stale_entity])
    state_path.write_text(json.dumps({"completed_chunks": {}}), encoding="utf-8")

    summary = extract_entities.run(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--state-output",
            str(state_path),
            "--resume",
            "--mock-llm",
            "--llm-augmentation",
            "off",
        ]
    )

    records = read_jsonl(output_path)
    assert summary["resume_skipped_count"] == 0
    assert summary["processed_chunk_count"] == 2
    assert all(record["entity_id"] != "stale" for record in records)


def test_run_loads_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Path] = []
    monkeypatch.setattr(extract_entities, "load_dotenv", lambda path: calls.append(path))
    work_dir = smoke_dir("dotenv-load")
    input_path = work_dir / "chunks.jsonl"
    output_path = work_dir / "entities.jsonl"
    write_jsonl(input_path, [make_chunk("Thien Co o Cung Menh.")])

    extract_entities.run(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--mock-llm",
        ]
    )

    assert calls == [ROOT_DIR / ".env"]


def test_run_stops_cleanly_when_all_keys_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    work_dir = smoke_dir("all-keys-unavailable")
    input_path = work_dir / "chunks.jsonl"
    output_path = work_dir / "entities.jsonl"
    summary_path = work_dir / "partial_summary.json"
    state_path = work_dir / "state.json"
    chunks = [
        make_chunk("Thien Co o Cung Menh.", chunk_id="a"),
        make_chunk("Thai Duong o Cung Ngo.", chunk_id="b"),
    ]
    write_jsonl(input_path, chunks)
    adapter = extract_entities.MultiKeyGeminiLLMAdapter(
        [
            FakeGeminiClient([RuntimeError("requests per day quota")]),
            FakeGeminiClient([RuntimeError("daily quota exhausted")]),
        ],
        sleep_fn=no_sleep,
        time_fn=fake_time,
    )
    monkeypatch.setattr(extract_entities, "make_llm_adapter", lambda args, config: adapter)

    summary = extract_entities.run(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--partial-summary-output",
            str(summary_path),
            "--state-output",
            str(state_path),
        ]
    )

    assert summary["completed"] is False
    assert summary["error_count"] == 1
    assert summary["disabled_key_count"] == 2
    assert summary["processed_chunk_count"] == 0
    assert read_jsonl(output_path) == []
    partial_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert partial_summary["completed"] is False
    assert state["completed_chunks"] == {}


def test_local_qwen_adapter_adds_llm_entities_without_loading_model() -> None:
    config = load_config()
    chunk = make_chunk("Doan nay noi ve dac cach trong luan giai.")

    class FakeJsonClient:
        model_name = "Qwen/Qwen2.5-7B-Instruct"

        def get_usage_summary(self) -> dict:
            return {"llm_backend": "local", "local_llm_call_count": 1}

        def generate_json(self, prompt: str) -> dict:
            assert "chunk_text" in prompt
            return {
                "entities": [
                    {
                        "confidence": 0.8,
                        "entity_type": "KhaiNiem",
                        "evidence_text": "dac cach",
                        "surface_text": "dac cach",
                    }
                ]
            }

    adapter = extract_entities.LocalQwenEntityLLMAdapter(FakeJsonClient())

    records = extract_entities.extract_chunk_entities(
        chunk,
        config,
        adapter=adapter,
        llm_augmentation_enabled=True,
        extraction_run_id="local-run",
    )

    assert any(record["canonical_name"] == "dac cach" for record in records)
    assert any(record["extraction_source"] == "llm" for record in records)
    assert adapter.get_usage_summary()["llm_backend"] == "local"
