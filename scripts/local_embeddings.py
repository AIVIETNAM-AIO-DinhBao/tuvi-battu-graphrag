"""Lazy local embedding clients for Kaggle/offline W3 ingestion.

The module intentionally has no heavy imports at module import time. Kaggle
notebooks install the optional dependencies, while normal unit tests can import
this file without torch/transformers/FlagEmbedding installed.
"""

from __future__ import annotations

import math
from typing import Any


DEFAULT_LOCAL_EMBEDDING_MODEL = "BAAI/bge-m3"
DEFAULT_LOCAL_EMBEDDING_DIM = 1024
DEFAULT_LOCAL_EMBEDDING_BATCH_SIZE = 16


def l2_normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return [0.0 for _ in vector]
    return [value / norm for value in vector]


def to_float_list(vector: Any) -> list[float]:
    if hasattr(vector, "tolist"):
        vector = vector.tolist()
    return [float(value) for value in vector]


class LocalBgeM3EmbeddingClient:
    """BGE-M3 dense embedding client with FlagEmbedding/SentenceTransformer fallback."""

    def __init__(
        self,
        model_name: str = DEFAULT_LOCAL_EMBEDDING_MODEL,
        *,
        expected_dim: int = DEFAULT_LOCAL_EMBEDDING_DIM,
        batch_size: int = DEFAULT_LOCAL_EMBEDDING_BATCH_SIZE,
        device: str | None = None,
        implementation: str = "auto",
        normalize: bool = True,
        use_fp16: bool = True,
    ) -> None:
        self.model_name = model_name
        self.embedding_backend = "local"
        self.expected_dim = expected_dim
        self.batch_size = max(1, int(batch_size))
        self.device = device
        self.implementation = implementation
        self.normalize = normalize
        self.use_fp16 = use_fp16
        self._model: Any | None = None
        self._resolved_backend: str | None = None
        self.document_call_count = 0
        self.query_call_count = 0

    @property
    def resolved_backend(self) -> str:
        self._ensure_model()
        return str(self._resolved_backend)

    def get_usage_summary(self) -> dict[str, Any]:
        return {
            "embedding_backend": "local",
            "local_embedding_backend": self._resolved_backend or self.implementation,
            "local_embedding_batch_size": self.batch_size,
            "local_embedding_device": self.device,
            "local_embedding_model": self.model_name,
            "local_embedding_normalize": self.normalize,
            "local_embedding_query_calls": self.query_call_count,
            "local_embedding_document_calls": self.document_call_count,
        }

    def _ensure_model(self) -> None:
        if self._model is not None:
            return

        if self.implementation in {"auto", "flagembedding"}:
            try:
                from FlagEmbedding import BGEM3FlagModel  # type: ignore[import-not-found]
            except ImportError:
                if self.implementation == "flagembedding":
                    raise RuntimeError(
                        "FlagEmbedding is not installed. Install backend/requirements-kaggle.txt "
                        "or use --local-embedding-implementation sentence-transformers."
                    )
            else:
                kwargs: dict[str, Any] = {"use_fp16": self.use_fp16}
                if self.device:
                    kwargs["device"] = self.device
                self._model = BGEM3FlagModel(self.model_name, **kwargs)
                self._resolved_backend = "flagembedding"
                return

        if self.implementation in {"auto", "sentence-transformers"}:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]
            except ImportError as exc:
                raise RuntimeError(
                    "No local embedding backend is installed. Install FlagEmbedding or "
                    "sentence-transformers from backend/requirements-kaggle.txt."
                ) from exc
            kwargs = {}
            if self.device:
                kwargs["device"] = self.device
            self._model = SentenceTransformer(self.model_name, **kwargs)
            self._resolved_backend = "sentence-transformers"
            return

        raise ValueError(
            "--local-embedding-implementation must be auto, flagembedding, or sentence-transformers."
        )

    def _encode_texts(self, texts: list[str]) -> list[list[float]]:
        self._ensure_model()
        if not texts:
            return []

        if self._resolved_backend == "flagembedding":
            encoded = self._model.encode(texts, batch_size=self.batch_size, max_length=8192)
            vectors = encoded.get("dense_vecs") if isinstance(encoded, dict) else encoded
        else:
            vectors = self._model.encode(
                texts,
                batch_size=self.batch_size,
                normalize_embeddings=self.normalize,
                convert_to_numpy=False,
            )

        results = []
        for vector in vectors:
            values = to_float_list(vector)
            if self.normalize and self._resolved_backend != "sentence-transformers":
                values = l2_normalize(values)
            if len(values) != self.expected_dim:
                raise ValueError(
                    f"Local embedding dimension mismatch for {self.model_name}: "
                    f"expected {self.expected_dim}, got {len(values)}."
                )
            results.append(values)
        return results

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self.document_call_count += len(texts)
        return self._encode_texts(texts)

    def embed_document(self, text: str, title: str | None = None) -> list[float]:
        document = f"title: {title or 'none'} | text: {text}" if title else text
        return self.embed_documents([document])[0]

    def embed_query(self, text: str) -> list[float]:
        self.query_call_count += 1
        return self._encode_texts([text])[0]
