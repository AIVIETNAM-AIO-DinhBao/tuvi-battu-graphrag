import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

import embed_chunks  # noqa: E402


class FakeEmbeddingClient:
    def __init__(self, name: str, errors: list[Exception] | None = None) -> None:
        self.model_name = "gemini-embedding-2"
        self.name = name
        self.errors = list(errors or [])
        self.calls = 0

    def embed_document(self, text: str, title: str | None = None) -> list[float]:
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        seed = f"{self.name}:{title}:{text}"
        return embed_chunks.mock_embedding(seed, expected_dim=768)

    def embed_query(self, text: str) -> list[float]:
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return embed_chunks.mock_embedding(f"{self.name}:{text}", expected_dim=768)


def make_chunk() -> dict:
    return {
        "chunk_hash": "hash-1",
        "chunk_id": "TVGM_chunk_structure_parent_child_child_000001",
        "chunk_strategy_id": "chunk_structure_parent_child",
        "chunk_type": "child",
        "domain": "TUVI",
        "existing_embedding_text_hash": None,
        "mention_keywords": ["Thiên Mã", "Quan Lộc", "Thiên Mã", "", " Hóa Kỵ "],
        "parent_id": "TVGM_chunk_structure_parent_child_parent_000001",
        "retrieval_unit": True,
        "section_id": "TVGM_SEC01",
        "source_id": "TVGM",
        "source_name": "Tử Vi Giảng Minh",
        "source_page": 7,
        "text": "Thiên Mã tại Quan Lộc cần xét Hóa Kỵ.",
    }


def test_embedding_slot_config_maps_bge_m3_fields() -> None:
    config = embed_chunks.embedding_slot_config("bge_m3")

    assert config["slot"] == "bge_m3"
    assert config["vector_property"] == "embedding_bge_m3"
    assert config["vector_index_name"] == "chunkVectorBgeM3"
    assert config["expected_dim"] == 1024
    assert config["metadata_fields"] == {
        "embedded_at": "embedding_bge_m3_embedded_at",
        "embedding_dim": "embedding_bge_m3_dim",
        "embedding_model": "embedding_bge_m3_model",
        "embedding_text_hash": "embedding_bge_m3_text_hash",
    }


def test_select_chunks_query_skips_existing_embeddings_by_default() -> None:
    cypher = embed_chunks.build_select_chunks_cypher(force=False, limit=10)

    assert "c.embedding IS NULL" in cypher
    assert "c.embedding_model IS NULL" not in cypher
    assert "c.embedding_text_hash AS existing_embedding_text_hash" not in cypher
    assert "LIMIT $limit" in cypher


def test_select_chunks_query_force_does_not_filter_existing_embeddings() -> None:
    cypher = embed_chunks.build_select_chunks_cypher(force=True, limit=None)

    assert "c.embedding IS NULL" not in cypher
    assert "LIMIT $limit" not in cypher


def test_select_chunks_query_child_only_filters_parent_child_retrieval_units() -> None:
    cypher = embed_chunks.build_select_chunks_cypher(force=False, limit=10, child_only=True)

    assert "c.chunk_type = 'child'" in cypher
    assert "c.retrieval_unit = true" in cypher
    assert "c.parent_id AS parent_id" in cypher
    assert "c.chunk_type AS chunk_type" in cypher


def test_select_chunks_query_uses_bge_slot_property() -> None:
    cypher = embed_chunks.build_select_chunks_cypher(force=False, limit=10, embedding_slot="bge_m3")

    assert "c.embedding_bge_m3 IS NULL" in cypher
    assert "c.embedding IS NULL" not in cypher


def test_child_only_policy_only_applies_to_parent_child_without_override() -> None:
    assert embed_chunks.should_use_child_only_policy("chunk_structure_parent_child", False) is True
    assert embed_chunks.should_use_child_only_policy("chunk_structure_parent_child", True) is False
    assert embed_chunks.should_use_child_only_policy("chunk_fixed_512", False) is False


