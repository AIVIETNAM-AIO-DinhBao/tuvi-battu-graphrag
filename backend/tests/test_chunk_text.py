import sys
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

import chunk_text  # noqa: E402


CONFIG_PATH = ROOT_DIR / "configs" / "chunking_strategies.yaml"
CORPUS_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "corpus"
ALL_STRATEGIES = [
    "chunk_structure_parent_child",
    "chunk_fixed_256",
    "chunk_fixed_512",
    "chunk_fixed_1024",
    "chunk_sentence_merge",
    "chunk_semantic_embedding",
    "chunk_semantic_embedding_bge_m3",
    "chunk_semantic",
]
OFFICIAL_STRATEGIES = {
    "chunk_fixed_512",
    "chunk_structure_parent_child",
    "chunk_semantic_embedding",
}
REQUIRED_FIELDS = {
    "chunk_id",
    "parent_id",
    "chunk_type",
    "chunk_text",
    "text",
    "source_id",
    "source_name",
    "source_page",
    "domain",
    "chunk_strategy_id",
    "chunk_hash",
    "provenance",
    "metadata",
    "doc_id",
    "section_id",
    "char_start",
    "char_end",
    "token_count",
    "chunking_version",
    "preserved_entities",
}


def sample_registry() -> dict[str, dict]:
    return {
        "TVGM": {"title": "Tử Vi Giảng Minh", "domain": "tu_vi"},
        "TVNL": {"title": "Tử Vi Nghiệm Lý Toàn Thư", "domain": "tu_vi"},
    }


def make_test_unit(text: str, section_id: str = "TVGM_TEST_SEC01") -> chunk_text.SourceUnit:
    return chunk_text.SourceUnit(
        doc_id="TVGM",
        section_id=section_id,
        text=text,
        source_name="Tử Vi Giảng Minh",
        source_page=1,
        domain="TUVI",
        input_format="clean_json",
        page_pdf_start=1,
        page_pdf_end=1,
        page_book=None,
        metadata={"page_pdf": 1},
    )


def test_config_declares_implemented_strategies_with_three_official_baselines() -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)

    assert set(config["strategies"]) == set(ALL_STRATEGIES)
    assert all(chunk_text.get_strategy_config(config, strategy)["implemented"] for strategy in ALL_STRATEGIES)
    official = {
        strategy_id
        for strategy_id, strategy in config["strategies"].items()
        if strategy.get("official_baseline")
    }
    assert official == OFFICIAL_STRATEGIES
    assert config["strategies"]["chunk_semantic"]["semantic_method"] == "lexical_legacy"
    assert config["strategies"]["chunk_semantic_embedding"]["semantic_method"] == "embedding_similarity"
    assert config["strategies"]["chunk_semantic_embedding_bge_m3"]["official_baseline"] is False
    assert config["strategies"]["chunk_semantic_embedding_bge_m3"]["embedding_backend"] == "local"
    assert config["strategies"]["chunk_semantic_embedding_bge_m3"]["output_dimensionality"] == 1024


def test_load_clean_json_records() -> None:
    clean_path = CORPUS_DIR / "TVGM" / "TVGM_clean.json"

    units = chunk_text.load_clean_json(clean_path, sample_registry())

    assert len(units) > 1
    assert units[0].doc_id == "TVGM"
    assert units[0].source_name == "Tử Vi Giảng Minh"
    assert units[0].source_page == 1
    assert units[0].domain == "TUVI"
    assert units[0].input_format == "clean_json"


def test_load_sections_jsonl_records() -> None:
    sections_path = CORPUS_DIR / "TVGM" / "TVGM_sections.jsonl"

    units = chunk_text.load_sections_jsonl(sections_path, sample_registry())

    assert len(units) > 1
    assert units[0].section_id
    assert units[0].source_page == 1
    assert units[0].page_pdf_end == 1
    assert units[0].input_format == "sections_jsonl"


def test_domain_is_tuvi_only() -> None:
    assert chunk_text.normalize_domain(None) == "TUVI"
    assert chunk_text.normalize_domain("tu_vi") == "TUVI"
    with pytest.raises(ValueError, match="Tử Vi-only"):
        chunk_text.normalize_domain("bat_tu")


def test_tvnl_clean_path_is_used_and_thnl_typo_is_reported() -> None:
    tvnl_clean = CORPUS_DIR / "TVNL" / "TVNL_clean.json"
    thnl_typo = CORPUS_DIR / "TVNL" / "THNL_clean.json"

    assert tvnl_clean.exists()
    assert not thnl_typo.exists()
    assert tvnl_clean.resolve() in chunk_text.discover_input_files([tvnl_clean.parent])
    with pytest.raises(FileNotFoundError, match="Did you mean TVNL_clean.json"):
        chunk_text.discover_input_files([thnl_typo])


