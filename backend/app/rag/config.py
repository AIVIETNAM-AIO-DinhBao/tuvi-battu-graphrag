from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.config import settings


ROOT_DIR = Path(__file__).resolve().parents[3]

VALID_BRANCHES = {"gemini-call", "rule-only", "local-kaggle"}
VALID_BASELINE_CHUNK_STRATEGIES = {
    "chunk_fixed_512",
    "chunk_structure_parent_child",
    "chunk_semantic_embedding_bge_m3",
}
VALID_FUSION_METHODS = {"rrf", "weighted_sum", "graph_first"}
VALID_CONTEXT_ASSEMBLY_STRATEGIES = {"balanced", "dense_first", "graph_first", "compact"}
VALID_QUERY_REWRITE_BACKENDS = {"gemini"}
VALID_RUNTIME_ENTITY_BACKENDS = {"dictionary"}
VALID_GRAPH_RELATION_TYPES = {
    "APPLIES_TO",
    "DOI_CHIEU",
    "GIAI_THICH",
    "LIEN_KE",
    "LUU_Y",
    "MENTIONS",
    "RELATED_TO",
    "THUOC_CUNG",
}
SAFE_NEO4J_INDEX_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DEFAULT_FUSION_PATH_WEIGHTS = {"graph": 1.45, "dense": 1.15, "sparse": 0.80}
VALID_RETRIEVAL_PATHS = set(DEFAULT_FUSION_PATH_WEIGHTS)


class EmbeddingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slot: Literal["bge_m3"]
    model: str = "BAAI/bge-m3"
    vector_index: str = "chunkVectorBgeM3"
    dimension: int = 1024

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: str) -> str:
        if value != "BAAI/bge-m3":
            raise ValueError("W4 default runtime embedding model must be BAAI/bge-m3.")
        return value

    @field_validator("vector_index")
    @classmethod
    def validate_vector_index(cls, value: str) -> str:
        if value != "chunkVectorBgeM3":
            raise ValueError("W4 default runtime vector index must be chunkVectorBgeM3.")
        return value

    @field_validator("dimension")
    @classmethod
    def validate_dimension(cls, value: int) -> int:
        if value != 1024:
            raise ValueError("W4 default runtime embedding dimension must be 1024.")
        return value


class RerankerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    model: str | None = "BAAI/bge-reranker-v2-m3"
    top_k: int = Field(default=10, ge=1)
    batch_size: int = Field(default=2, ge=1, le=128)
    max_length: int = Field(default=512, ge=128, le=8192)
    local_files_only: bool = True
    local_model_path: Path | None = None

    @model_validator(mode="after")
    def validate_model_backed_reranker(self) -> "RerankerConfig":
        if not self.enabled:
            return self
        model_name = (self.model or "").strip()
        if not model_name:
            raise ValueError("enabled reranker_config requires a cross-encoder model.")
        if model_name in {"lexical", "lexical-overlap-v1"}:
            raise ValueError("lexical reranker is not allowed for enabled runtime configs.")
        return self


class QueryRewriteConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backend: Literal["gemini"] = "gemini"
    model: str = "gemini-3.1-flash-lite-preview"
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    max_output_tokens: int = Field(default=256, ge=32, le=2048)
    fallback_on_error: bool = True

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query_rewrite.model must be non-empty.")
        return value


class RuntimeEntityExtractionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backend: Literal["dictionary"] = "dictionary"
    model: str = "dictionary-rule"
    entity_config_path: Path = Path("configs/entity_extraction.yaml")
    max_entities: int = Field(default=16, ge=1, le=100)
    exclude_entity_types: list[str] = Field(default_factory=lambda: ["LuanGiai"])

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("runtime_entity_extraction.model must be non-empty.")
        return value

    @field_validator("entity_config_path")
    @classmethod
    def validate_entity_config_path(cls, value: Path) -> Path:
        candidate = value if value.is_absolute() else ROOT_DIR / value
        if not candidate.exists():
            raise ValueError(f"runtime entity config does not exist: {candidate}")
        return value

    @field_validator("exclude_entity_types")
    @classmethod
    def validate_exclude_entity_types(cls, value: list[str]) -> list[str]:
        return sorted({item for item in value if str(item).strip()})


class GraphRetrievalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top_k: int = Field(default=8, ge=1, le=100)
    per_entity_limit: int = Field(default=5, ge=1, le=50)
    allowed_relation_types: list[str] = Field(
        default_factory=lambda: [
            "MENTIONS",
            "GIAI_THICH",
            "RELATED_TO",
            "THUOC_CUNG",
            "DOI_CHIEU",
            "LIEN_KE",
            "APPLIES_TO",
            "LUU_Y",
        ]
    )
    timeout_seconds: float = Field(default=3.0, ge=0.1, le=60.0)
    child_only: bool = True

    @field_validator("allowed_relation_types")
    @classmethod
    def validate_allowed_relation_types(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("graph_retrieval.allowed_relation_types must not be empty.")
        invalid = sorted(set(value) - VALID_GRAPH_RELATION_TYPES)
        if invalid:
            allowed = ", ".join(sorted(VALID_GRAPH_RELATION_TYPES))
            raise ValueError(
                f"Unsupported graph relation types: {', '.join(invalid)}. Allowed: {allowed}."
            )
        return sorted(dict.fromkeys(value))


class DenseRetrievalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top_k: int = Field(default=8, ge=1, le=100)
    candidate_k: int = Field(default=500, ge=1, le=5000)
    vector_index: str = "chunkVectorBgeM3"
    embedding_slot: Literal["bge_m3"] = "bge_m3"
    timeout_seconds: float = Field(default=3.0, ge=0.1, le=60.0)
    child_only: bool = True

    @field_validator("vector_index")
    @classmethod
    def validate_vector_index(cls, value: str) -> str:
        if value != "chunkVectorBgeM3":
            raise ValueError("dense_retrieval.vector_index must be chunkVectorBgeM3.")
        if not SAFE_NEO4J_INDEX_RE.match(value):
            raise ValueError("dense_retrieval.vector_index must be a safe Neo4j index name.")
        return value

    @model_validator(mode="after")
    def validate_candidate_window(self) -> "DenseRetrievalConfig":
        if self.candidate_k < self.top_k:
            raise ValueError("dense_retrieval.candidate_k must be greater than or equal to top_k.")
        return self


class SparseRetrievalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top_k: int = Field(default=8, ge=1, le=100)
    fulltext_index: str = "chunkFulltext"
    timeout_seconds: float = Field(default=3.0, ge=0.1, le=60.0)
    sanitization_mode: Literal["or_terms"] = "or_terms"
    child_only: bool = True

    @field_validator("fulltext_index")
    @classmethod
    def validate_fulltext_index(cls, value: str) -> str:
        if value != "chunkFulltext":
            raise ValueError("sparse_retrieval.fulltext_index must be chunkFulltext.")
        if not SAFE_NEO4J_INDEX_RE.match(value):
            raise ValueError("sparse_retrieval.fulltext_index must be a safe Neo4j index name.")
        return value


class ExperimentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    experiment_id: str
    name: str
    branch: Literal["gemini-call", "rule-only", "local-kaggle"]
    domain: Literal["TUVI"] = "TUVI"
    source_ids: list[str] = Field(default_factory=lambda: ["TVKL", "TVNL", "TVHS", "TVGM"])
    chunk_strategy_id: str
    accepted_chunk_strategy_ids: list[str] = Field(
        default_factory=lambda: sorted(VALID_BASELINE_CHUNK_STRATEGIES)
    )
    embedding: EmbeddingConfig
    query_rewrite_enabled: bool
    query_rewrite: QueryRewriteConfig
    entity_extraction_enabled: bool
    runtime_entity_extraction: RuntimeEntityExtractionConfig
    graph_retrieval_enabled: bool
    graph_retrieval: GraphRetrievalConfig
    dense_retrieval_enabled: bool
    dense_retrieval: DenseRetrievalConfig
    sparse_retrieval_enabled: bool
    sparse_retrieval: SparseRetrievalConfig
    fusion_method: str
    fusion_path_weights: dict[str, float] = Field(default_factory=lambda: dict(DEFAULT_FUSION_PATH_WEIGHTS))
    reranker_config: RerankerConfig
    document_grading_enabled: bool
    prompt_template_id: str
    generation_model: str
    context_assembly_strategy: str
    cache_disabled: bool

    @property
    def reranker_enabled(self) -> bool:
        return self.reranker_config.enabled

    @field_validator("experiment_id", "name", "prompt_template_id", "generation_model")
    @classmethod
    def validate_non_empty_string(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field must be a non-empty string.")
        return value

    @field_validator("source_ids")
    @classmethod
    def validate_source_ids(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("source_ids must include at least one source.")
        empty = [source for source in value if not str(source).strip()]
        if empty:
            raise ValueError("source_ids cannot contain empty values.")
        return value

    @field_validator("chunk_strategy_id")
    @classmethod
    def validate_chunk_strategy_id(cls, value: str) -> str:
        if value not in VALID_BASELINE_CHUNK_STRATEGIES:
            allowed = ", ".join(sorted(VALID_BASELINE_CHUNK_STRATEGIES))
            raise ValueError(f"chunk_strategy_id must be one of: {allowed}.")
        return value

    @field_validator("accepted_chunk_strategy_ids")
    @classmethod
    def validate_accepted_chunk_strategy_ids(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("accepted_chunk_strategy_ids must not be empty.")
        invalid = sorted(set(value) - VALID_BASELINE_CHUNK_STRATEGIES)
        if invalid:
            raise ValueError(f"Unsupported accepted chunk strategies: {', '.join(invalid)}.")
        return value

    @field_validator("fusion_method")
    @classmethod
    def validate_fusion_method(cls, value: str) -> str:
        if value not in VALID_FUSION_METHODS:
            allowed = ", ".join(sorted(VALID_FUSION_METHODS))
            raise ValueError(f"fusion_method must be one of: {allowed}.")
        return value

    @field_validator("fusion_path_weights")
    @classmethod
    def validate_fusion_path_weights(cls, value: dict[str, float]) -> dict[str, float]:
        if not value:
            raise ValueError("fusion_path_weights must not be empty.")
        invalid = sorted(set(value) - VALID_RETRIEVAL_PATHS)
        if invalid:
            allowed = ", ".join(sorted(VALID_RETRIEVAL_PATHS))
            raise ValueError(f"Unsupported fusion path weights: {', '.join(invalid)}. Allowed: {allowed}.")
        weights = {path: float(value.get(path, DEFAULT_FUSION_PATH_WEIGHTS[path])) for path in VALID_RETRIEVAL_PATHS}
        non_positive = sorted(path for path, weight in weights.items() if weight <= 0.0)
        if non_positive:
            raise ValueError(f"fusion_path_weights must be positive for: {', '.join(non_positive)}.")
        return {path: weights[path] for path in ("graph", "dense", "sparse")}

    @field_validator("context_assembly_strategy")
    @classmethod
    def validate_context_assembly_strategy(cls, value: str) -> str:
        if value not in VALID_CONTEXT_ASSEMBLY_STRATEGIES:
            allowed = ", ".join(sorted(VALID_CONTEXT_ASSEMBLY_STRATEGIES))
            raise ValueError(f"context_assembly_strategy must be one of: {allowed}.")
        return value


def resolve_config_path(path: Path | str | None = None) -> Path:
    candidate = Path(path or settings.DEFAULT_EXPERIMENT_CONFIG)
    if not candidate.is_absolute():
        candidate = ROOT_DIR / candidate
    return candidate


def load_experiment_config(path: Path | str | None = None) -> ExperimentConfig:
    config_path = resolve_config_path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Experiment config not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Experiment config must be a YAML object: {config_path}")
    return ExperimentConfig.model_validate(payload)


def _canonicalize_hash_value(value: object) -> object:
    """Normalize config values so hashes are stable across operating systems."""
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {key: _canonicalize_hash_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonicalize_hash_value(item) for item in value]
    return value


def config_hash(config: ExperimentConfig) -> str:
    payload = _canonicalize_hash_value(config.model_dump(mode="python", exclude_none=True))
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