def test_mock_embedding_is_deterministic_768_dimensional() -> None:
    first = embed_chunks.mock_embedding("Thiên Mã", expected_dim=768)
    second = embed_chunks.mock_embedding("Thiên Mã", expected_dim=768)

    assert len(first) == 768
    assert first == second
    assert any(value != 0 for value in first)


def test_validate_embedding_dimension_rejects_mismatch() -> None:
    with pytest.raises(ValueError, match="expected 768, got 2"):
        embed_chunks.validate_embedding_dimension([0.1, 0.2], 768)


def test_load_gemini_api_keys_prefers_comma_separated_env() -> None:
    keys = embed_chunks.load_gemini_api_keys(
        {
            "GEMINI_API_KEYS": " key-1, key-2, key-1, ,",
            "GEMINI_API_KEY": "fallback-1",
            "GEMINI_API_KEY_2": "fallback-2",
        }
    )

    assert keys == ["key-1", "key-2", "fallback-1", "fallback-2"]


def test_load_gemini_api_keys_falls_back_to_legacy_env_names() -> None:
    keys = embed_chunks.load_gemini_api_keys(
        {
            "GEMINI_API_KEYS": "",
            "GEMINI_API_KEY": "key-1",
            "GEMINI_API_KEY_2": "key-2",
            "GEMINI_API_KEY_4": "key-4",
            "GEMINI_API_KEY_10": "key-10",
            "GEMINI_API_KEY_3": "key-3",
        }
    )

    assert keys == ["key-1", "key-2", "key-3", "key-4", "key-10"]


def test_normalize_keywords_deduplicates_and_sorts() -> None:
    keywords = embed_chunks.normalize_keywords(["Thiên Mã", "Quan Lộc", "thiên mã", " Hóa Kỵ "])

    assert keywords == "Hóa Kỵ Quan Lộc Thiên Mã"


def test_prepare_embedding_updates_preserves_metadata() -> None:
    client = embed_chunks.MockEmbeddingClient()
    updates = embed_chunks.prepare_embedding_updates([make_chunk()], client, expected_dim=768)

    assert len(updates) == 1
    update = updates[0]
    assert update["chunk_hash"] == "hash-1"
    assert update["chunk_id"] == "TVGM_chunk_structure_parent_child_child_000001"
    assert update["chunk_type"] == "child"
    assert update["embedding_model"] == "mock-embedding-768"
    assert update["embedding_dim"] == 768
    assert len(update["embedding"]) == 768
    assert update["title"] == "TVGM_SEC01"
    assert update["keywords"] == "Hóa Kỵ Quan Lộc Thiên Mã"
    assert update["parent_id"] == "TVGM_chunk_structure_parent_child_parent_000001"
    assert update["retrieval_unit"] is True
    assert update["embedding_text_hash"] == embed_chunks.embedding_text_hash(make_chunk()["text"])


def test_prepare_embedding_updates_marks_bge_slot_metadata() -> None:
    client = embed_chunks.MockEmbeddingClient(expected_dim=1024)
    updates = embed_chunks.prepare_embedding_updates(
        [make_chunk()],
        client,
        expected_dim=1024,
        embedding_slot="bge_m3",
    )

    assert updates[0]["embedding_slot"] == "bge_m3"
    assert updates[0]["vector_index_name"] == "chunkVectorBgeM3"
    assert updates[0]["vector_property"] == "embedding_bge_m3"


def test_prepare_embedding_update_skips_empty_text() -> None:
    client = embed_chunks.MockEmbeddingClient()
    chunk = make_chunk()
    chunk["text"] = ""
    chunk["chunk_text"] = ""

    update = embed_chunks.prepare_embedding_update(chunk, client, expected_dim=768)

    assert update is None


def test_rate_limit_error_detection_handles_quota_messages() -> None:
    exc = RuntimeError("429 ResourceExhausted: requests per minute quota exceeded")

    assert embed_chunks.is_rate_limit_error(exc) is True
    assert embed_chunks.is_rate_limit_error(RuntimeError("permission denied")) is False


