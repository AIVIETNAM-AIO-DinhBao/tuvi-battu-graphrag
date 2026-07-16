from __future__ import annotations

from pathlib import Path
from typing import Any

from app.rag.ablation import AblationDatasetItem, InMemoryExperimentRunStore, load_ablation_manifest
from app.rag.config import ExperimentConfig
from app.rag.evaluation import (
    EvaluationJudgeResult,
    EvaluationRunner,
    StaticEvaluationJudge,
    aggregate_evaluation_metrics,
    aggregate_grouped_metrics,
    build_ablation_analysis,
    build_chunking_ablation_analysis,
    build_generation_prompt_ablation_analysis,
    build_single_config_manifest,
    extract_json_object,
    render_markdown_report,
    summarize_evaluation_item,
)


ROOT_DIR = Path(__file__).resolve().parents[2]
RELEASE_DATASET_PATH = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "release" / "tuviqa_v1_release.jsonl"
DEFAULT_CONFIG_PATH = ROOT_DIR / "configs" / "default_production.yaml"
W6_BASELINE_MANIFEST = ROOT_DIR / "configs" / "w6_eval_baseline.yaml"
W6_ABL_02_MANIFEST = ROOT_DIR / "configs" / "w6_abl_02_retrieval_matrix.yaml"
W6_ABL_03_MANIFEST = ROOT_DIR / "configs" / "w6_abl_03_chunking_matrix.yaml"
W7_ABL_01_MANIFEST = ROOT_DIR / "configs" / "w7_abl_01_generation_prompt_matrix.yaml"
W8_ABL_01_MANIFEST = ROOT_DIR / "configs" / "w8_abl_01_retrieval_matrix_v2.yaml"


