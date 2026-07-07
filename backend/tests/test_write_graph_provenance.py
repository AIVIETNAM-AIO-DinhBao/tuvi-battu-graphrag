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
        "extraction_run_id": "entity_run_test",
        "extraction_source": "dictionary",
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

    def extract_many(self, chunk_entity_batches: list[tuple[dict, list[dict]]]) -> dict[str, list[dict]]:
        self.calls += 1
        response = self.responses.pop(0) if self.responses else {}
        if isinstance(response, Exception):
            raise response
        return response  # type: ignore[return-value]


def no_sleep(_: float) -> None:
    return None


def fake_time() -> float:
    return 0.0


def relation_types(payload: dict) -> set[str]:
    return {relation["relation_type"] for relation in payload["relation_records"]}


def test_relation_candidate_filter_drops_review_luan_giai_and_khai_niem_by_default() -> None:
    chunk = make_chunk("SaoA CungA KhaiA LuậnA.")
    sao = make_entity(chunk, "SaoA", "Sao")
    cung = make_entity(chunk, "CungA", "Cung")
    khai_niem = make_entity(chunk, "KhaiA", "KhaiNiem")
    luan_giai = make_entity(chunk, "LuậnA", "LuanGiai")
    sao["needs_review"] = True
    stats: writer.Counter[str] = writer.Counter()
    type_counts: writer.Counter[str] = writer.Counter()

    candidates = writer.filter_relation_candidates(
        [sao, cung, khai_niem, luan_giai],
        candidate_stats=stats,
        dropped_type_counts=type_counts,
    )

    assert [entity["entity_id"] for entity in candidates] == [cung["entity_id"]]
    assert stats["raw_entity_count"] == 4
    assert stats["candidate_entity_count"] == 1
    assert stats["dropped_needs_review_count"] == 1
    assert type_counts["Sao"] == 1
    assert type_counts["KhaiNiem"] == 1
    assert type_counts["LuanGiai"] == 1


def test_relation_candidate_filter_can_include_khai_niem_when_enabled() -> None:
    chunk = make_chunk("CungA KhaiA.")
    cung = make_entity(chunk, "CungA", "Cung")
    khai_niem = make_entity(chunk, "KhaiA", "KhaiNiem")

    candidates = writer.filter_relation_candidates(
        [cung, khai_niem],
        include_khai_niem_candidates=True,
    )

    assert {entity["entity_type"] for entity in candidates} == {"Cung", "KhaiNiem"}


def test_relation_candidate_filter_caps_by_priority_and_reports_summary() -> None:
    chunk = make_chunk("SaoA CungA DiaA NguA ToHopA.")
    entities = [
        make_entity(chunk, "SaoA", "Sao"),
        make_entity(chunk, "CungA", "Cung"),
        make_entity(chunk, "DiaA", "DiaChi"),
        make_entity(chunk, "NguA", "NguHanh"),
        make_entity(chunk, "ToHopA", "ToHop"),
    ]
    stats: writer.Counter[str] = writer.Counter()

    candidates = writer.filter_relation_candidates(
        entities,
        max_candidates=2,
        candidate_stats=stats,
    )

    assert [entity["entity_type"] for entity in candidates] == ["Sao", "Cung"]
    assert stats["capped_chunk_count"] == 1
    assert stats["capped_entity_count"] == 3
    assert stats["candidate_entity_count"] == 2


