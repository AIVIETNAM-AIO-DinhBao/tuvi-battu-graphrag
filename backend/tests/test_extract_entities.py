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
        ]
    )

    assert summary["completed"] is False
    assert summary["error_count"] == 1
    assert summary["disabled_key_count"] == 2
    assert read_jsonl(output_path) == []