def fake_state(item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
    context_chunks = [
        {
            "citation_marker": "S1",
            "chunk_id": f"chunk-{item.id}",
            "chunk_hash": f"hash-{item.id}",
            "chunk_strategy_id": config.chunk_strategy_id,
            "source_id": "TVKL",
            "source_name": "Tử Vi Khảo Luận",
            "source_page": 8,
            "excerpt": "Tương sinh thì hợp cách và tốt đẹp, tương khắc thì sái cách và tầm thường.",
            "retrieval_paths": ["graph", "sparse"],
        }
    ]
    return {
        "answer": f"Câu trả lời đánh giá cho {item.id} dựa trên nguồn [S1].",
        "sources": context_chunks,
        "context_chunks": context_chunks,
        "graph_candidates": [{"chunk_id": f"chunk-{item.id}"}],
        "citation_metadata": {"citation_fallback": False, "source_count": 1},
        "context_summary": {"selected_count": 1},
        "retrieval_trace": {
            "nodes": [
                {"node": "graph_retrieval", "status": "completed", "duration_ms": 100.0},
                {"node": "sparse_retrieval", "status": "completed", "duration_ms": 50.0},
                {"node": "generation", "status": "completed"},
            ]
        },
        "retrieval_diagnostics": {
            "question_complexity": item.question_complexity,
            "question_family": (item.labels or {}).get("question_family"),
            "candidate_counts": {
                "graph": 1,
                "dense": 0,
                "sparse": 1,
                "fused": 1,
                "reranked": 1,
                "graded": 1,
                "ranked": 1,
                "context_selected": 1,
                "sources": 1,
            },
            "final_selected_retrieval_paths": ["graph", "sparse"],
            "selected_evidence_roles": ["generic"],
        },
    }


class FixedJudge:
    backend = "gemini"

    def evaluate(
        self,
        *,
        item: AblationDatasetItem,
        state: dict[str, Any],
        config: ExperimentConfig,
    ) -> EvaluationJudgeResult:
        return EvaluationJudgeResult(
            faithfulness=0.8,
            answer_relevancy=0.7,
            context_recall=0.6,
            reasons={
                "faithfulness": "supported enough",
                "answer_relevancy": "answers the question",
                "context_recall": "some evidence present",
            },
            backend="gemini",
            model="fake-gemini",
            raw_response='{"faithfulness": 0.8}',
        )


def test_extract_json_object_accepts_plain_and_fenced_json() -> None:
    assert extract_json_object('{"faithfulness": 0.8}')["faithfulness"] == 0.8

    fenced = "```json\n{\"answer_relevancy\": 0.75, \"context_recall\": 1}\n```"
    payload = extract_json_object(fenced)

    assert payload["answer_relevancy"] == 0.75
    assert payload["context_recall"] == 1


def test_summarize_item_excludes_chart_only_from_corpus_metrics() -> None:
    manifest = load_ablation_manifest(ROOT_DIR / "configs" / "w4_ablation_smoke.yaml")
    config = manifest.configs[0].build_config()
    chart_only_item = AblationDatasetItem(
        id="direct",
        chart_id="chart-1",
        query="Cung Mệnh ở đâu?",
        chart_data={"chart_type": "TUVI"},
        expected_answer_summary="Cung Mệnh nằm tại Ngọ.",
        question_complexity="Direct",
        labels={"question_family": "core_identity"},
    )

    result = summarize_evaluation_item(
        chart_only_item,
        fake_state(chart_only_item, config),
        EvaluationJudgeResult(0.9, 0.8, 0.7, backend="gemini"),
        latency_ms=123.4,
    )

    assert result["chart_only"] is True
    assert result["context_recall"] is None
    assert result["chart_context_grounding"] == 0.7
    assert result["graph_hit"] is None
    assert result["citation_coverage"] is None
    assert result["diagnostic_candidate_counts"]["graph"] == 1
    assert result["diagnostic_selected_retrieval_paths"] == ["graph", "sparse"]


def test_aggregate_metrics_and_groups_use_w6_metric_names() -> None:
    items = [
        {
            "status": "completed",
            "chart_only": True,
            "answer_present": True,
            "faithfulness": 0.9,
            "answer_relevancy": 0.8,
            "context_recall": None,
            "chart_context_grounding": 0.7,
            "graph_hit": None,
            "citation_coverage": None,
            "source_count": 0,
            "latency_ms": 100.0,
            "retrieval_latency_ms": None,
            "context_selected_count": 0,
            "question_complexity": "Direct",
            "question_family": "core_identity",
            "diagnostic_candidate_counts": {"graph": 0, "dense": 0, "sparse": 0, "fused": 0, "ranked": 0, "context_selected": 0},
            "diagnostic_selected_retrieval_paths": [],
        },
        {
            "status": "completed",
            "chart_only": False,
            "answer_present": True,
            "faithfulness": 0.7,
            "answer_relevancy": 0.6,
            "context_recall": 0.5,
            "chart_context_grounding": None,
            "graph_hit": True,
            "citation_coverage": 1.0,
            "source_count": 2,
            "latency_ms": 300.0,
            "retrieval_latency_ms": 120.0,
            "context_selected_count": 2,
            "question_complexity": "One-hop",
            "question_family": "menh_house_interpretation",
            "diagnostic_candidate_counts": {"graph": 3, "dense": 0, "sparse": 5, "fused": 6, "ranked": 4, "context_selected": 2},
            "diagnostic_selected_retrieval_paths": ["graph", "sparse"],
        },
    ]

    metrics = aggregate_evaluation_metrics(items, expected_item_count=2)
    groups = aggregate_grouped_metrics(items)

    assert metrics["faithfulness_avg"] == 0.8
    assert metrics["answer_relevancy_avg"] == 0.7
    assert metrics["context_recall_avg"] == 0.5
    assert metrics["chart_context_grounding_avg"] == 0.7
    assert metrics["graph_hit_rate"] == 1.0
    assert metrics["citation_coverage_rate"] == 1.0
    assert metrics["corpus_grounded_item_count"] == 1
    assert metrics["corpus_source_coverage_rate"] == 1.0
    assert metrics["citation_marker_presence_rate"] == 0.0
    assert metrics["citation_source_alignment_rate"] == 0.0
    assert metrics["avg_graph_candidate_count"] == 1.5
    assert metrics["avg_sparse_candidate_count"] == 2.5
    assert metrics["selected_graph_path_rate"] == 0.5
    assert metrics["selected_sparse_path_rate"] == 0.5
    assert metrics["p95_latency_ms"] == 290.0
    assert groups["by_question_complexity"]["Direct"]["chart_only_count"] == 1
    assert groups["by_question_family"]["menh_house_interpretation"]["context_recall_avg"] == 0.5


def test_w6_eval_baseline_manifest_loads_release_dataset_and_default_config() -> None:
    manifest = load_ablation_manifest(W6_BASELINE_MANIFEST)
    config = manifest.configs[0].build_config()

    assert manifest.name == "w6_eval_02_baseline"
    assert manifest.dataset_path == RELEASE_DATASET_PATH
    assert manifest.output_dir == ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "reports" / "w6_eval_02"
    assert manifest.configs[0].name == "default_production_baseline"
    assert config.experiment_id == "w6_eval_02_default_production_baseline"
    assert config.cache_disabled is True


def test_w6_abl_02_manifest_loads_full_retrieval_matrix() -> None:
    manifest = load_ablation_manifest(W6_ABL_02_MANIFEST)
    names = [spec.name for spec in manifest.configs]
    configs = {spec.name: spec.build_config() for spec in manifest.configs}

    assert manifest.name == "w6_abl_02_retrieval_fusion_reranker_v1"
    assert manifest.dataset_path == RELEASE_DATASET_PATH
    assert manifest.output_dir == ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "reports" / "w6_abl_02"
    assert len(names) == 11
    assert len({config.experiment_id for config in configs.values()}) == 11
    assert {
        "baseline_graph_sparse_rrf",
        "graph_only_rrf",
        "sparse_only_rrf",
        "dense_only_rrf",
        "dense_sparse_rrf",
        "graph_dense_rrf",
        "graph_sparse_rrf",
        "all_paths_planner_dense_rrf",
        "baseline_no_reranker",
        "baseline_weighted_sum",
        "baseline_graph_first",
    } == set(names)
    assert configs["dense_only_rrf"].dense_retrieval_enabled is True
    assert configs["dense_only_rrf"].graph_retrieval_enabled is False
    assert configs["dense_only_rrf"].sparse_retrieval_enabled is False
    assert configs["baseline_no_reranker"].reranker_enabled is False
    assert configs["baseline_weighted_sum"].fusion_method == "weighted_sum"
    assert configs["baseline_graph_first"].fusion_method == "graph_first"


def test_w8_abl_01_manifest_loads_ten_unique_retrieval_behaviors() -> None:
    manifest = load_ablation_manifest(W8_ABL_01_MANIFEST)
    configs = {spec.name: spec.build_config() for spec in manifest.configs}

    def behavior_signature(config: ExperimentConfig) -> tuple[bool, bool, bool, str, bool]:
        return (
            config.graph_retrieval_enabled,
            config.dense_retrieval_enabled,
            config.sparse_retrieval_enabled,
            config.fusion_method,
            config.reranker_enabled,
        )

    assert manifest.name == "w8_abl_01_retrieval_fusion_reranker_v2"
    assert manifest.dataset_path == RELEASE_DATASET_PATH
    assert manifest.output_dir == ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "reports" / "w8_abl_01" / "retrieval_v2"
    assert set(configs) == {
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
    assert len(configs) == 10
    assert len({config.experiment_id for config in configs.values()}) == 10
    assert len({behavior_signature(config) for config in configs.values()}) == 10


def test_w8_abl_01_retrieval_matrix_holds_fairness_controls_fixed() -> None:
    manifest = load_ablation_manifest(W8_ABL_01_MANIFEST)
    configs = {spec.name: spec.build_config() for spec in manifest.configs}

    def fairness_controls(config: ExperimentConfig) -> dict[str, Any]:
        payload = config.model_dump(mode="json")
        for field in (
            "experiment_id",
            "name",
            "graph_retrieval_enabled",
            "dense_retrieval_enabled",
            "sparse_retrieval_enabled",
            "fusion_method",
        ):
            payload.pop(field)
        payload["reranker_config"].pop("enabled")
        return payload

    assert {spec.base_config_path for spec in manifest.configs} == {DEFAULT_CONFIG_PATH}
    controls = [fairness_controls(config) for config in configs.values()]
    assert all(control == controls[0] for control in controls)
    for config in configs.values():
        assert config.chunk_strategy_id == "chunk_semantic_embedding_bge_m3"
        assert config.prompt_template_id == "tuvi_generation_v1"
        assert config.generation_model == "gemini-3.1-flash-lite-preview"
        assert config.query_rewrite_enabled is False
        assert config.context_assembly_strategy == "balanced"

    baseline = configs["baseline_graph_sparse_rrf"].model_dump(mode="json")
    graph_first = configs["baseline_graph_first"].model_dump(mode="json")
    for payload in (baseline, graph_first):
        payload.pop("experiment_id")
        payload.pop("name")
        payload.pop("fusion_method")
    assert graph_first == baseline


def test_w6_abl_03_manifest_loads_chunking_matrix_with_single_variable() -> None:
    manifest = load_ablation_manifest(W6_ABL_03_MANIFEST)
    configs = {spec.name: spec.build_config() for spec in manifest.configs}

    assert manifest.name == "w6_abl_03_chunking_strategy_v1"
    assert manifest.dataset_path == RELEASE_DATASET_PATH
    assert manifest.output_dir == ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "reports" / "w6_abl_03"
    assert set(configs) == {
        "fixed_512_graph_sparse_rrf",
        "parent_child_graph_sparse_rrf",
        "semantic_bge_m3_graph_sparse_rrf",
    }
    assert {config.chunk_strategy_id for config in configs.values()} == {
        "chunk_fixed_512",
        "chunk_structure_parent_child",
        "chunk_semantic_embedding_bge_m3",
    }
    assert len({config.experiment_id for config in configs.values()}) == 3
    for config in configs.values():
        assert config.source_ids == ["TVKL", "TVNL", "TVHS", "TVGM"]
        assert config.graph_retrieval_enabled is True
        assert config.dense_retrieval_enabled is False
        assert config.sparse_retrieval_enabled is True
        assert config.fusion_method == "rrf"
        assert config.reranker_enabled is True
        assert config.context_assembly_strategy == "balanced"


def test_w7_abl_01_manifest_loads_generation_prompt_matrix_with_retrieval_control() -> None:
    manifest = load_ablation_manifest(W7_ABL_01_MANIFEST)
    configs = {spec.name: spec.build_config() for spec in manifest.configs}

    assert manifest.name == "w7_abl_01_generation_prompt_v1"
    assert manifest.dataset_path == RELEASE_DATASET_PATH
    assert manifest.output_dir == ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "reports" / "w7_abl_01"
    assert set(configs) == {"baseline_v1_flash_lite", "grounded_v2_flash_lite", "structured_v3_flash_lite"}
    assert {config.prompt_template_id for config in configs.values()} == {
        "tuvi_generation_v1",
        "tuvi_generation_grounded_v2",
        "tuvi_generation_structured_v3",
    }
    assert {config.generation_model for config in configs.values()} == {"gemini-3.1-flash-lite-preview"}
    assert len({config.experiment_id for config in configs.values()}) == 3
    for config in configs.values():
        assert config.chunk_strategy_id == "chunk_semantic_embedding_bge_m3"
        assert config.graph_retrieval_enabled is True
        assert config.dense_retrieval_enabled is False
        assert config.sparse_retrieval_enabled is True
        assert config.fusion_method == "rrf"
        assert config.reranker_enabled is True
        assert config.context_assembly_strategy == "balanced"


def test_evaluation_runner_writes_reports_and_experiment_rows(tmp_path: Path) -> None:
    manifest = build_single_config_manifest(
        dataset_path=RELEASE_DATASET_PATH,
        config_path=DEFAULT_CONFIG_PATH,
        output_dir=tmp_path,
    )
    store = InMemoryExperimentRunStore()
    calls: list[str] = []

    def runner(item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
        calls.append(item.id)
        return fake_state(item, config)

    report = EvaluationRunner(run_store=store, rag_runner=runner, judge=FixedJudge()).run(
        manifest,
        limit=2,
        output_dir=tmp_path,
    )

    assert calls == ["TVQA-001", "TVQA-002"]
    assert report["judge_backend"] == "gemini"
    assert report["dataset_item_count"] == 2
    assert report["configs"][0]["metrics"]["faithfulness_avg"] == 0.8
    assert report["configs"][0]["items"][0]["diagnostic_question_family"] == "core_identity"
    assert report["configs"][0]["items"][1]["diagnostic_question_family"] == "menh_house_interpretation"
    assert "by_question_complexity" in report["configs"][0]["grouped_metrics"]
    assert "ablation_analysis" in report
    assert report["ablation_analysis"]["preliminary_recommendation"]["recommended_candidate"]
    assert len(store.rows) == 1
    assert store.rows[0]["status"] == "completed"
    assert store.rows[0]["metrics"]["answer_relevancy_avg"] == 0.7
    assert (tmp_path / "evaluation_report.json").exists()
    assert (tmp_path / "evaluation_report.md").exists()


def test_static_judge_is_marked_as_non_official_in_markdown(tmp_path: Path) -> None:
    report = {
        "manifest_name": "static-smoke",
        "dataset_path": "dataset.jsonl",
        "dataset_item_count": 1,
        "config_count": 1,
        "judge_backend": StaticEvaluationJudge.backend,
        "started_at": "start",
        "completed_at": "done",
        "configs": [
            {
                "config_name": "config",
                "status": "completed",
                "metrics": aggregate_evaluation_metrics([], expected_item_count=0),
                "grouped_metrics": {"by_question_complexity": {}, "by_question_family": {}},
                "items": [],
            }
        ],
    }

    markdown = render_markdown_report(report)

    assert "not an official W6 metric run" in markdown
    assert "Overall metrics" in markdown


def test_ablation_analysis_ranks_and_marks_retrieval_and_rerank_misses() -> None:
    report = {
        "configs": [
            {
                "config_name": "baseline_graph_sparse_rrf",
                "experiment_id": "baseline",
                "status": "completed",
                "reranker_enabled": True,
                "metrics": {
                    "context_recall_avg": 0.2,
                    "citation_coverage_rate": 0.0,
                    "faithfulness_avg": 0.5,
                    "answer_relevancy_avg": 0.6,
                    "graph_hit_rate": 0.0,
                    "p95_latency_ms": 100.0,
                },
                "items": [
                    {
                        "item_id": "TVQA-X",
                        "status": "completed",
                        "chart_only": False,
                        "question_complexity": "One-hop",
                        "question_family": "menh_house_interpretation",
                        "context_recall": 0.2,
                        "gold_doc_coverage_rate": 0.0,
                        "citation_coverage": 0.0,
                        "source_count": 1,
                        "context_selected_count": 1,
                        "diagnostic_candidate_counts": {"fused": 3, "ranked": 2, "context_selected": 1},
                        "diagnostic_selected_retrieval_paths": ["graph"],
                    }
                ],
            },
            {
                "config_name": "sparse_only_rrf",
                "experiment_id": "sparse",
                "status": "completed",
                "reranker_enabled": False,
                "metrics": {
                    "context_recall_avg": 0.8,
                    "citation_coverage_rate": 1.0,
                    "faithfulness_avg": 0.8,
                    "answer_relevancy_avg": 0.8,
                    "graph_hit_rate": 0.0,
                    "p95_latency_ms": 200.0,
                },
                "items": [],
            },
        ]
    }

    analysis = build_ablation_analysis(report)
    rendered = render_markdown_report({
        "manifest_name": "w6_abl_02_retrieval_fusion_reranker_v1",
        "dataset_path": "dataset.jsonl",
        "dataset_item_count": 1,
        "config_count": 2,
        "judge_backend": "gemini",
        "started_at": "start",
        "completed_at": "done",
        "configs": report["configs"],
        "ablation_analysis": analysis,
    })

    assert analysis["ranking_by_context_recall"][0]["config_name"] == "sparse_only_rrf"
    assert analysis["retrieval_miss_summary"][0]["miss_count"] == 1
    assert analysis["rerank_miss_summary"][0]["miss_count"] == 1
    assert "Ablation analysis" in rendered
    assert "Retrieval miss summary" in rendered
    assert "Rerank miss summary" in rendered


def test_chunking_ablation_analysis_is_vietnamese_and_ranks_strategies() -> None:
    configs = [
        {
            "config_name": "fixed_512_graph_sparse_rrf",
            "experiment_id": "fixed",
            "status": "completed",
            "chunk_strategy_id": "chunk_fixed_512",
            "metrics": {
                "context_recall_avg": 0.4,
                "citation_coverage_rate": 0.5,
                "graph_hit_rate": 0.6,
                "faithfulness_avg": 0.7,
                "answer_relevancy_avg": 0.7,
                "p95_latency_ms": 100.0,
            },
            "items": [],
        },
        {
            "config_name": "parent_child_graph_sparse_rrf",
            "experiment_id": "parent",
            "status": "completed",
            "chunk_strategy_id": "chunk_structure_parent_child",
            "metrics": {
                "context_recall_avg": 0.8,
                "citation_coverage_rate": 0.9,
                "graph_hit_rate": 0.7,
                "faithfulness_avg": 0.8,
                "answer_relevancy_avg": 0.8,
                "p95_latency_ms": 200.0,
            },
            "items": [],
        },
    ]
    report = {
        "manifest_name": "w6_abl_03_chunking_strategy_v1",
        "dataset_path": "dataset.jsonl",
        "dataset_item_count": 2,
        "config_count": 2,
        "judge_backend": "gemini",
        "started_at": "start",
        "completed_at": "done",
        "configs": configs,
        "ablation_analysis": build_ablation_analysis({"configs": configs}),
    }
    analysis = build_chunking_ablation_analysis(report)
    report["chunking_ablation_analysis"] = analysis
    rendered = render_markdown_report(report)

    assert analysis is not None
    assert analysis["ranking_by_context_recall"][0]["chunk_strategy_id"] == "chunk_structure_parent_child"
    assert analysis["preliminary_chunking_candidate"]["recommended_chunk_strategy_id"] == "chunk_structure_parent_child"
    assert "Phân tích ablation chiến lược chunking" in rendered
    assert "chunk_semantic_embedding_bge_m3" in rendered
    assert "Ứng viên chunking sơ bộ" in rendered


def test_generation_prompt_ablation_analysis_ranks_prompt_templates() -> None:
    configs = [
        {
            "config_name": "baseline_v1_flash_lite",
            "experiment_id": "baseline",
            "status": "completed",
            "prompt_template_id": "tuvi_generation_v1",
            "generation_model": "gemini-3.1-flash-lite-preview",
            "metrics": {
                "faithfulness_avg": 0.7,
                "answer_relevancy_avg": 0.7,
                "citation_coverage_rate": 0.6,
                "chart_context_grounding_avg": 0.8,
                "p95_latency_ms": 100.0,
            },
            "items": [],
        },
        {
            "config_name": "grounded_v2_flash_lite",
            "experiment_id": "grounded",
            "status": "completed",
            "prompt_template_id": "tuvi_generation_grounded_v2",
            "generation_model": "gemini-3.1-flash-lite-preview",
            "metrics": {
                "faithfulness_avg": 0.9,
                "answer_relevancy_avg": 0.85,
                "citation_coverage_rate": 0.8,
                "chart_context_grounding_avg": 0.8,
                "p95_latency_ms": 200.0,
            },
            "items": [],
        },
    ]
    report = {
        "manifest_name": "w7_abl_01_generation_prompt_v1",
        "dataset_path": "dataset.jsonl",
        "dataset_item_count": 2,
        "config_count": 2,
        "judge_backend": "gemini",
        "started_at": "start",
        "completed_at": "done",
        "configs": configs,
    }
    analysis = build_generation_prompt_ablation_analysis(report)
    report["generation_prompt_ablation_analysis"] = analysis
    rendered = render_markdown_report(report)

    assert analysis is not None
    assert analysis["ranking_by_faithfulness"][0]["prompt_template_id"] == "tuvi_generation_grounded_v2"
    assert analysis["preliminary_generation_candidate"]["recommended_prompt_template_id"] == "tuvi_generation_grounded_v2"
    assert "Phân tích ablation generation prompt/model" in rendered
    assert "tuvi_generation_grounded_v2" in rendered