def test_daily_quota_error_detection_handles_per_day_messages() -> None:
    exc = RuntimeError("429 quota exceeded for GenerateRequestsPerDayPerProjectPerModel-FreeTier")

    assert embed_chunks.is_daily_quota_error(exc) is True
    assert embed_chunks.is_daily_quota_error(RuntimeError("requests per minute quota exceeded")) is False


def test_gemini_client_stops_immediately_on_daily_quota() -> None:
    calls = {"count": 0}

    class FakeModels:
        def embed_content(self, **_: object) -> object:
            calls["count"] += 1
            raise RuntimeError("429 GenerateRequestsPerDayPerProjectPerModel-FreeTier exceeded")

    client = object.__new__(embed_chunks.GeminiEmbeddingClient)
    client._client = SimpleNamespace(models=FakeModels())
    client._types = SimpleNamespace(EmbedContentConfig=lambda **kwargs: kwargs)
    client.model_name = "gemini-embedding-2"
    client.output_dimensionality = 768
    client.requests_per_minute = None
    client.max_retries = 8
    client.retry_base_seconds = 0.0
    client.max_retry_sleep_seconds = 0.0
    client.stop_on_daily_quota = True
    client._rate_limiter = embed_chunks.RequestRateLimiter(None)

    with pytest.raises(RuntimeError, match="daily quota appears exhausted"):
        client._embed("text")

    assert calls["count"] == 1


def test_multi_key_client_round_robins_successful_requests() -> None:
    client_1 = FakeEmbeddingClient("key-1")
    client_2 = FakeEmbeddingClient("key-2")
    client = embed_chunks.MultiKeyGeminiEmbeddingClient([client_1, client_2], retry_base_seconds=0)

    for index in range(5):
        vector = client.embed_document(f"text-{index}")
        assert len(vector) == 768

    assert client_1.calls == 3
    assert client_2.calls == 2
    assert client.get_usage_summary()["api_key_usage_counts"] == {"key_1": 3, "key_2": 2}


def test_multi_key_client_fails_over_after_rate_limit() -> None:
    client_1 = FakeEmbeddingClient("key-1", [RuntimeError("429 requests per minute quota exceeded")])
    client_2 = FakeEmbeddingClient("key-2")
    client = embed_chunks.MultiKeyGeminiEmbeddingClient(
        [client_1, client_2],
        max_retries=1,
        retry_base_seconds=0,
        max_retry_sleep_seconds=0,
        sleep_fn=lambda _: None,
    )

    vector = client.embed_document("text")

    assert len(vector) == 768
    assert client_1.calls == 1
    assert client_2.calls == 1
    assert client.quota_failover_count == 1
    assert client.disabled_key_count == 0


def test_multi_key_client_disables_daily_quota_key() -> None:
    client_1 = FakeEmbeddingClient("key-1", [RuntimeError("429 GenerateRequestsPerDayPerProjectPerModel")])
    client_2 = FakeEmbeddingClient("key-2")
    client = embed_chunks.MultiKeyGeminiEmbeddingClient(
        [client_1, client_2],
        retry_base_seconds=0,
        max_retry_sleep_seconds=0,
        sleep_fn=lambda _: None,
    )

    first = client.embed_document("text-1")
    second = client.embed_document("text-2")

    assert len(first) == 768
    assert len(second) == 768
    assert client_1.calls == 1
    assert client_2.calls == 2
    assert client.disabled_key_count == 1


def test_multi_key_client_all_keys_unavailable_error_does_not_leak_keys() -> None:
    client_1 = FakeEmbeddingClient("secret-key-1", [RuntimeError("429 GenerateRequestsPerDayPerProjectPerModel")])
    client_2 = FakeEmbeddingClient("secret-key-2", [RuntimeError("429 GenerateRequestsPerDayPerProjectPerModel")])
    client = embed_chunks.MultiKeyGeminiEmbeddingClient([client_1, client_2], sleep_fn=lambda _: None)

    with pytest.raises(RuntimeError, match="All Gemini API keys are unavailable") as exc_info:
        client.embed_document("text")

    assert "secret-key" not in str(exc_info.value)


