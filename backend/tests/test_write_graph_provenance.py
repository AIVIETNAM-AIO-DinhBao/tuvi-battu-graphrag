import json
import sys
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

import write_graph_provenance as writer  # noqa: E402


def make_chunk(
    text: str,
    *,
    chunk_id: str = "TVGM_chunk_structure_parent_child_child_000001",
    strategy_id: str = "chunk_structure_parent_child",
) -> dict:
    return {
        "char_end": len(text),
        "char_start": 0,
        "chunk_hash": f"hash-{chunk_id}",
        "chunk_id": chunk_id,
        "chunk_strategy_id": strategy_id,
        "chunk_text": text,
        "chunk_type": "child",
        "domain": "TUVI",
        "metadata": {"source_id": "TVGM"},
        "parent_id": None,
        "provenance": {"source_id": "TVGM", "source_page": 7},
        "section_id": "TVGM_SEC01",
        "source_id": "TVGM",
        "source_name": "Tử Vi Giảng Minh",
        "source_page": 7,
        "text": text,
        "token_count": len(text.split()),
    }


def make_entity(
    chunk: dict,
    surface_text: str,
    entity_type: str,
    canonical_name: str | None = None,
    *,
    entity_id_suffix: str | None = None,
) -> dict:
    text = chunk["chunk_text"]
    start = text.index(surface_text)
    end = start + len(surface_text)
    canonical = canonical_name or surface_text
    suffix = entity_id_suffix or f"{entity_type}_{start}_{end}"
    return {
        "aliases_matched": [surface_text],
        "canonical_name": canonical,
        "char_end": end,
        "char_start": start,
        "chunk_hash": chunk["chunk_hash"],
        "chunk_id": chunk["chunk_id"],
        "chunk_strategy_id": chunk["chunk_strategy_id"],
        "confidence": 0.9,
        "domain": "TUVI",
        "entity_dict_version": "test",
        "entity_id": f"{chunk['chunk_id']}_ENT_{suffix}",
        "entity_type": entity_type,
        "evidence_text": surface_text,
        "extraction_model": "test",
        "needs_review": False,
        "prompt_version": "test",
        "section_id": chunk["section_id"],
        "source_id": chunk["source_id"],
        "source_name": chunk["source_name"],
        "source_page": chunk["source_page"],
        "surface_text": surface_text,
    }


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def smoke_dir(name: str) -> Path:
    path = ROOT_DIR / "pytest-cache-files-writer" / name
    path.mkdir(parents=True, exist_ok=True)
    return path


class FakeRelationClient:
    model_name = "fake-relation"

    def __init__(self, responses: list[object] | None = None) -> None:
        self.responses = list(responses or [[]])
        self.calls = 0

    def extract(self, chunk: dict, entities: list[dict]) -> list[dict]:
        self.calls += 1
        response = self.responses.pop(0) if self.responses else []
        if isinstance(response, Exception):
            raise response
        return response  # type: ignore[return-value]


def no_sleep(_: float) -> None:
    return None


def fake_time() -> float:
    return 0.0


def relation_types(payload: dict) -> set[str]:
    return {relation["relation_type"] for relation in payload["relation_records"]}


def test_rejects_non_tuvi_chunk_domain() -> None:
    chunk = make_chunk("Thiên Mã tại Quan Lộc.")
    chunk["domain"] = "BATU"
    entity = make_entity(chunk | {"domain": "TUVI"}, "Thiên Mã", "Sao")
    entity["domain"] = "TUVI"

    with pytest.raises(ValueError, match="expected TUVI"):
        writer.build_ingest_payload([chunk], [entity], relation_mode="rule", include_ontology=False)


def test_strategy_filter_and_dry_run_do_not_require_databases() -> None:
    first = make_chunk(
        "Thiên Mã tại Quan Lộc.",
        chunk_id="TVGM_chunk_structure_parent_child_child_000001",
        strategy_id="chunk_structure_parent_child",
    )
    second = make_chunk(
        "Thái Dương tại Mệnh.",
        chunk_id="TVGM_chunk_fixed_256_chunk_000001",
        strategy_id="chunk_fixed_256",
    )
    chunks = [first, second]
    entities = [
        make_entity(first, "Thiên Mã", "Sao"),
        make_entity(first, "Quan Lộc", "Cung"),
        make_entity(second, "Thái Dương", "Sao"),
        make_entity(second, "Mệnh", "Cung"),
    ]
    work_dir = smoke_dir("strategy-filter")
    chunk_path = work_dir / "chunks.jsonl"
    entity_path = work_dir / "entities.jsonl"
    summary_path = work_dir / "summary.json"
    write_jsonl(chunk_path, chunks)
    write_jsonl(entity_path, entities)

    summary = writer.run(
        [
            "--chunks-input",
            str(chunk_path),
            "--entities-input",
            str(entity_path),
            "--chunking-strategy",
            "chunk_fixed_256",
            "--dry-run",
            "--mock-llm",
            "--skip-ontology",
            "--summary-output",
            str(summary_path),
        ]
    )

    written_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["dry_run"] is True
    assert summary["chunk_count"] == 1
    assert summary["entity_count"] == 2
    assert written_summary["chunk_count"] == 1
    assert summary["db_write_counts"] == {}


