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
        "domain": "TUVI",
        "existing_embedding_text_hash": None,
        "mention_keywords": ["Thiên Mã", "Quan Lộc", "Thiên Mã", "", " Hóa Kỵ "],
        "section_id": "TVGM_SEC01",
        "source_id": "TVGM",
        "source_name": "Tử Vi Giảng Minh",
        "source_page": 7,
        "text": "Thiên Mã tại Quan Lộc cần xét Hóa Kỵ.",
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

    assert keys == ["key-1", "key-2"]


def test_load_gemini_api_keys_falls_back_to_legacy_env_names() -> None:
    keys = embed_chunks.load_gemini_api_keys(
        {
            "GEMINI_API_KEYS": "",
            "GEMINI_API_KEY": "key-1",
            "GEMINI_API_KEY_2": "key-2",
        }
    )

    assert keys == ["key-1", "key-2"]


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
    assert update["embedding_model"] == "mock-embedding-768"
    assert update["embedding_dim"] == 768
    assert len(update["embedding"]) == 768
    assert update["title"] == "TVGM_SEC01"
    assert update["keywords"] == "Hóa Kỵ Quan Lộc Thiên Mã"
    assert update["embedding_text_hash"] == embed_chunks.embedding_text_hash(make_chunk()["text"])


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
        error=error,
    )

    assert summary["completed"] is False
    assert summary["db_write_counts"]["embedded_chunks"] == 864
    assert summary["update_count"] == 870
    assert summary["error"] == "RuntimeError: quota exhausted"


def test_assert_required_indexes_online() -> None:
    indexes = [
        {"name": "chunkVector", "state": "ONLINE"},
        {"name": "chunkFulltext", "state": "ONLINE"},
    ]

    embed_chunks.assert_required_indexes_online(indexes)


def test_assert_required_indexes_online_rejects_missing_index() -> None:
    with pytest.raises(ValueError, match="Missing Neo4j index"):
        embed_chunks.assert_required_indexes_online([{"name": "chunkVector", "state": "ONLINE"}])