def test_llm_relation_usage_summary_reports_candidate_filtering() -> None:
    chunk = make_chunk("SaoA CungA KhaiA LuậnA DiaA.")
    sao = make_entity(chunk, "SaoA", "Sao")
    cung = make_entity(chunk, "CungA", "Cung")
    khai_niem = make_entity(chunk, "KhaiA", "KhaiNiem")
    luan_giai = make_entity(chunk, "LuậnA", "LuanGiai")
    dia_chi = make_entity(chunk, "DiaA", "DiaChi")
    sao["needs_review"] = True
    usage_summary: dict = {}

    writer.extract_llm_relations(
        [chunk],
        [sao, cung, khai_niem, luan_giai, dia_chi],
        mock_llm=True,
        model_name="mock",
        max_relation_candidates_per_chunk=1,
        usage_summary=usage_summary,
    )

    assert usage_summary["relation_candidate_raw_entity_count"] == 5
    assert usage_summary["relation_candidate_count"] == 1
    assert usage_summary["relation_candidate_dropped_needs_review_count"] == 1
    assert usage_summary["relation_candidate_capped_chunk_count"] == 1
    assert usage_summary["relation_candidate_dropped_type_counts"]["KhaiNiem"] == 1
    assert usage_summary["relation_candidate_dropped_type_counts"]["LuanGiai"] == 1


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
    review_path = work_dir / "relation_review.json"
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
            "--relation-review-output",
            str(review_path),
        ]
    )

    written_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    written_review = json.loads(review_path.read_text(encoding="utf-8"))
    assert summary["dry_run"] is True
    assert summary["chunk_count"] == 1
    assert summary["entity_count"] == 2
    assert written_summary["chunk_count"] == 1
    assert written_review["relation_count"] >= 1
    assert "relation_counts" in written_review["summary"]
    assert summary["db_write_counts"] == {}


def test_dry_run_exports_portable_payload_dir() -> None:
    chunk = make_chunk("ThiÃªn MÃ£ táº¡i Quan Lá»™c.")
    entities = [
        make_entity(chunk, "ThiÃªn MÃ£", "Sao"),
        make_entity(chunk, "Quan Lá»™c", "Cung"),
    ]
    work_dir = smoke_dir("payload-export")
    chunk_path = work_dir / "chunks.jsonl"
    entity_path = work_dir / "entities.jsonl"
    payload_dir = work_dir / "payload"
    write_jsonl(chunk_path, [chunk])
    write_jsonl(entity_path, entities)

    summary = writer.run(
        [
            "--chunks-input",
            str(chunk_path),
            "--entities-input",
            str(entity_path),
            "--chunking-strategy",
            "chunk_structure_parent_child",
            "--dry-run",
            "--mock-llm",
            "--payload-output-dir",
            str(payload_dir),
        ]
    )

    payload = writer.load_payload_output_dir(payload_dir)
    assert summary["payload_output_dir"] == str(payload_dir)
    assert payload["summary"]["chunk_count"] == 1
    assert len(payload["chunk_records"]) == 1
    assert len(payload["entity_records"]) >= 2
    assert len(payload["mention_records"]) >= 2


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


def test_relation_multi_key_adapter_batches_successful_requests() -> None:
    first = make_chunk("Thien Ma tai Quan Loc.", chunk_id="first")
    second = make_chunk("Thai Duong tai Menh.", chunk_id="second")
    first_entities = [make_entity(first, "Thien Ma", "Sao"), make_entity(first, "Quan Loc", "Cung")]
    second_entities = [make_entity(second, "Thai Duong", "Sao"), make_entity(second, "Menh", "Cung")]
    clients = [FakeRelationClient([{"first": [], "second": []}]), FakeRelationClient([{}])]
    adapter = writer.MultiKeyGeminiRelationLLMAdapter(
        clients,
        sleep_fn=no_sleep,
        time_fn=fake_time,
    )

    assert adapter.extract_many([(first, first_entities), (second, second_entities)]) == {
        "first": [],
        "second": [],
    }
    assert [client.calls for client in clients] == [1, 0]
    assert adapter.get_usage_summary()["api_key_usage_counts"] == {"key_1": 1, "key_2": 0}


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


def test_rule_skips_luan_giai_relations_by_default() -> None:
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

    assert "APPLIES_TO" not in relation_types(payload)
    assert "GIAI_THICH" not in relation_types(payload)


def test_rule_derives_luan_giai_relations_when_enabled() -> None:
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

    payload = writer.build_ingest_payload(
        [chunk],
        entities,
        relation_mode="rule",
        include_ontology=False,
        include_luan_giai_relations=True,
    )

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