def test_load_gemini_api_keys_supports_combined_and_numbered_keys() -> None:
    env = {
        "GEMINI_API_KEYS": "key-c, key-a",
        "GEMINI_API_KEY": "key-a",
        "GEMINI_API_KEY_2": "key-b",
        "GEMINI_API_KEY_3": "key-c",
        "GEMINI_API_KEY_10": "key-d",
        "GEMINI_API_KEY_EXTRA": "ignored",
    }

    assert writer.load_gemini_api_keys(env) == ["key-c", "key-a", "key-b", "key-d"]


def test_relation_multi_key_adapter_round_robins_successful_requests() -> None:
    chunk = make_chunk("Thien Co o Cung Menh.")
    entities = [make_entity(chunk, "Cung", "Cung")]
    clients = [FakeRelationClient([[], []]), FakeRelationClient([[], []])]
    adapter = writer.MultiKeyGeminiRelationLLMAdapter(
        clients,
        sleep_fn=no_sleep,
        time_fn=fake_time,
    )

    for _ in range(4):
        assert adapter.extract(chunk, entities) == []

    assert [client.calls for client in clients] == [2, 2]
    assert adapter.get_usage_summary()["api_key_usage_counts"] == {"key_1": 2, "key_2": 2}


def test_relation_multi_key_adapter_fails_over_on_rate_limit() -> None:
    chunk = make_chunk("Thien Co o Cung Menh.")
    entities = [make_entity(chunk, "Cung", "Cung")]
    clients = [FakeRelationClient([RuntimeError("429 rate limit")]), FakeRelationClient([[]])]
    adapter = writer.MultiKeyGeminiRelationLLMAdapter(
        clients,
        max_retries=1,
        retry_base_seconds=1,
        sleep_fn=no_sleep,
        time_fn=fake_time,
    )

    assert adapter.extract(chunk, entities) == []
    summary = adapter.get_usage_summary()
    assert [client.calls for client in clients] == [1, 1]
    assert summary["api_key_usage_counts"] == {"key_1": 0, "key_2": 1}
    assert summary["disabled_key_count"] == 0
    assert summary["quota_failover_count"] == 1


def test_relation_multi_key_adapter_disables_daily_quota_key() -> None:
    chunk = make_chunk("Thien Co o Cung Menh.")
    entities = [make_entity(chunk, "Cung", "Cung")]
    clients = [FakeRelationClient([RuntimeError("requests per day quota")]), FakeRelationClient([[]])]
    adapter = writer.MultiKeyGeminiRelationLLMAdapter(
        clients,
        sleep_fn=no_sleep,
        time_fn=fake_time,
    )

    assert adapter.extract(chunk, entities) == []
    summary = adapter.get_usage_summary()
    assert [client.calls for client in clients] == [1, 1]
    assert summary["disabled_key_count"] == 1
    assert summary["quota_failover_count"] == 1


def test_relation_multi_key_adapter_raises_when_all_keys_unavailable() -> None:
    chunk = make_chunk("Thien Co o Cung Menh.")
    entities = [make_entity(chunk, "Cung", "Cung")]
    clients = [
        FakeRelationClient([RuntimeError("requests per day quota")]),
        FakeRelationClient([RuntimeError("daily quota exhausted")]),
    ]
    adapter = writer.MultiKeyGeminiRelationLLMAdapter(
        clients,
        sleep_fn=no_sleep,
        time_fn=fake_time,
    )

    with pytest.raises(writer.GeminiKeysUnavailableError):
        adapter.extract(chunk, entities)
    assert adapter.get_usage_summary()["disabled_key_count"] == 2


def test_rule_derives_thuoc_cung_for_star_at_palace() -> None:
    chunk = make_chunk("Thiên Mã tại Quan Lộc.")
    entities = [
        make_entity(chunk, "Thiên Mã", "Sao"),
        make_entity(chunk, "Quan Lộc", "Cung"),
    ]

    payload = writer.build_ingest_payload([chunk], entities, relation_mode="rule", include_ontology=False)
    relations = payload["relation_records"]

    assert "THUOC_CUNG" in relation_types(payload)
    relation = next(item for item in relations if item["relation_type"] == "THUOC_CUNG")
    assert relation["head_canonical_name"] == "Thiên Mã"
    assert relation["tail_canonical_name"] == "Quan Lộc"
    assert relation["relation_source"] == "rule"


