from app import clients


def test_dense_query_embedding_service_lazy_loads_local_client(monkeypatch) -> None:
    created = {"count": 0}

    class FakeLocalClient:
        def __init__(self, **kwargs):
            created["count"] += 1
            created["kwargs"] = kwargs

        def embed_query(self, text: str) -> list[float]:
            return [float(len(text))]

    monkeypatch.setattr(clients, "LocalBgeM3EmbeddingClient", FakeLocalClient)
    service = clients.DenseQueryEmbeddingService(
        backend="local",
        model_name="BAAI/bge-m3",
        device="cpu",
        slot="bge_m3",
        expected_dim=1024,
    )

    assert service.describe()["slot"] == "bge_m3"
    assert created["count"] == 0
    assert service.embed_query("abc") == [3.0]
    assert created["count"] == 1
    assert created["kwargs"]["device"] == "cpu"
    assert created["kwargs"]["expected_dim"] == 1024


def test_get_dense_query_embedding_service_uses_settings(monkeypatch) -> None:
    monkeypatch.setattr(clients.settings, "DENSE_QUERY_EMBEDDING_BACKEND", "local")
    monkeypatch.setattr(clients.settings, "DENSE_QUERY_EMBEDDING_MODEL", "BAAI/bge-m3")
    monkeypatch.setattr(clients.settings, "DENSE_QUERY_EMBEDDING_DEVICE", "cpu")
    monkeypatch.setattr(clients.settings, "DENSE_QUERY_EMBEDDING_SLOT", "bge_m3")
    monkeypatch.setattr(clients.settings, "DENSE_QUERY_EMBEDDING_DIM", 1024)
    monkeypatch.setattr(clients.settings, "DENSE_QUERY_EMBEDDING_IMPLEMENTATION", "auto")
    monkeypatch.setattr(clients.settings, "DENSE_QUERY_EMBEDDING_NORMALIZE", True)

    clients.get_dense_query_embedding_service.cache_clear()
    service = clients.get_dense_query_embedding_service()

    assert service.describe() == {
        "backend": "local",
        "device": "cpu",
        "expected_dim": 1024,
        "implementation": "auto",
        "model_name": "BAAI/bge-m3",
        "normalize": True,
        "slot": "bge_m3",
    }