def test_chunk_hash_changes_when_strategy_changes() -> None:
    common = {
        "chunking_version": "chunking_v1",
        "config_version": "chunking_v1",
        "chunk_type": "child",
        "doc_id": "TVGM",
        "section_id": "TVGM_SEC01",
        "source_page": 1,
        "char_start": 0,
        "char_end": 42,
        "chunk_text": "Thiên Cơ ở Cung Tý.",
    }

    strategy_a_hash = chunk_text.make_chunk_hash(
        chunk_strategy_id="chunk_structure_parent_child", **common
    )
    fixed_hash = chunk_text.make_chunk_hash(chunk_strategy_id="chunk_fixed_256", **common)

    assert strategy_a_hash != fixed_hash


@pytest.mark.parametrize("strategy_id", ALL_STRATEGIES)
def test_all_strategies_generate_chunks_with_shared_schema(strategy_id: str) -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)
    text = (
        "Thiên Cơ ở Cung Tý luận về Giáp Tý và Ngũ Hành. "
        "Cung Mệnh cần xét cùng Cung Thân để giữ bối cảnh. "
        "Tử Vi và Thiên Phủ tạo thành một nhóm luận đoán riêng. "
    ) * 90

    chunks = chunk_text.chunk_units([make_test_unit(text)], config=config, strategy_id=strategy_id)

    assert chunks
    assert all(REQUIRED_FIELDS <= set(chunk) for chunk in chunks)
    assert all(chunk["chunk_strategy_id"] == strategy_id for chunk in chunks)
    assert all(chunk["domain"] == "TUVI" for chunk in chunks)
    assert all(chunk["source_id"] == "TVGM" for chunk in chunks)
    assert all(chunk["source_page"] == 1 for chunk in chunks)
    assert all(chunk["text"] == chunk["chunk_text"] for chunk in chunks)
    assert all(chunk["provenance"]["source_id"] == "TVGM" for chunk in chunks)
    assert all(chunk["metadata"]["chunk_strategy_id"] == strategy_id for chunk in chunks)


@pytest.mark.parametrize(
    ("strategy_id", "max_tokens"),
    [
        ("chunk_fixed_256", 256),
        ("chunk_fixed_512", 512),
        ("chunk_fixed_1024", 1024),
    ],
)
def test_fixed_strategies_respect_configured_token_caps(strategy_id: str, max_tokens: int) -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)
    text = (
        "Thiên Cơ ở Cung Tý luận về Giáp Tý và Ngũ Hành. "
        "Cung Mệnh cần xét cùng Cung Thân để giữ bối cảnh. "
    ) * 140

    chunks = chunk_text.chunk_units([make_test_unit(text)], config=config, strategy_id=strategy_id)

    assert chunks
    assert all(chunk["chunk_type"] == "chunk" for chunk in chunks)
    assert all(chunk["parent_id"] is None for chunk in chunks)
    assert max(chunk["token_count"] for chunk in chunks) <= max_tokens


def test_sentence_merge_does_not_merge_across_source_units() -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)
    first = make_test_unit(
        "Thiên Cơ ở Cung Tý. Cung Mệnh giữ một đoạn riêng. " * 25,
        section_id="TVGM_TEST_SEC01",
    )
    second = make_test_unit(
        "Tử Vi ở Cung Thân. Thiên Phủ giữ một đoạn riêng. " * 25,
        section_id="TVGM_TEST_SEC02",
    )

    chunks = chunk_text.chunk_units(
        [first, second], config=config, strategy_id="chunk_sentence_merge"
    )

    section_ids = {chunk["section_id"] for chunk in chunks}
    assert section_ids == {"TVGM_TEST_SEC01", "TVGM_TEST_SEC02"}
    assert all(chunk["chunk_type"] == "chunk" for chunk in chunks)


def test_legacy_semantic_strategy_splits_clear_lexical_topic_shift() -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)
    strategy = {
        "chunking_version": "chunk_semantic_test_v1",
        "min_tokens": 10,
        "target_tokens": 20,
        "max_tokens": 80,
        "similarity_threshold": 0.2,
    }
    unit = make_test_unit(
        (
            "Thiên Cơ Cung Mệnh luận sao chính tinh. "
            "Thiên Cơ Cung Mệnh xét thêm Tử Vi Thiên Phủ. "
            "Điền Trạch đất nhà ruộng vườn tài sản. "
            "Điền Trạch nhà cửa đất đai sản nghiệp. "
        )
        * 4
    )

    windows = list(
        chunk_text.iter_semantic_windows(
            [unit],
            strategy=strategy,
            protected_terms=["Thiên Cơ", "Cung Mệnh", "Điền Trạch"],
        )
    )

    assert len(windows) >= 2


