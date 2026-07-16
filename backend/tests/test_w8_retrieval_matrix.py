from __future__ import annotations

import json
from pathlib import Path

from app.rag.ablation import load_ablation_manifest
from app.rag.config import ExperimentConfig


ROOT_DIR = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT_DIR / "configs" / "w8_abl_01_retrieval_matrix_v2.yaml"
EXPECTED_NAMES = {
    "baseline_graph_sparse_rrf",
    "graph_only_rrf",
    "sparse_only_rrf",
    "dense_only_rrf",
    "dense_sparse_rrf",
    "graph_dense_rrf",
    "all_paths_planner_dense_rrf",
    "baseline_no_reranker",
    "baseline_weighted_sum",
    "baseline_graph_first",
}


def behavior_signature(config: ExperimentConfig) -> str:
    payload = config.model_dump(mode="json")
    payload.pop("experiment_id", None)
    payload.pop("name", None)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def test_w8_retrieval_matrix_has_ten_unique_fair_configs() -> None:
    manifest = load_ablation_manifest(MANIFEST_PATH)
    configs = {spec.name: spec.build_config() for spec in manifest.configs}

    assert manifest.name == "w8_abl_01_retrieval_fusion_reranker_v2"
    assert set(configs) == EXPECTED_NAMES
    assert len(configs) == 10
    assert len({config.experiment_id for config in configs.values()}) == 10
    assert len({behavior_signature(config) for config in configs.values()}) == 10

    for config in configs.values():
        assert config.chunk_strategy_id == "chunk_semantic_embedding_bge_m3"
        assert config.prompt_template_id == "tuvi_generation_v1"
        assert config.generation_model == "gemini-3.1-flash-lite-preview"
        assert config.query_rewrite_enabled is False
        assert config.context_assembly_strategy == "balanced"
        assert config.document_grading_enabled is True
        assert config.cache_disabled is True
        assert config.source_ids == ["TVKL", "TVNL", "TVHS", "TVGM"]


def test_w8_retrieval_matrix_isolates_dense_reranker_and_fusion_variants() -> None:
    manifest = load_ablation_manifest(MANIFEST_PATH)
    configs = {spec.name: spec.build_config() for spec in manifest.configs}
    baseline = configs["baseline_graph_sparse_rrf"]

    assert configs["dense_only_rrf"].dense_retrieval_enabled is True
    assert configs["dense_only_rrf"].graph_retrieval_enabled is False
    assert configs["dense_only_rrf"].sparse_retrieval_enabled is False
    assert configs["all_paths_planner_dense_rrf"].dense_retrieval_enabled is True
    assert configs["all_paths_planner_dense_rrf"].graph_retrieval_enabled is True
    assert configs["all_paths_planner_dense_rrf"].sparse_retrieval_enabled is True

    no_reranker = configs["baseline_no_reranker"]
    weighted = configs["baseline_weighted_sum"]
    graph_first = configs["baseline_graph_first"]
    assert baseline.reranker_enabled is True
    assert no_reranker.reranker_enabled is False
    assert weighted.fusion_method == "weighted_sum"
    assert graph_first.fusion_method == "graph_first"
    assert weighted.context_assembly_strategy == baseline.context_assembly_strategy == "balanced"
    assert graph_first.context_assembly_strategy == baseline.context_assembly_strategy == "balanced"
