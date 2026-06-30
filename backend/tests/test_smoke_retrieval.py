import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

import smoke_retrieval  # noqa: E402


class FakeNode(dict):
    pass


class FakeRecord(dict):
    pass


class FakeTransaction:
    def __init__(self) -> None:
        self.cypher = ""
        self.params: dict[str, object] = {}

    def run(self, query: str, **params: object) -> list[FakeRecord]:
        self.cypher = query
        self.params = params
        return [make_record()]


def make_record(score: float = 0.87) -> FakeRecord:
    return FakeRecord(
        {
            "node": FakeNode(
                {
                    "chunk_hash": "hash-1",
                    "chunk_id": "TVGM_chunk_structure_parent_child_child_000001",
                    "chunk_strategy_id": "chunk_structure_parent_child",
                    "domain": "TUVI",
                    "source_id": "TVGM",
                    "source_name": "Tử Vi Giảng Minh",
                    "source_page": 7,
                    "text": "Thiên Mã tại Quan Lộc cần xét Hóa Kỵ.",
                }
            ),
            "score": score,
        }
    )


def test_normalize_hit_preserves_retrieval_contract() -> None:
    hit = smoke_retrieval.normalize_hit(make_record())

    assert hit["chunk_id"] == "TVGM_chunk_structure_parent_child_child_000001"
    assert hit["chunk_hash"] == "hash-1"
    assert hit["chunk_strategy_id"] == "chunk_structure_parent_child"
    assert hit["domain"] == "TUVI"
    assert hit["source_id"] == "TVGM"
    assert hit["source_page"] == 7
    assert hit["score"] == 0.87
    assert "Thiên Mã" in hit["text_preview"]


def test_sanitize_fulltext_query_removes_lucene_operators() -> None:
    query = smoke_retrieval.sanitize_fulltext_query('Cung Phu Thê + Hóa Kỵ: "cần xét"?')

    assert "+" not in query
    assert ":" not in query
    assert '"' not in query
    assert "Cung Phu Thê" in query


def test_build_fulltext_query_uses_or_terms_and_removes_light_stopwords() -> None:
    query = smoke_retrieval.build_fulltext_query('Cung Phu Thê + Hóa Kỵ: "cần xét"?')

    assert query == "Cung OR Phu OR Thê OR Hóa OR Kỵ OR cần OR xét"


def test_dense_retrieval_uses_explicit_candidate_k() -> None:
    tx = FakeTransaction()

    hits = smoke_retrieval.dense_retrieval_tx(
        tx,
        embedding=[0.1, 0.2],
        candidate_k=500,
        top_k=5,
        domain="TUVI",
        source_id="TVGM",
        chunk_strategy_id="chunk_structure_parent_child",
    )

    assert tx.params["candidate_k"] == 500
    assert tx.params["top_k"] == 5
    assert hits[0]["source_id"] == "TVGM"


def test_sparse_retrieval_uses_non_conflicting_fulltext_param() -> None:
    tx = FakeTransaction()

    hits = smoke_retrieval.sparse_retrieval_tx(
        tx,
        query='Cung Phu Thê + Hóa Kỵ: "cần xét"?',
        top_k=5,
        domain="TUVI",
        source_id="TVGM",
        chunk_strategy_id="chunk_structure_parent_child",
    )

    assert "$fulltext_query" in tx.cypher
    assert "fulltext_query" in tx.params
    assert "query" not in tx.params
    assert tx.params["fulltext_query"] == "Cung OR Phu OR Thê OR Hóa OR Kỵ OR cần OR xét"
    assert hits[0]["source_id"] == "TVGM"


def test_build_query_result_requires_dense_and_sparse_hits() -> None:
    dense = [smoke_retrieval.normalize_hit(make_record(0.9))]
    sparse = [smoke_retrieval.normalize_hit(make_record(1.2))]

    passed = smoke_retrieval.build_query_result("Thiên Mã", dense, sparse)
    failed = smoke_retrieval.build_query_result("Thiên Mã", dense, [])

    assert passed["passed"] is True
    assert passed["dense_hit_count"] == 1
    assert passed["sparse_hit_count"] == 1
    assert failed["passed"] is False


def test_assert_smoke_passed_rejects_empty_hits() -> None:
    results = [
        smoke_retrieval.build_query_result(
            "Thiên Mã",
            [smoke_retrieval.normalize_hit(make_record())],
            [],
        )
    ]

    with pytest.raises(ValueError, match="Dense/sparse smoke retrieval returned empty hits"):
        smoke_retrieval.assert_smoke_passed(results)


def test_make_embedding_client_passes_expected_dimension(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeEmbeddingClient:
        model_name = "fake"

    def fake_make_embedding_client(args: SimpleNamespace) -> FakeEmbeddingClient:
        captured["model_name"] = args.model
        captured["expected_dim"] = args.expected_dim
        captured["requests_per_minute"] = args.requests_per_minute
        captured["max_retries"] = args.max_retries
        return FakeEmbeddingClient()

    monkeypatch.setattr(smoke_retrieval.embed_chunks, "make_embedding_client", fake_make_embedding_client)

    args = SimpleNamespace(
        mock_embedding=False,
        model="gemini-embedding-2",
        expected_dim=768,
        requests_per_minute=90.0,
        max_retries=6,
    )

    client = smoke_retrieval.make_embedding_client(args)

    assert isinstance(client, FakeEmbeddingClient)
    assert captured == {
        "model_name": "gemini-embedding-2",
        "expected_dim": 768,
        "requests_per_minute": 90.0,
        "max_retries": 6,
    }


def test_parse_args_infers_bge_slot_defaults() -> None:
    args = smoke_retrieval.parse_args(["--embedding-backend", "local"])

    assert args.embedding_slot == "bge_m3"
    assert args.expected_dim == 1024
    assert args.vector_index_name == "chunkVectorBgeM3"


def test_retrieval_diagnostics_uses_slot_specific_properties() -> None:
    tx = FakeTransaction()

    diagnostics = smoke_retrieval.retrieval_diagnostics_tx(
        tx,
        domain="TUVI",
        source_id="TVGM",
        chunk_strategy_id="chunk_structure_parent_child",
        embedding_slot="bge_m3",
    )

    assert "c.embedding_bge_m3 IS NULL" in tx.cypher
    assert "c.embedding_bge_m3_model" in tx.cypher
    assert diagnostics["embedding_property"] == "embedding_bge_m3"
    assert diagnostics["embedding_slot"] == "bge_m3"