def test_semantic_embedding_strategy_splits_by_mock_embedding_similarity() -> None:
    strategy = {
        "centroid_policy": "running_centroid",
        "chunking_version": "chunk_semantic_embedding_test_v1",
        "embedding_model_for_chunking": "mock",
        "max_tokens": 30,
        "min_tokens": 4,
        "semantic_method": "embedding_similarity",
        "similarity_threshold": 0.7,
        "target_tokens": 10,
    }
    unit = make_test_unit(
        (
            "alpha beta gamma topic. "
            "alpha beta gamma topic. "
            "money house land asset. "
            "money house land asset. "
        )
        * 2
    )
    events: list[chunk_text.SemanticSimilarityEvent] = []

    windows = chunk_text.iter_semantic_embedding_windows(
        [unit],
        strategy=strategy,
        protected_terms=[],
        embedding_client=chunk_text.MockSemanticEmbeddingClient(),
        events=events,
    )

    assert len(windows) >= 2
    assert any(event.break_reason == "embedding_similarity_below_threshold" for event in events)


def test_semantic_embedding_chunks_include_metadata_and_similarity_report() -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)
    config = dict(config)
    config["strategies"] = dict(config["strategies"])
    strategy = dict(config["strategies"]["chunk_semantic_embedding"])
    strategy.update({"min_tokens": 4, "target_tokens": 10, "max_tokens": 30, "similarity_threshold": 0.7})
    config["strategies"]["chunk_semantic_embedding"] = strategy
    unit = make_test_unit(
        (
            "alpha beta gamma topic. "
            "alpha beta gamma topic. "
            "money house land asset. "
            "money house land asset. "
        )
        * 2
    )
    events: list[chunk_text.SemanticSimilarityEvent] = []

    chunks = chunk_text.chunk_semantic_embedding(
        [unit],
        config=config,
        embedding_client=chunk_text.MockSemanticEmbeddingClient(),
        semantic_events=events,
    )
    report = chunk_text.build_semantic_similarity_report(
        events,
        strategy_id="chunk_semantic_embedding",
        strategy=strategy,
    )

    assert chunks
    first_metadata = chunks[0]["metadata"]
    assert first_metadata["semantic_method"] == "embedding_similarity"
    assert first_metadata["embedding_model_for_chunking"].startswith("mock-semantic-hash")
    assert first_metadata["semantic_similarity_threshold"] == 0.7
    assert "semantic_break_score" in first_metadata
    assert report["chunk_strategy_id"] == "chunk_semantic_embedding"
    assert report["semantic_similarity_threshold"] == 0.7
    assert report["event_count"] == len(events)
    assert report["break_count"] >= 1


class FakeSemanticEmbeddingClient:
    model_name = "gemini-embedding-2"

    def __init__(self, name: str, errors: list[Exception] | None = None) -> None:
        self.name = name
        self.errors = list(errors or [])
        self.calls = 0

    def embed_document(self, text: str) -> list[float]:
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return [float(self.calls), float(len(text))]


def test_semantic_embedding_multi_key_client_round_robins_and_fails_over() -> None:
    first = FakeSemanticEmbeddingClient("key-1", [RuntimeError("429 requests per minute quota")])
    second = FakeSemanticEmbeddingClient("key-2")
    client = chunk_text.MultiKeyGeminiSemanticEmbeddingClient(
        [first, second],
        max_retries=1,
        retry_base_seconds=0,
        max_retry_sleep_seconds=0,
        sleep_fn=lambda _: None,
    )

    vector = client.embed_document("semantic atom")

    assert vector == [1.0, 13.0]
    assert first.calls == 1
    assert second.calls == 1
    assert client.get_usage_summary()["api_key_usage_counts"] == {"key_1": 0, "key_2": 1}
    assert client.get_usage_summary()["quota_failover_count"] == 1


def test_semantic_embedding_multi_key_error_does_not_leak_raw_keys() -> None:
    first = FakeSemanticEmbeddingClient("secret-key-1", [RuntimeError("429 daily quota")])
    second = FakeSemanticEmbeddingClient("secret-key-2", [RuntimeError("429 requests per day")])
    client = chunk_text.MultiKeyGeminiSemanticEmbeddingClient([first, second], sleep_fn=lambda _: None)

    with pytest.raises(RuntimeError, match="All Gemini API keys are unavailable") as exc_info:
        client.embed_document("semantic atom")

    assert "secret-key" not in str(exc_info.value)


