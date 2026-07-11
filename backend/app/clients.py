import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import requests
from neo4j import GraphDatabase
from supabase import create_client
from .config import settings


ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from local_embeddings import LocalBgeM3EmbeddingClient


class LangfuseClient:
    def __init__(self, base_url: str, public_key: str, secret_key: str):
        self.base_url = base_url.rstrip("/")
        self.public_key = public_key
        self.secret_key = secret_key
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "x-api-key": self.secret_key,
        })

    def log_event(self, event_name: str, payload: dict):
        url = f"{self.base_url}/events"
        body = {
            "event": event_name,
            "public_key": self.public_key,
            "payload": payload,
        }
        response = self.session.post(url, json=body)
        response.raise_for_status()
        return response.json()


class DenseQueryEmbeddingService:
    def __init__(
        self,
        *,
        backend: str,
        model_name: str,
        device: str | None,
        slot: str,
        expected_dim: int,
        implementation: str = "auto",
        normalize: bool = True,
    ) -> None:
        self.backend = backend
        self.model_name = model_name
        self.device = device
        self.slot = slot
        self.expected_dim = expected_dim
        self.implementation = implementation
        self.normalize = normalize
        self._client: Any | None = None

    def _ensure_client(self) -> LocalBgeM3EmbeddingClient:
        if self.backend != "local":
            raise ValueError(
                f"Unsupported DENSE_QUERY_EMBEDDING_BACKEND {self.backend!r}. Only 'local' is configured."
            )
        if self.slot != "bge_m3":
            raise ValueError(f"Unsupported DENSE_QUERY_EMBEDDING_SLOT {self.slot!r}. Only 'bge_m3' is configured.")
        if self._client is None:
            self._client = LocalBgeM3EmbeddingClient(
                model_name=self.model_name,
                expected_dim=self.expected_dim,
                device=self.device,
                implementation=self.implementation,
                normalize=self.normalize,
            )
        return self._client

    def describe(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "device": self.device,
            "expected_dim": self.expected_dim,
            "implementation": self.implementation,
            "model_name": self.model_name,
            "normalize": self.normalize,
            "slot": self.slot,
        }

    def embed_query(self, text: str) -> list[float]:
        return self._ensure_client().embed_query(text)


def get_supabase_client():
    return create_client(settings.NEXT_PUBLIC_SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def get_neo4j_driver():
    return GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
        connection_timeout=settings.NEO4J_CONNECTION_TIMEOUT,
        connection_acquisition_timeout=settings.NEO4J_CONNECTION_ACQUISITION_TIMEOUT,
        max_transaction_retry_time=settings.NEO4J_MAX_TRANSACTION_RETRY_TIME,
    )


def get_langfuse_client():
    return LangfuseClient(
        base_url=settings.LANGFUSE_BASE_URL,
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
    )


@lru_cache(maxsize=1)
def get_dense_query_embedding_service() -> DenseQueryEmbeddingService:
    return DenseQueryEmbeddingService(
        backend=settings.DENSE_QUERY_EMBEDDING_BACKEND,
        model_name=settings.DENSE_QUERY_EMBEDDING_MODEL,
        device=settings.DENSE_QUERY_EMBEDDING_DEVICE,
        slot=settings.DENSE_QUERY_EMBEDDING_SLOT,
        expected_dim=settings.DENSE_QUERY_EMBEDDING_DIM,
        implementation=settings.DENSE_QUERY_EMBEDDING_IMPLEMENTATION,
        normalize=settings.DENSE_QUERY_EMBEDDING_NORMALIZE,
    )