def test_parse_args_defaults_to_safe_requests_per_minute() -> None:
    args = embed_chunks.parse_args([])

    assert args.requests_per_minute == embed_chunks.DEFAULT_REQUESTS_PER_MINUTE
    assert args.max_retries == 6
    assert args.max_retry_sleep_seconds == embed_chunks.DEFAULT_MAX_RETRY_SLEEP_SECONDS
    assert args.stop_on_daily_quota is True
    assert args.progress_every == 25
    assert args.include_parent_chunks is False
    assert args.smoke_query == "Tu Vi"
    assert args.smoke_limit == 5
    assert args.embedding_backend is None
    assert args.embedding_slot == "gemini"
    assert args.expected_dim == 768
    assert args.model == "gemini-embedding-2"
    assert args.vector_index_name == "chunkVector"


def test_parse_args_infers_bge_slot_from_local_embedding_flags() -> None:
    args = embed_chunks.parse_args(["--embedding-backend", "local"])

    assert args.embedding_slot == "bge_m3"
    assert args.expected_dim == 1024
    assert args.model == "BAAI/bge-m3"
    assert args.vector_index_name == "chunkVectorBgeM3"


def test_parse_args_rejects_slot_override_conflicts() -> None:
    with pytest.raises(ValueError, match="conflicts with --embedding-slot 'bge_m3'"):
        embed_chunks.parse_args(["--embedding-slot", "bge_m3", "--expected-dim", "768"])


def test_local_embedding_client_factory_uses_bge_m3(monkeypatch: pytest.MonkeyPatch) -> None:
    created: dict[str, object] = {}

    class FakeLocalClient:
        model_name = "BAAI/bge-m3"

        def __init__(self, **kwargs: object) -> None:
            created.update(kwargs)

    monkeypatch.setattr(embed_chunks, "LocalBgeM3EmbeddingClient", FakeLocalClient)
    args = embed_chunks.parse_args(
        [
            "--embedding-backend",
            "local",
            "--model",
            "BAAI/bge-m3",
            "--expected-dim",
            "1024",
            "--local-embedding-batch-size",
            "4",
        ]
    )

    client = embed_chunks.make_embedding_client(args)

    assert isinstance(client, FakeLocalClient)
    assert created["model_name"] == "BAAI/bge-m3"
    assert created["expected_dim"] == 1024
    assert created["batch_size"] == 4