def test_semantic_similarity_report_includes_safe_key_usage_summary() -> None:
    report = chunk_text.build_semantic_similarity_report(
        [],
        strategy_id="chunk_semantic_embedding",
        strategy={"semantic_method": "embedding_similarity", "similarity_threshold": 0.7},
        usage_summary={
            "api_key_count": 3,
            "api_key_usage_counts": {"key_1": 2, "key_2": 1, "key_3": 0},
            "disabled_key_count": 1,
            "quota_failover_count": 2,
        },
    )

    assert report["api_key_count"] == 3
    assert report["api_key_usage_counts"] == {"key_1": 2, "key_2": 1, "key_3": 0}
    assert "secret" not in str(report)


def test_semantic_embedding_local_backend_factory_uses_bge_m3(monkeypatch: pytest.MonkeyPatch) -> None:
    created: dict[str, object] = {}

    class FakeLocalClient:
        model_name = "BAAI/bge-m3"

        def __init__(self, **kwargs: object) -> None:
            created.update(kwargs)

    monkeypatch.setattr(chunk_text, "LocalBgeM3EmbeddingClient", FakeLocalClient)

    client = chunk_text.make_semantic_embedding_client(
        {"embedding_backend": "local", "output_dimensionality": 1024},
        mock_embedding=False,
        embedding_backend="local",
        local_embedding_model="BAAI/bge-m3",
        local_embedding_batch_size=8,
    )

    assert isinstance(client, FakeLocalClient)
    assert created["model_name"] == "BAAI/bge-m3"
    assert created["expected_dim"] == 1024
    assert created["batch_size"] == 8


def test_parent_child_schema_and_parent_references() -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)
    text = (
        "Thiên Cơ ở Cung Tý luận về Giáp Tý và Ngũ Hành. "
        "Cung Mệnh cần xét cùng Cung Thân để giữ bối cảnh. "
    ) * 70
    unit = make_test_unit(text)

    chunks = chunk_text.chunk_units(
        [unit], config=config, strategy_id="chunk_structure_parent_child"
    )
    parents = [chunk for chunk in chunks if chunk["chunk_type"] == "parent"]
    children = [chunk for chunk in chunks if chunk["chunk_type"] == "child"]
    parent_ids = {chunk["chunk_id"] for chunk in parents}
    assert parents
    assert children
    assert all(REQUIRED_FIELDS <= set(chunk) for chunk in chunks)
    assert all(parent["parent_id"] is None for parent in parents)
    assert all(child["parent_id"] in parent_ids for child in children)
    assert all(parent["metadata"]["retrieval_unit"] is False for parent in parents)
    assert all(child["metadata"]["retrieval_unit"] is True for child in children)
    assert all(chunk["metadata"]["chunk_strategy_id"] == "chunk_structure_parent_child" for chunk in chunks)
    assert all(chunk["domain"] == "TUVI" for chunk in chunks)
    assert all(chunk["source_id"] == "TVGM" for chunk in chunks)
    assert all(chunk["text"] == chunk["chunk_text"] for chunk in chunks)
    assert all(chunk["provenance"]["source_id"] == "TVGM" for chunk in chunks)
    assert any("Thiên Cơ" in chunk["preserved_entities"] for chunk in chunks)


def test_protected_terms_are_not_split_by_long_segment_fallback() -> None:
    segment = (
        "a b c d Thiên Cơ e f g h Cung Tý i j k l Giáp Tý m n o p"
    )
    atoms = chunk_text.split_long_segment(
        segment,
        absolute_start=0,
        protected_terms=["Thiên Cơ", "Cung Tý", "Giáp Tý"],
        max_tokens=5,
    )
    atom_texts = [atom.text for atom in atoms]

    assert any("Thiên Cơ" in text for text in atom_texts)
    assert any("Cung Tý" in text for text in atom_texts)
    assert any("Giáp Tý" in text for text in atom_texts)
    assert all(not text.endswith("Thiên") for text in atom_texts)
    assert all(not text.startswith("Cơ ") for text in atom_texts)
    assert all(not text.endswith("Cung") for text in atom_texts)
    assert all(not text.startswith("Tý ") for text in atom_texts)
    assert all(not text.endswith("Giáp") for text in atom_texts)
    assert all(not text.startswith("Tý ") for text in atom_texts)
