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


def test_get_neo4j_driver_uses_fail_fast_settings(monkeypatch) -> None:
    captured = {}
    sentinel_driver = object()

    def fake_driver(uri: str, **kwargs):
        captured["uri"] = uri
        captured["kwargs"] = kwargs
        return sentinel_driver

    monkeypatch.setattr(clients.GraphDatabase, "driver", fake_driver)
    monkeypatch.setattr(clients.settings, "NEO4J_URI", "neo4j+s://example.databases.neo4j.io")
    monkeypatch.setattr(clients.settings, "NEO4J_USERNAME", "neo4j-user")
    monkeypatch.setattr(clients.settings, "NEO4J_PASSWORD", "neo4j-password")
    monkeypatch.setattr(clients.settings, "NEO4J_CONNECTION_TIMEOUT", 4.0)
    monkeypatch.setattr(clients.settings, "NEO4J_CONNECTION_ACQUISITION_TIMEOUT", 5.0)
    monkeypatch.setattr(clients.settings, "NEO4J_MAX_TRANSACTION_RETRY_TIME", 6.0)

    driver = clients.get_neo4j_driver()

    assert driver is sentinel_driver
    assert captured == {
        "uri": "neo4j+s://example.databases.neo4j.io",
        "kwargs": {
            "auth": ("neo4j-user", "neo4j-password"),
            "connection_timeout": 4.0,
            "connection_acquisition_timeout": 5.0,
            "max_transaction_retry_time": 6.0,
        },
    }