def test_parent_child_chunks_create_structural_edges() -> None:
    parent = make_chunk(
        "Parent context.",
        chunk_id="TVGM_chunk_structure_parent_child_parent_000001",
    )
    parent["chunk_type"] = "parent"
    child = make_chunk(
        "Thiên Mã tại Quan Lộc.",
        chunk_id="TVGM_chunk_structure_parent_child_child_000001",
    )
    child["parent_id"] = parent["chunk_id"]
    entities = [
        make_entity(child, "Thiên Mã", "Sao"),
        make_entity(child, "Quan Lộc", "Cung"),
    ]

    payload = writer.build_ingest_payload([parent, child], entities, relation_mode="rule", include_ontology=False)
    relations = payload["relation_records"]

    assert {"HAS_PARENT", "CONTAINS_CHILD"} <= relation_types(payload)
    has_parent = next(relation for relation in relations if relation["relation_type"] == "HAS_PARENT")
    contains_child = next(relation for relation in relations if relation["relation_type"] == "CONTAINS_CHILD")
    assert has_parent["head_key"] == child["chunk_hash"]
    assert has_parent["tail_key"] == parent["chunk_hash"]
    assert contains_child["head_key"] == parent["chunk_hash"]
    assert contains_child["tail_key"] == child["chunk_hash"]
    assert payload["summary"]["parent_child_relation_count"] == 2


def test_relation_type_pair_validation_rejects_invalid_thuoc_cung() -> None:
    chunk = make_chunk("Mệnh tại Thiên Mã.")
    cung = make_entity(chunk, "Mệnh", "Cung")
    sao = make_entity(chunk, "Thiên Mã", "Sao")
    relation = writer.make_relation(
        "THUOC_CUNG",
        writer.relation_endpoint(cung),
        writer.relation_endpoint(sao),
        chunk=chunk,
        evidence_text=chunk["chunk_text"],
        relation_source="rule",
    )

    with pytest.raises(ValueError, match="invalid type pair"):
        writer.validate_relations(
            [relation],
            {chunk["chunk_hash"]: chunk},
            {cung["entity_id"], sao["entity_id"]},
        )


def test_llm_relation_postprocess_counts_invalid_drops() -> None:
    chunk = make_chunk("Thiên Mã tại Quan Lộc.")
    entities = [
        make_entity(chunk, "Thiên Mã", "Sao"),
        make_entity(chunk, "Quan Lộc", "Cung"),
    ]
    drop_counts: writer.Counter[str] = writer.Counter()
    raw_relations = [
        {
            "relation_type": "THUOC_CUNG",
            "head_entity_id": entities[0]["entity_id"],
            "tail_entity_id": "missing",
            "evidence_text": chunk["chunk_text"],
        },
        {
            "relation_type": "THUOC_CUNG",
            "head_entity_id": entities[0]["entity_id"],
            "tail_entity_id": entities[1]["entity_id"],
            "evidence_text": "not in chunk",
        },
    ]

    records = writer.postprocess_llm_relations(raw_relations, chunk, entities, drop_counts)

    assert records == []
    assert drop_counts["unknown_or_same_endpoint"] == 1
    assert drop_counts["evidence_not_in_chunk"] == 1


def test_llm_relation_postprocess_rejects_luan_giai_and_disabled_relation_types() -> None:
    chunk = make_chunk("SaoA luận tốt.")
    sao = make_entity(chunk, "SaoA", "Sao")
    luan_giai = make_entity(chunk, "luận tốt", "LuanGiai")
    drop_counts: writer.Counter[str] = writer.Counter()
    raw_relations = [
        {
            "relation_type": "RELATED_TO",
            "head_entity_id": luan_giai["entity_id"],
            "tail_entity_id": sao["entity_id"],
            "evidence_text": chunk["chunk_text"],
        },
        {
            "relation_type": "APPLIES_TO",
            "head_entity_id": luan_giai["entity_id"],
            "tail_entity_id": sao["entity_id"],
            "evidence_text": chunk["chunk_text"],
        },
    ]

    records = writer.postprocess_llm_relations(raw_relations, chunk, [sao, luan_giai], drop_counts)

    assert records == []
    assert drop_counts["endpoint_luan_giai_not_allowed"] == 1
    assert drop_counts["relation_type_not_allowed"] == 1


def test_llm_relation_postprocess_rejects_needs_review_endpoint() -> None:
    chunk = make_chunk("SaoA tai CungA.")
    sao = make_entity(chunk, "SaoA", "Sao")
    cung = make_entity(chunk, "CungA", "Cung")
    sao["needs_review"] = True
    drop_counts: writer.Counter[str] = writer.Counter()
    raw_relations = [
        {
            "relation_type": "THUOC_CUNG",
            "head_entity_id": sao["entity_id"],
            "tail_entity_id": cung["entity_id"],
            "evidence_text": chunk["chunk_text"],
        }
    ]

    records = writer.postprocess_llm_relations(raw_relations, chunk, [sao, cung], drop_counts)

    assert records == []
    assert drop_counts["endpoint_needs_review_not_allowed"] == 1


