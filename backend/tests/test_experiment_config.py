from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.rag.config import (
    ExperimentConfig,
    config_hash,
    load_experiment_config,
)


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT_DIR / "configs" / "default_production.yaml"
W6_PLANNER_GATED_DENSE_CONFIG_PATH = ROOT_DIR / "configs" / "w6_planner_gated_dense.yaml"
W7_GENERATION_CONFIG_PATHS = [
    ROOT_DIR / "configs" / "w7_generation_baseline_v1_flash_lite.yaml",
    ROOT_DIR / "configs" / "w7_generation_grounded_v2_flash_lite.yaml",
    ROOT_DIR / "configs" / "w7_generation_structured_v3_flash_lite.yaml",
]
EXPERIMENT_RUNS_MIGRATION = ROOT_DIR / "infra" / "supabase" / "migrations" / "20260709_experiment_runs.sql"
LOCKED_DEFAULT_CONFIG_HASH = "c40227a029588b7793201702798e96e640d7a436131d6f5f0437f67151803d96"


def default_payload() -> dict:
    config = load_experiment_config(DEFAULT_CONFIG_PATH)
    return config.model_dump(mode="json")


def test_default_production_config_loads_with_w7_evidence_locked_defaults() -> None:
    config = load_experiment_config(DEFAULT_CONFIG_PATH)

    assert config.experiment_id == "default_production_v2"
    assert config.name == "Default production config - W7 evidence locked"
    assert config.branch == "gemini-call"
    assert config.domain == "TUVI"
    assert config.chunk_strategy_id == "chunk_semantic_embedding_bge_m3"
    assert config.embedding.slot == "bge_m3"
    assert config.embedding.model == "BAAI/bge-m3"
    assert config.embedding.vector_index == "chunkVectorBgeM3"
    assert config.embedding.dimension == 1024
    assert config.query_rewrite.backend == "gemini"
    assert config.query_rewrite.model == "gemini-3.1-flash-lite-preview"
    assert config.runtime_entity_extraction.backend == "dictionary"
    assert config.runtime_entity_extraction.model == "dictionary-rule"
    assert config.graph_retrieval.top_k == 8
    assert config.graph_retrieval.per_entity_limit == 5
    assert "MENTIONS" in config.graph_retrieval.allowed_relation_types
    assert config.dense_retrieval.top_k == 8
    assert config.dense_retrieval.candidate_k == 500
    assert config.dense_retrieval.vector_index == "chunkVectorBgeM3"
    assert config.dense_retrieval.embedding_slot == "bge_m3"
    assert config.sparse_retrieval.top_k == 8
    assert config.sparse_retrieval.fulltext_index == "chunkFulltext"
    assert config.sparse_retrieval.sanitization_mode == "or_terms"
    assert config.query_rewrite_enabled is False
    assert config.graph_retrieval_enabled is True
    assert config.dense_retrieval_enabled is False
    assert config.sparse_retrieval_enabled is True
    assert config.fusion_method == "rrf"
    assert config.reranker_enabled is True
    assert config.reranker_config.model == "lexical-overlap-v1"
    assert config.reranker_config.top_k == 10
    assert config.prompt_template_id == "tuvi_generation_v1"
    assert config.generation_model == "gemini-3.1-flash-lite-preview"
    assert config.context_assembly_strategy == "balanced"
    assert config.cache_disabled is True
    assert set(config.accepted_chunk_strategy_ids) == {
        "chunk_fixed_512",
        "chunk_structure_parent_child",
        "chunk_semantic_embedding_bge_m3",
    }


def test_config_hash_is_stable_for_same_config() -> None:
    config = load_experiment_config(DEFAULT_CONFIG_PATH)

    assert config_hash(config) == config_hash(ExperimentConfig.model_validate(config.model_dump(mode="json")))


def test_default_production_config_hash_matches_w7_lock() -> None:
    config = load_experiment_config(DEFAULT_CONFIG_PATH)

    assert config_hash(config) == LOCKED_DEFAULT_CONFIG_HASH