def test_rule_derives_doi_chieu_between_palaces() -> None:
    chunk = make_chunk("Mệnh xung chiếu Thiên Di.")
    entities = [
        make_entity(chunk, "Mệnh", "Cung"),
        make_entity(chunk, "Thiên Di", "Cung"),
    ]

    payload = writer.build_ingest_payload([chunk], entities, relation_mode="rule", include_ontology=False)
    relation = next(item for item in payload["relation_records"] if item["relation_type"] == "DOI_CHIEU")

    assert relation["head_canonical_name"] == "Mệnh"
    assert relation["tail_canonical_name"] == "Thiên Di"
    assert relation["relation_subtype"] == "xung_chiếu"


def test_rule_derives_giap_lien_ke_with_subtype() -> None:
    chunk = make_chunk("Mệnh giáp Kình Đà.")
    entities = [
        make_entity(chunk, "Mệnh", "Cung"),
        make_entity(chunk, "Kình Đà", "ToHop"),
    ]

    payload = writer.build_ingest_payload([chunk], entities, relation_mode="rule", include_ontology=False)
    relation = next(item for item in payload["relation_records"] if item["relation_type"] == "LIEN_KE")

    assert relation["head_canonical_name"] == "Mệnh"
    assert relation["tail_canonical_name"] == "Kình Đà"
    assert relation["relation_subtype"] == "giáp"


def test_rule_derives_luan_giai_relations() -> None:
    chunk = make_chunk("Gặp Hóa Kỵ thì cần xét kỹ.")
    entities = [
        make_entity(chunk, "Hóa Kỵ", "TuHoa"),
        make_entity(
            chunk,
            "Gặp Hóa Kỵ thì cần xét kỹ.",
            "LuanGiai",
            "Gặp Hóa Kỵ thì cần xét kỹ.",
            entity_id_suffix="LUAN_GIAI",
        ),
    ]

    payload = writer.build_ingest_payload([chunk], entities, relation_mode="rule", include_ontology=False)

    assert {"APPLIES_TO", "GIAI_THICH"} <= relation_types(payload)
    applies_to = next(item for item in payload["relation_records"] if item["relation_type"] == "APPLIES_TO")
    giai_thich = next(item for item in payload["relation_records"] if item["relation_type"] == "GIAI_THICH")
    assert applies_to["head_entity_type"] == "LuanGiai"
    assert applies_to["tail_canonical_name"] == "Hóa Kỵ"
    assert giai_thich["head_canonical_name"] == "Hóa Kỵ"
    assert giai_thich["tail_entity_type"] == "LuanGiai"


def test_rule_derives_luu_y_from_warning_trigger() -> None:
    chunk = make_chunk("Cần xét thêm tam phương trước khi luận.")
    entities = [make_entity(chunk, "tam phương", "QuanHeCung", "Tam phương")]

    payload = writer.build_ingest_payload([chunk], entities, relation_mode="rule", include_ontology=False)
    relation = next(item for item in payload["relation_records"] if item["relation_type"] == "LUU_Y")

    assert relation["head_kind"] == "chunk"
    assert relation["tail_canonical_name"] == "Tam phương"
    assert relation["relation_subtype"] == "cần_xét"


def test_validate_rejects_relation_without_evidence_in_chunk() -> None:
    chunk = make_chunk("Thiên Mã tại Quan Lộc.")
    entities = [
        make_entity(chunk, "Thiên Mã", "Sao"),
        make_entity(chunk, "Quan Lộc", "Cung"),
    ]
    relation = writer.make_relation(
        "RELATED_TO",
        writer.relation_endpoint(entities[0]),
        writer.relation_endpoint(entities[1]),
        chunk=chunk,
        evidence_text="not present in chunk",
        relation_source="rule",
    )

    with pytest.raises(ValueError, match="evidence_text is not present"):
        writer.validate_relations(
            [relation],
            {chunk["chunk_hash"]: chunk},
            {entity["entity_id"] for entity in entities},
        )


def test_validate_rejects_relation_unknown_endpoint() -> None:
    chunk = make_chunk("Thiên Mã tại Quan Lộc.")
    entities = [
        make_entity(chunk, "Thiên Mã", "Sao"),
        make_entity(chunk, "Quan Lộc", "Cung"),
    ]
    unknown_tail = writer.relation_endpoint(entities[1])
    unknown_tail["key"] = "missing-entity"
    relation = writer.make_relation(
        "RELATED_TO",
        writer.relation_endpoint(entities[0]),
        unknown_tail,
        chunk=chunk,
        evidence_text=chunk["chunk_text"],
        relation_source="rule",
    )

    with pytest.raises(ValueError, match="unknown tail entity"):
        writer.validate_relations(
            [relation],
            {chunk["chunk_hash"]: chunk},
            {entity["entity_id"] for entity in entities},
        )