def test_llm_relation_postprocess_drops_invalid_type_pair() -> None:
    chunk = make_chunk("Giap Ty.")
    thien_can = make_entity(chunk, "Giap", "ThienCan")
    dia_chi = make_entity(chunk, "Ty", "DiaChi")
    drop_counts: writer.Counter[str] = writer.Counter()
    raw_relations = [
        {
            "relation_type": "THUOC_CUNG",
            "head_entity_id": thien_can["entity_id"],
            "tail_entity_id": dia_chi["entity_id"],
            "evidence_text": chunk["chunk_text"],
        }
    ]

    records = writer.postprocess_llm_relations(raw_relations, chunk, [thien_can, dia_chi], drop_counts)

    assert records == []
    assert drop_counts["invalid_relation_type_pair"] == 1


def test_canonical_relation_aggregation_groups_evidence_relations() -> None:
    first = make_chunk("Thiên Mã tại Quan Lộc.", chunk_id="first")
    second = make_chunk("Thiên Mã tại Quan Lộc.", chunk_id="second")
    entities = [
        make_entity(first, "Thiên Mã", "Sao"),
        make_entity(first, "Quan Lộc", "Cung"),
        make_entity(second, "Thiên Mã", "Sao"),
        make_entity(second, "Quan Lộc", "Cung"),
    ]

    payload = writer.build_ingest_payload([first, second], entities, relation_mode="rule", include_ontology=False)

    canonical = [
        relation
        for relation in payload["canonical_relation_records"]
        if relation["relation_type"] == "THUOC_CUNG"
    ]
    assert len(canonical) == 1
    assert canonical[0]["evidence_count"] == 2
    assert canonical[0]["source_ids"] == ["TVGM"]
    assert canonical[0]["chunk_strategy_ids"] == ["chunk_structure_parent_child"]


def test_chunk_records_include_citation_metadata() -> None:
    chunk = make_chunk("Thiên Mã tại Quan Lộc.")
    entities = [make_entity(chunk, "Thiên Mã", "Sao")]

    record = writer.build_chunk_records([chunk], entities)[0]

    assert record["metadata"]["chunk_hash"] == chunk["chunk_hash"]
    assert record["metadata"]["chunk_type"] == "child"
    assert record["metadata"]["source_page"] == 7
    assert record["metadata"]["token_count"] == chunk["token_count"]


def test_llm_relation_resume_skips_completed_chunk_state(monkeypatch: pytest.MonkeyPatch) -> None:
    chunk = make_chunk("Thiên Mã tại Quan Lộc.")
    entities = [
        make_entity(chunk, "Thiên Mã", "Sao"),
        make_entity(chunk, "Quan Lộc", "Cung"),
    ]
    relation = writer.make_relation(
        "THUOC_CUNG",
        writer.relation_endpoint(entities[0]),
        writer.relation_endpoint(entities[1]),
        chunk=chunk,
        evidence_text=chunk["chunk_text"],
        relation_source="llm",
    )
    work_dir = smoke_dir("relation-resume")
    state_path = work_dir / "graph_relation_state.json"
    writer.write_relation_state(
        state_path,
        {
            "completed_chunks": {
                writer.relation_state_key(chunk): {
                    "chunk_id": chunk["chunk_id"],
                    "relation_count": 1,
                    "relation_records": [relation],
                }
            }
        },
    )
    calls = {"count": 0}

    class CountingAdapter:
        model_name = "counting"

        def extract(self, *_: object) -> list[dict]:
            calls["count"] += 1
            return []

    monkeypatch.setattr(writer, "MockRelationLLMAdapter", CountingAdapter)

    records = writer.extract_llm_relations(
        [chunk],
        entities,
        mock_llm=True,
        model_name="mock",
        state_output=state_path,
        resume=True,
    )

    assert calls["count"] == 0
    assert records == [relation]