def test_w6_planner_gated_dense_config_loads_for_ablation() -> None:
    default_config = load_experiment_config(DEFAULT_CONFIG_PATH)
    dense_config = load_experiment_config(W6_PLANNER_GATED_DENSE_CONFIG_PATH)

    assert default_config.dense_retrieval_enabled is False
    assert dense_config.experiment_id == "w6_planner_gated_dense_v1"
    assert dense_config.dense_retrieval_enabled is True
    assert dense_config.dense_retrieval.embedding_slot == "bge_m3"
    assert dense_config.dense_retrieval.vector_index == "chunkVectorBgeM3"
    assert dense_config.context_assembly_strategy == default_config.context_assembly_strategy


def test_w7_generation_prompt_configs_load_with_fixed_retrieval_stack() -> None:
    configs = [load_experiment_config(path) for path in W7_GENERATION_CONFIG_PATHS]

    assert {config.prompt_template_id for config in configs} == {
        "tuvi_generation_v1",
        "tuvi_generation_grounded_v2",
        "tuvi_generation_structured_v3",
    }
    assert {config.generation_model for config in configs} == {"gemini-3.1-flash-lite-preview"}
    assert len({config_hash(config) for config in configs}) == 3
    for config in configs:
        assert config.chunk_strategy_id == "chunk_semantic_embedding_bge_m3"
        assert config.graph_retrieval_enabled is True
        assert config.dense_retrieval_enabled is False
        assert config.sparse_retrieval_enabled is True
        assert config.fusion_method == "rrf"
        assert config.reranker_enabled is True


def test_missing_required_field_fails_clearly() -> None:
    payload = default_payload()
    del payload["name"]

    with pytest.raises(ValidationError, match="name"):
        ExperimentConfig.model_validate(payload)


@pytest.mark.parametrize(
    ("path_parts", "value", "message"),
    [
        (("branch",), "qwen-main", "branch"),
        (("chunk_strategy_id",), "chunk_fixed_256", "chunk_strategy_id"),
        (("embedding", "slot"), "gemini", "slot"),
        (("query_rewrite", "backend"), "mock", "query_rewrite"),
        (("runtime_entity_extraction", "backend"), "gemini", "runtime_entity_extraction"),
        (("runtime_entity_extraction", "entity_config_path"), "configs/missing.yaml", "runtime entity config"),
        (("graph_retrieval", "top_k"), 0, "graph_retrieval"),
        (("graph_retrieval", "allowed_relation_types"), ["BAD_REL"], "Unsupported graph relation types"),
        (("dense_retrieval", "candidate_k"), 1, "candidate_k"),
        (("dense_retrieval", "vector_index"), "chunkVectorBad", "dense_retrieval"),
        (("sparse_retrieval", "fulltext_index"), "chunkFulltextBad", "sparse_retrieval"),
    ],
)
def test_invalid_config_values_fail(
    path_parts: tuple[str, ...],
    value: object,
    message: str,
) -> None:
    payload = default_payload()
    target = payload
    for part in path_parts[:-1]:
        target = target[part]
    target[path_parts[-1]] = value

    with pytest.raises(ValidationError, match=message):
        ExperimentConfig.model_validate(payload)


def test_experiment_runs_migration_contains_required_schema() -> None:
    sql = EXPERIMENT_RUNS_MIGRATION.read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS experiment_runs" in sql
    assert "experiment_id TEXT NOT NULL" in sql
    assert "config_hash TEXT NOT NULL" in sql
    assert "config JSONB NOT NULL" in sql
    assert "metrics JSONB NOT NULL" in sql
    assert "trace JSONB NOT NULL" in sql
    assert "idx_experiment_runs_experiment_id" in sql
    assert "idx_experiment_runs_config_hash" in sql
    assert "idx_experiment_runs_status" in sql