def test_offline_embedding_mode_writes_artifact_without_db_env() -> None:
    work_dir = ROOT_DIR / "pytest-cache-files-embed-offline" / "artifact"
    work_dir.mkdir(parents=True, exist_ok=True)
    chunk_path = work_dir / "chunks.jsonl"
    output_path = work_dir / "embeddings.jsonl"
    summary_path = work_dir / "summary.json"
    smoke_path = work_dir / "retrieval.json"
    chunk = make_chunk()
    chunk_path.write_text(json.dumps(chunk, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = embed_chunks.run(
        [
            "--chunks-input",
            str(chunk_path),
            "--output",
            str(output_path),
            "--summary-output",
            str(summary_path),
            "--retrieval-smoke-output",
            str(smoke_path),
            "--mock-embedding",
            "--source-id",
            "TVGM",
            "--chunking-strategy",
            "chunk_structure_parent_child",
        ]
    )

    records = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
    assert summary["mode"] == "offline_artifact"
    assert summary["completed"] is True
    assert summary["update_count"] == 1
    assert records[0]["chunk_id"] == chunk["chunk_id"]
    assert len(records[0]["embedding"]) == 768
    assert json.loads(smoke_path.read_text(encoding="utf-8"))["diagnostics"]["mode"] == "offline_artifact"


def test_build_run_summary_marks_partial_failure() -> None:
    args = embed_chunks.parse_args(["--source-id", "TVGM"])
    error = RuntimeError("quota exhausted")

    summary = embed_chunks.build_run_summary(
        args=args,
        db_counts={"embedded_chunks": 864},
        embedding_model="gemini-embedding-2",
        selected_chunks=919,
        update_count=870,
        completed=False,
        selected_chunk_records=[make_chunk()],
        updates=[],
        parent_skipped_count=49,
        error=error,
    )

    assert summary["completed"] is False
    assert summary["db_write_counts"]["embedded_chunks"] == 864
    assert summary["update_count"] == 870
    assert summary["parent_skipped_count"] == 49
    assert summary["selected_chunk_type_counts"] == {"child": 1}
    assert summary["keyword_coverage"] == {"chunk_count": 0, "coverage": 0.0, "with_keywords": 0}
    assert summary["error"] == "RuntimeError: quota exhausted"


def test_assert_required_indexes_online() -> None:
    indexes = [
        {
            "name": "chunkVector",
            "state": "ONLINE",
            "properties": ["embedding"],
            "options": {"indexConfig": {"vector.dimensions": 768}},
        },
        {"name": "chunkFulltext", "state": "ONLINE"},
    ]

    embed_chunks.assert_required_indexes_online(indexes, embedding_slot="gemini", vector_index_name="chunkVector")


def test_assert_required_indexes_online_rejects_missing_index() -> None:
    with pytest.raises(ValueError, match="Missing Neo4j index"):
        embed_chunks.assert_required_indexes_online([{"name": "chunkVector", "state": "ONLINE"}])


def test_assert_required_indexes_online_rejects_slot_dim_mismatch() -> None:
    indexes = [
        {
            "name": "chunkVectorBgeM3",
            "state": "ONLINE",
            "properties": ["embedding_bge_m3"],
            "options": {"indexConfig": {"vector.dimensions": 768}},
        },
        {"name": "chunkFulltext", "state": "ONLINE"},
    ]

    with pytest.raises(ValueError, match="expected 1024"):
        embed_chunks.assert_required_indexes_online(
            indexes,
            {"chunkVectorBgeM3", "chunkFulltext"},
            embedding_slot="bge_m3",
            vector_index_name="chunkVectorBgeM3",
        )


def test_run_summary_reports_embedded_chunk_types_and_keyword_coverage() -> None:
    args = embed_chunks.parse_args(["--source-id", "TVGM"])
    chunk = make_chunk()
    update = {
        "chunk_hash": chunk["chunk_hash"],
        "chunk_id": chunk["chunk_id"],
        "chunk_type": "child",
        "keywords": "Hóa Kỵ Quan Lộc Thiên Mã",
    }

    summary = embed_chunks.build_run_summary(
        args=args,
        db_counts={"embedded_chunks": 1},
        embedding_model="mock",
        selected_chunks=1,
        update_count=1,
        completed=True,
        selected_chunk_records=[chunk],
        updates=[update],
        parent_skipped_count=1,
    )

    assert summary["embedded_chunk_type_counts"] == {"child": 1}
    assert summary["keyword_coverage"]["coverage"] == 1.0
    assert summary["parent_skipped_count"] == 1


def test_retrieval_smoke_queries_filter_strategy_and_child_type() -> None:
    dense = embed_chunks.build_dense_retrieval_smoke_cypher(child_only=True, limit=3)
    sparse = embed_chunks.build_sparse_retrieval_smoke_cypher(child_only=True, limit=3)

    assert "chunkVector" in dense
    assert "chunkFulltext" in sparse
    assert "node.chunk_strategy_id = $chunk_strategy_id" in dense
    assert "node.chunk_type = 'child'" in dense
    assert "node.retrieval_unit = true" in sparse


def test_parent_expansion_diagnostics_counts_found_parents() -> None:
    dense_hits = [
        {"chunk_id": "child-1", "parent_id": "parent-1"},
        {"chunk_id": "child-2", "parent_id": "parent-2"},
    ]
    sparse_hits = [{"chunk_id": "child-1", "parent_id": "parent-1"}]
    parents = [{"chunk_id": "parent-1"}]

    diagnostics = embed_chunks.build_parent_expansion_diagnostics(dense_hits, sparse_hits, parents)

    assert diagnostics["child_hits_with_parent"] == 2
    assert diagnostics["parent_fetch_count"] == 1
    assert diagnostics["parent_expansion_hit_rate"] == 0.5