def test_llm_relation_resume_sanitizes_invalid_relation_records(monkeypatch: pytest.MonkeyPatch) -> None:
    chunk = make_chunk("Giap Ty.")
    entities = [
        make_entity(chunk, "Giap", "ThienCan"),
        make_entity(chunk, "Ty", "DiaChi"),
    ]
    invalid_relation = writer.make_relation(
        "THUOC_CUNG",
        writer.relation_endpoint(entities[0]),
        writer.relation_endpoint(entities[1]),
        chunk=chunk,
        evidence_text=chunk["chunk_text"],
        relation_source="llm",
    )
    work_dir = smoke_dir("relation-resume-sanitize-invalid-v1")
    state_path = work_dir / "graph_relation_state.json"
    writer.write_relation_state(
        state_path,
        {
            "completed_chunks": {
                writer.relation_state_key(chunk): {
                    "chunk_id": chunk["chunk_id"],
                    "relation_count": 1,
                    "relation_records": [invalid_relation],
                }
            }
        },
    )
    calls = {"count": 0}
    drop_counts: writer.Counter[str] = writer.Counter()

    class CountingAdapter:
        model_name = "counting"

        def extract(self, *_: object) -> list[dict]:
            calls["count"] += 1
            return []

    monkeypatch.setattr(writer, "MockRelationLLMAdapter", CountingAdapter)

    records = writer.extract_llm_relations(
        [chunk],
        entities,
        mock_llm=True,
        model_name="mock",
        state_output=state_path,
        resume=True,
        drop_counts=drop_counts,
    )

    state = json.loads(state_path.read_text(encoding="utf-8"))
    entry = state["completed_chunks"][writer.relation_state_key(chunk)]
    assert calls["count"] == 0
    assert records == []
    assert entry["relation_count"] == 0
    assert entry["relation_records"] == []
    assert "sanitized_at" in entry
    assert drop_counts["resumed_invalid_relation_type_pair"] == 1


def test_relation_state_key_distinguishes_duplicate_chunk_hashes(monkeypatch: pytest.MonkeyPatch) -> None:
    first = make_chunk("SaoA tai CungA.", chunk_id="first")
    second = make_chunk("SaoB tai CungB.", chunk_id="second")
    second["chunk_hash"] = first["chunk_hash"]
    entities = [
        make_entity(first, "SaoA", "Sao"),
        make_entity(first, "CungA", "Cung"),
        make_entity(second, "SaoB", "Sao"),
        make_entity(second, "CungB", "Cung"),
    ]
    work_dir = smoke_dir("relation-duplicate-hash-state")
    state_path = work_dir / "graph_relation_state.json"
    calls = {"count": 0}

    class CountingAdapter:
        model_name = "counting"

        def extract(self, *_: object) -> list[dict]:
            calls["count"] += 1
            return []

    monkeypatch.setattr(writer, "MockRelationLLMAdapter", CountingAdapter)

    writer.extract_llm_relations(
        [first, second],
        entities,
        mock_llm=True,
        model_name="mock",
        state_output=state_path,
    )

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert calls["count"] == 2
    assert set(state["completed_chunks"]) == {
        writer.relation_state_key(first),
        writer.relation_state_key(second),
    }


def test_llm_relation_batch_missing_chunk_response_is_not_completed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = make_chunk("Thien Ma tai Quan Loc.", chunk_id="first")
    second = make_chunk("Thai Duong tai Menh.", chunk_id="second")
    entities = [
        make_entity(first, "Thien Ma", "Sao"),
        make_entity(first, "Quan Loc", "Cung"),
        make_entity(second, "Thai Duong", "Sao"),
        make_entity(second, "Menh", "Cung"),
    ]
    work_dir = smoke_dir("relation-batch-missing-v2")
    state_path = work_dir / "graph_relation_state.json"
    drop_counts: writer.Counter[str] = writer.Counter()

    class MissingBatchAdapter:
        model_name = "missing-batch"

        def extract_many(self, batch: list[tuple[dict, list[dict]]]) -> dict[str, list[dict]]:
            return {"first": []}

    monkeypatch.setattr(writer, "MockRelationLLMAdapter", MissingBatchAdapter)

    records = writer.extract_llm_relations(
        [first, second],
        entities,
        mock_llm=True,
        model_name="mock",
        llm_batch_size=2,
        state_output=state_path,
        drop_counts=drop_counts,
    )

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert records == []
    assert set(state["completed_chunks"]) == {writer.relation_state_key(first)}
    assert drop_counts["missing_batch_chunk_response"] == 1


