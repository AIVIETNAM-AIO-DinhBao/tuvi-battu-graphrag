from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from app.rag.ablation import load_ablation_manifest
from app.rag.config import ExperimentConfig


ROOT_DIR = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT_DIR / "configs" / "w8_abl_01_retrieval_matrix_v2.yaml"
PRIORITY_WAVE_PATH = ROOT_DIR / "configs" / "w8_abl_01_priority_wave.yaml"
MERGE_SCRIPT_PATH = ROOT_DIR / "scripts" / "merge_w8_retrieval_shards.py"
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
PRIORITY_WAVE_NAMES = {
    "sparse_only_rrf",
    "dense_sparse_rrf",
    "baseline_no_reranker",
    "baseline_weighted_sum",
}
SHARD_MANIFESTS = {
    ROOT_DIR / "configs" / "w8_abl_01_retrieval_matrix_v2_shard_a_controls.yaml": {
        "baseline_graph_sparse_rrf",
        "baseline_no_reranker",
        "baseline_weighted_sum",
        "baseline_graph_first",
    },
    ROOT_DIR / "configs" / "w8_abl_01_retrieval_matrix_v2_shard_b_single_paths.yaml": {
        "graph_only_rrf",
        "sparse_only_rrf",
        "dense_only_rrf",
    },
    ROOT_DIR / "configs" / "w8_abl_01_retrieval_matrix_v2_shard_c_dense_combos.yaml": {
        "dense_sparse_rrf",
        "graph_dense_rrf",
        "all_paths_planner_dense_rrf",
    },
}


def load_merge_script_module():
    spec = importlib.util.spec_from_file_location("merge_w8_retrieval_shards", MERGE_SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        assert config.prompt_template_id == "tuvi_generation_structured_v3"
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


def test_w8_priority_wave_reuses_exact_matrix_configs() -> None:
    full_manifest = load_ablation_manifest(MANIFEST_PATH)
    wave_manifest = load_ablation_manifest(PRIORITY_WAVE_PATH)
    full_configs = {spec.name: spec.build_config() for spec in full_manifest.configs}
    wave_configs = {spec.name: spec.build_config() for spec in wave_manifest.configs}

    assert wave_manifest.name == "w8_abl_01_priority_wave_full100"
    assert set(wave_configs) == PRIORITY_WAVE_NAMES
    assert len({behavior_signature(config) for config in wave_configs.values()}) == 4

    for name, config in wave_configs.items():
        assert config == full_configs[name]
        assert config.chunk_strategy_id == "chunk_semantic_embedding_bge_m3"
        assert config.prompt_template_id == "tuvi_generation_structured_v3"
        assert config.generation_model == "gemini-3.1-flash-lite-preview"
        assert config.query_rewrite_enabled is False
        assert config.context_assembly_strategy == "balanced"
        assert config.document_grading_enabled is True
        assert config.cache_disabled is True


def test_w8_retrieval_shard_manifests_partition_canonical_matrix() -> None:
    full_manifest = load_ablation_manifest(MANIFEST_PATH)
    full_configs = {spec.name: spec.build_config() for spec in full_manifest.configs}

    seen_names: set[str] = set()
    for shard_path, expected_names in SHARD_MANIFESTS.items():
        shard_manifest = load_ablation_manifest(shard_path)
        shard_configs = {spec.name: spec.build_config() for spec in shard_manifest.configs}

        assert set(shard_configs) == expected_names
        assert set(shard_configs).isdisjoint(seen_names)
        seen_names.update(shard_configs)
        assert "reports_final/20_retrieval_fusion_reranker_matrix/shards/" in shard_manifest.output_dir.as_posix()
        for name, config in shard_configs.items():
            assert config == full_configs[name]

    assert seen_names == EXPECTED_NAMES


def test_w8_retrieval_merge_script_combines_completed_shards(tmp_path: Path) -> None:
    module = load_merge_script_module()
    full_manifest = load_ablation_manifest(MANIFEST_PATH)
    expected_hashes = {spec.name: module.config_hash(spec.build_config()) for spec in full_manifest.configs}
    dataset_path = str(full_manifest.dataset_path)

    def item(item_id: str) -> dict[str, object]:
        return {
            "item_id": item_id,
            "status": "completed",
            "metrics": {},
        }

    shard_reports: list[Path] = []
    for index, (shard_path, names) in enumerate(SHARD_MANIFESTS.items(), start=1):
        shard_manifest = load_ablation_manifest(shard_path)
        report = {
            "manifest_name": shard_manifest.name,
            "dataset_path": dataset_path,
            "dataset_item_count": 100,
            "config_count": len(names),
            "judge_backend": "gemini",
            "metric_definitions": {"faithfulness_avg": "synthetic"},
            "status": "completed",
            "execution_summary": {
                "expected_pair_count": len(names) * 100,
                "completed_pair_count": len(names) * 100,
                "failed_pair_count": 0,
                "executed_pair_count": len(names) * 100,
                "resumed_pair_count": 0,
            },
            "configs": [
                {
                    "config_name": name,
                    "config_hash": expected_hashes[name],
                    "status": "completed",
                    "started_at": f"2026-08-03T00:0{index}:00Z",
                    "completed_at": f"2026-08-03T00:1{index}:00Z",
                    "metrics": {
                        "item_count": 100,
                        "failed_count": 0,
                        "faithfulness_avg": 1.0,
                        "answer_relevancy_avg": 1.0,
                        "context_recall_avg": 1.0,
                        "citation_coverage_rate": 1.0,
                    },
                    "grouped_metrics": {},
                    "items": [item(f"TVQA-{i:03d}") for i in range(1, 101)],
                }
                for name in names
            ],
        }
        report_path = tmp_path / f"shard_{index}" / "evaluation_report.json"
        report_path.parent.mkdir(parents=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
        shard_reports.append(report_path)

    output_dir = tmp_path / "canonical"
    args = argparse.Namespace(
        canonical_manifest=MANIFEST_PATH,
        output_dir=output_dir,
        shard_reports=shard_reports,
        judge_model="gemini-3.1-flash-lite-preview",
        allow_incomplete=False,
        dry_run=False,
    )

    report = module.merge_reports(args)
    assert report["status"] == "completed"
    assert report["config_count"] == 10
    assert report["execution_summary"]["completed_pair_count"] == 1000
    assert report["execution_summary"]["failed_pair_count"] == 0
    assert [row["config_name"] for row in report["configs"]] == [spec.name for spec in full_manifest.configs]

    module.write_merged_artifacts(report, output_dir)
    assert (output_dir / "evaluation_report.json").exists()
    assert (output_dir / "evaluation_report.md").exists()
    assert (output_dir / "checkpoints" / "checkpoint_summary.json").exists()


def test_w8_retrieval_merge_accepts_canonical_dataset_from_another_workspace() -> None:
    module = load_merge_script_module()
    expected_path = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "release" / "tuviqa_v1_release.jsonl"

    assert module.dataset_path_matches(
        r"D:\other-workspace\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl",
        expected_path,
    )
    assert not module.dataset_path_matches(
        r"D:\other-workspace\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\different_dataset.jsonl",
        expected_path,
    )
