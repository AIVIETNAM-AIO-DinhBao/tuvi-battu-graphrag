from __future__ import annotations

from pathlib import Path
from typing import Any

from app.rag.ablation import (
    AblationDatasetItem,
    AblationRunner,
    InMemoryExperimentRunStore,
    build_experiment_run_payload,
    load_ablation_dataset,
    load_ablation_manifest,
)
from app.rag.config import ExperimentConfig, load_experiment_config
from app.rag.generation import DeterministicGenerationClient
from app.rag.graph import run_rag_dry_run
from app.rag.rewrite import PassthroughQueryRewriter


ROOT_DIR = Path(__file__).resolve().parents[2]
SMOKE_MANIFEST_PATH = ROOT_DIR / "configs" / "w4_ablation_smoke.yaml"
RELEASE_DATASET_PATH = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "release" / "tuviqa_v1_release.jsonl"
REMOVED_TEMP_DATASET_PATH = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "w4_ablation_smoke.jsonl"


def config_with(**overrides: Any) -> ExperimentConfig:
    payload = load_experiment_config().model_dump(mode="json")
    payload.update(overrides)
    return ExperimentConfig.model_validate(payload)


def fake_rag_state(item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
    return {
        "answer": f"Câu trả lời thử nghiệm cho {item.id} bằng {config.experiment_id} [S1].",
        "sources": [
            {
                "citation_marker": "S1",
                "chunk_id": f"chunk-{item.id}",
                "chunk_hash": f"hash-{item.id}",
                "chunk_strategy_id": config.chunk_strategy_id,
                "source_id": "TVKL",
                "source_name": "Tử Vi Khảo Luận",
                "source_page": 12,
            }
        ],
        "citation_metadata": {"citation_fallback": False, "source_count": 1},
        "context_summary": {"selected_count": 1},
        "retrieval_trace": {
            "nodes": [
                {"node": "load_config", "status": "completed"},
                {"node": "generation", "status": "completed"},
                {"node": "citation_map", "status": "completed"},
            ]
        },
    }


class EmptyNeo4jSession:
    def __enter__(self) -> "EmptyNeo4jSession":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def execute_read(self, tx_func: Any, **kwargs: Any) -> list[Any]:
        return tx_func(self, **kwargs)

    def run(self, query: str, **kwargs: Any) -> list[Any]:
        return []


class EmptyNeo4jDriver:
    def session(self, **kwargs: Any) -> EmptyNeo4jSession:
        return EmptyNeo4jSession()


class FakeEmbeddingService:
    def embed_query(self, text: str) -> list[float]:
        return [0.0] * 1024


def test_smoke_manifest_loads_two_configs_and_dataset_items() -> None:
    manifest = load_ablation_manifest(SMOKE_MANIFEST_PATH)
    dataset = load_ablation_dataset(manifest.dataset_path, limit=2)

    assert manifest.name == "w4_abl_01_smoke"
    assert manifest.dataset_path == RELEASE_DATASET_PATH
    assert not REMOVED_TEMP_DATASET_PATH.exists()
    assert len(manifest.configs) == 2
    assert len(dataset) == 2
    assert dataset[0].id == "TVQA-001"
    assert dataset[0].chart_id == "CHART-001"
    assert dataset[0].query == "Cung Mệnh của lá số này nằm ở đâu và có những sao chính tinh nào?"
    assert dataset[0].chart_data and dataset[0].chart_data["chart_type"] == "TUVI"
    assert dataset[0].gold_answer
    assert dataset[0].expected_answer_summary
    assert dataset[0].gold_context_spans == []
    assert dataset[1].id == "TVQA-002"
    assert dataset[1].gold_context_spans
    assert dataset[1].question_complexity == "One-hop"

    configs = [spec.build_config() for spec in manifest.configs]
    assert [config.experiment_id for config in configs] == [
        "w4_abl_01_golden_smoke_rrf_balanced",
        "w4_abl_01_golden_smoke_graph_first",
    ]
    assert all(config.cache_disabled is True for config in configs)
    assert configs[0].fusion_method == "rrf"
    assert configs[1].fusion_method == "graph_first"


def test_ablation_runner_executes_two_by_two_matrix_and_writes_reports(tmp_path: Path) -> None:
    manifest = load_ablation_manifest(SMOKE_MANIFEST_PATH)
    store = InMemoryExperimentRunStore()
    calls: list[tuple[str, str]] = []

    def fake_runner(item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
        calls.append((item.id, config.experiment_id))
        return fake_rag_state(item, config)

    report = AblationRunner(run_store=store, rag_runner=fake_runner).run(manifest, limit=2, output_dir=tmp_path)

    assert len(calls) == 4
    assert report["dataset_item_count"] == 2
    assert report["config_count"] == 2
    assert {config["status"] for config in report["configs"]} == {"completed"}
    assert all(config["metrics"]["item_count"] == 2 for config in report["configs"])
    assert all(config["metrics"]["answer_present_rate"] == 1.0 for config in report["configs"])
    assert all(config["metrics"]["source_coverage_rate"] == 1.0 for config in report["configs"])
    assert all("avg_answer_token_recall_vs_summary" in config["metrics"] for config in report["configs"])
    assert all("summary_coverage_rate" in config["metrics"] for config in report["configs"])
    assert all("avg_gold_doc_coverage_rate" in config["metrics"] for config in report["configs"])
    assert all("avg_gold_page_hit_rate" in config["metrics"] for config in report["configs"])
    assert all("avg_gold_quote_overlap" in config["metrics"] for config in report["configs"])
    assert all("citation_marker_presence_rate" in config["metrics"] for config in report["configs"])
    assert all("citation_source_alignment_rate" in config["metrics"] for config in report["configs"])
    assert all("avg_char_ngram_similarity_vs_summary" in config["metrics"] for config in report["configs"])
    assert all("avg_rouge_l_like_vs_summary" in config["metrics"] for config in report["configs"])
    assert report["configs"][0]["items"][0]["item_id"] == "TVQA-001"
    assert report["configs"][0]["items"][1]["gold_span_count"] > 0

    assert len(store.rows) == 2
    assert [row["status"] for row in store.rows] == ["completed", "completed"]
    assert store.rows[0]["metrics"]["completed_count"] == 2
    assert (tmp_path / "ablation_report.json").exists()
    assert (tmp_path / "ablation_report.md").exists()


def test_ablation_runner_captures_item_failures_without_fail_fast(tmp_path: Path) -> None:
    manifest = load_ablation_manifest(SMOKE_MANIFEST_PATH)

    def flaky_runner(item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
        if item.id == "TVQA-002":
            raise RuntimeError("synthetic failure")
        return fake_rag_state(item, config)

    report = AblationRunner(rag_runner=flaky_runner).run(manifest, limit=2, output_dir=tmp_path)

    assert {config["status"] for config in report["configs"]} == {"completed"}
    assert all(config["metrics"]["completed_count"] == 1 for config in report["configs"])
    assert all(config["metrics"]["failed_count"] == 1 for config in report["configs"])
    assert "synthetic failure" in report["configs"][0]["items"][1]["error"]


def test_experiment_run_payload_contains_required_experiment_runs_fields() -> None:
    manifest = load_ablation_manifest(SMOKE_MANIFEST_PATH)
    config = manifest.configs[0].build_config()

    payload = build_experiment_run_payload(config=config, manifest=manifest, status="running")

    assert payload["experiment_id"] == config.experiment_id
    assert payload["config_name"] == config.name
    assert payload["config_hash"]
    assert payload["config"]["chunk_strategy_id"] == config.chunk_strategy_id
    assert payload["status"] == "running"
    assert payload["metrics"] == {}
    assert payload["trace"]["manifest_name"] == manifest.name
    assert payload["started_at"]


def test_run_rag_dry_run_accepts_in_memory_experiment_config() -> None:
    config = config_with(
        experiment_id="in_memory_config_test",
        name="In-memory config test",
        graph_retrieval_enabled=False,
        dense_retrieval_enabled=False,
        sparse_retrieval_enabled=False,
    )

    state = run_rag_dry_run(
        {"query": "Cung Mệnh là gì?", "chart_id": "chart-1", "user_id": "user-1"},
        experiment_config=config,
        chart_loader=lambda chart_id, user_id=None: {
            "id": chart_id,
            "user_id": user_id,
            "chart_system": "TUVI",
            "chart_data": {"chart_type": "TUVI", "metadata": {"label": "In-memory"}},
        },
        query_rewriter=PassthroughQueryRewriter(),
        neo4j_driver=EmptyNeo4jDriver(),
        dense_embedding_service=FakeEmbeddingService(),
        generation_client=DeterministicGenerationClient(),
    )

    assert state["experiment_id"] == "in_memory_config_test"
    assert state["experiment_config"].name == "In-memory config test"
    assert state["graph_candidates"] == []
    assert state["answer"]