def test_llm_relation_batch_json_error_falls_back_to_single_chunk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = make_chunk("Thien Ma tai Quan Loc.", chunk_id="first")
    second = make_chunk("Thai Duong tai Menh.", chunk_id="second")
    first_entities = [make_entity(first, "Thien Ma", "Sao"), make_entity(first, "Quan Loc", "Cung")]
    second_entities = [make_entity(second, "Thai Duong", "Sao"), make_entity(second, "Menh", "Cung")]
    entities = [*first_entities, *second_entities]
    drop_counts: writer.Counter[str] = writer.Counter()
    usage_summary: dict = {}

    class FallbackBatchAdapter:
        model_name = "fallback-batch"

        def __init__(self) -> None:
            self.single_calls = 0

        def extract_many(self, batch: list[tuple[dict, list[dict]]]) -> dict[str, list[dict]]:
            raise ValueError("bad json")

        def extract(self, chunk: dict, chunk_entities: list[dict]) -> list[dict]:
            self.single_calls += 1
            return [
                {
                    "confidence": 0.9,
                    "evidence_text": chunk["chunk_text"],
                    "head_entity_id": chunk_entities[0]["entity_id"],
                    "relation_type": "THUOC_CUNG",
                    "tail_entity_id": chunk_entities[1]["entity_id"],
                }
            ]

    adapter = FallbackBatchAdapter()
    monkeypatch.setattr(writer, "MockRelationLLMAdapter", lambda: adapter)

    records = writer.extract_llm_relations(
        [first, second],
        entities,
        mock_llm=True,
        model_name="mock",
        llm_batch_size=2,
        drop_counts=drop_counts,
        usage_summary=usage_summary,
    )

    assert len(records) == 2
    assert adapter.single_calls == 2
    assert drop_counts["batch_response_error"] == 1
    assert usage_summary["llm_relation_request_count"] == 3
    assert usage_summary["relation_extraction_completed"] is True


def test_llm_relation_progress_logging(capsys: pytest.CaptureFixture[str]) -> None:
    chunk = make_chunk("Thien Ma tai Quan Loc.")
    entities = [
        make_entity(chunk, "Thien Ma", "Sao"),
        make_entity(chunk, "Quan Loc", "Cung"),
    ]

    writer.extract_llm_relations(
        [chunk],
        entities,
        mock_llm=True,
        model_name="mock",
        progress_interval=1,
    )

    captured = capsys.readouterr()
    assert "[relation-progress]" in captured.err
    assert "processed=1/1" in captured.err


def test_local_qwen_relation_adapter_uses_existing_entity_ids() -> None:
    chunk = make_chunk("ThiÃªn MÃ£ táº¡i Quan Lá»™c.")
    entities = [
        make_entity(chunk, "ThiÃªn MÃ£", "Sao"),
        make_entity(chunk, "Quan Lá»™c", "Cung"),
    ]

    class FakeJsonClient:
        model_name = "Qwen/Qwen2.5-7B-Instruct"

        def get_usage_summary(self) -> dict:
            return {"llm_backend": "local", "local_llm_call_count": 1}

        def generate_json(self, prompt: str) -> dict:
            assert entities[0]["entity_id"] in prompt
            return {
                "relations": [
                    {
                        "confidence": 0.9,
                        "evidence_text": chunk["chunk_text"],
                        "head_entity_id": entities[0]["entity_id"],
                        "relation_type": "THUOC_CUNG",
                        "tail_entity_id": entities[1]["entity_id"],
                    }
                ]
            }

    adapter = writer.LocalQwenRelationLLMAdapter(FakeJsonClient())
    raw = adapter.extract(chunk, entities)
    records = writer.postprocess_llm_relations(raw, chunk, entities)

    assert len(records) == 1
    assert records[0]["relation_source"] == "llm"
    assert records[0]["relation_type"] == "THUOC_CUNG"
    assert adapter.get_usage_summary()["llm_backend"] == "local"
