from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from app.rag.ablation import load_ablation_manifest
from scripts.prepare_p6_kaggle import notebook_config
from scripts.prepare_sequential_phase import TWO_PERSON_ASSIGNMENTS, phase_specs
from scripts.analyze_sequential_phase import paired_bootstrap, retrieval_recall
from scripts.create_ablation_ticket import command_for
from scripts.check_sequential_preflight import config_isolation
from scripts import run_retrieval_eval


ROOT_DIR = Path(__file__).resolve().parents[2]
P1_MANIFEST = ROOT_DIR / "configs" / "ablation_sequential" / "p1_chunking.yaml"


def test_p1_changes_only_chunk_strategy_and_identity() -> None:
    manifest = load_ablation_manifest(P1_MANIFEST)
    assert config_isolation(manifest) is True
    configs = [spec.build_config() for spec in manifest.configs]
    controls = []
    for config in configs:
        payload = config.model_dump(mode="json")
        for key in ("experiment_id", "name", "chunk_strategy_id"):
            payload.pop(key)
        controls.append(payload)

    assert len(configs) == 3
    assert all(control == controls[0] for control in controls)
    assert {config.chunk_strategy_id for config in configs} == {
        "chunk_fixed_512",
        "chunk_structure_parent_child",
        "chunk_semantic_embedding_bge_m3",
    }
    for config in configs:
        assert config.graph_retrieval_enabled is False
        assert config.dense_retrieval_enabled is True
        assert config.sparse_retrieval_enabled is True
        assert config.fusion_method == "rrf"
        assert config.fusion_path_weights["graph"] == 1.0
        assert config.fusion_path_weights["dense"] == 1.0
        assert config.fusion_path_weights["sparse"] == 1.0
        assert config.reranker_enabled is False
        assert config.reranker_config.top_k == 20
        assert config.reranker_config.cap_fused_candidates_when_disabled is True
        assert config.prompt_template_id == "tuvi_generation_structured_v3"


def test_two_person_shards_cover_every_candidate_once() -> None:
    for phase in ("p2", "p3", "p4", "p5"):
        _, _, specs = phase_specs(phase, "configs/locked.yaml")
        expected = {spec["name"] for spec in specs}
        assigned_a = TWO_PERSON_ASSIGNMENTS[phase]["A"]
        assigned_b = TWO_PERSON_ASSIGNMENTS[phase]["B"]
        assert assigned_a.isdisjoint(assigned_b)
        assert assigned_a | assigned_b == expected


def test_p3_uses_the_registered_three_prompt_shortlist() -> None:
    _, _, specs = phase_specs("p3", "configs/locked.yaml")

    assert [spec["name"] for spec in specs] == ["p3_prompt_1", "p3_prompt_2", "p3_prompt_3"]
    assert [spec["overrides"]["prompt_template_id"] for spec in specs] == [
        "tuvi_generation_v1",
        "tuvi_generation_grounded_v2",
        "tuvi_generation_answer_first_v4",
    ]


def test_p6_notebooks_are_preconfigured_for_official_run() -> None:
    source = "".join(notebook_config("gemma3_4b", "sequential_final_1::p6_frozen_context"))

    assert "RUN_MODE = 'official'" in source
    assert "MODEL_KEY = 'gemma3_4b'" in source
    assert "sequential_final_1::p6_frozen_context" in source
    assert "RUN_MODE = 'smoke'" not in source


def test_retrieval_runner_never_invokes_generation_or_citation(monkeypatch) -> None:
    executed: list[str] = []

    def make_node(name: str):
        def node(state):
            executed.append(name)
            return state

        return node

    nodes = {name: make_node(name) for name in run_retrieval_eval.DRY_RUN_NODE_ORDER}
    monkeypatch.setattr(run_retrieval_eval, "build_node_map", lambda **kwargs: nodes)
    item = SimpleNamespace(
        chart_id="CHART-001",
        query="test",
        user_id=None,
        question_complexity="One-hop",
        labels={"question_family": "test"},
        chart_data={},
    )

    run_retrieval_eval.run_live_retrieval(item, SimpleNamespace())

    assert "generation" not in executed
    assert "citation_map" not in executed
    assert executed[-1] == "retrieval_diagnostics"


def test_paired_bootstrap_uses_the_same_full_100_items() -> None:
    control_items = [
        {
            "item_id": f"TVQA-{index:03d}",
            "status": "completed",
            "token_overlap_span_details": [{"hit": index % 2 == 0}],
        }
        for index in range(100)
    ]
    winner_items = [
        {
            "item_id": f"TVQA-{index:03d}",
            "status": "completed",
            "token_overlap_span_details": [{"hit": True}],
        }
        for index in range(100)
    ]
    result = paired_bootstrap(
        {"items": winner_items},
        {"items": control_items},
        metric=retrieval_recall,
        samples=1_000,
        seed=42,
    )

    assert result["paired_item_count"] == 100
    assert result["delta_ci95"][0] > 0
    assert result["outcome"] == "better"


def test_human_ticket_command_is_full_run_and_execution_policy_safe() -> None:
    command = command_for(
        P1_MANIFEST,
        "benchmark/tuvi_golden_dataset/sequential_ablation/results/P1_chunking",
        "p1",
        resume=False,
    )

    assert "powershell -NoProfile -ExecutionPolicy Bypass -File" in command
    assert "run_retrieval_phase.ps1" in command
    assert "--limit" not in command
    assert "-Resume" not in command


def test_p3_and_p5_tickets_require_shared_bundle_runners() -> None:
    p3 = command_for(P1_MANIFEST, "out/p3", "p3", resume=False, bundle="shared/p3")
    p5 = command_for(P1_MANIFEST, "out/p5", "p5", resume=False, bundle="shared/p5")

    assert "run_p3_frozen_prompt_phase.ps1" in p3
    assert "-FrozenBundle 'shared\\p3'" in p3
    assert "run_p5_replay_phase.ps1" in p5
    assert "-Bundle 'shared\\p5'" in p5
    assert "CheckpointDir" not in p5


def test_retrieval_markdown_keeps_only_compact_headline_metrics() -> None:
    markdown = run_retrieval_eval.render_markdown(
        {
            "manifest_name": "test",
            "status": "completed",
            "dataset_item_count": 100,
            "anchor_summary": {"mapping_coverage": 0.86},
            "configs": [
                {
                    "config_name": "candidate",
                    "status": "completed",
                    "metrics": {
                        "recall_at_8": 0.8,
                        "precision_at_8": 0.7,
                        "f1_at_8": 0.746667,
                        "retrieval_p95_ms": 123.0,
                        "failed_count": 0,
                        "character_recall": 0.9,
                        "fused_gold_span_recall": 0.95,
                    },
                }
            ],
        }
    )

    assert "Recall@8" in markdown
    assert "Precision@8" in markdown
    assert "F1@8" in markdown
    assert "Retrieval p95 ms" in markdown
    assert "Char R" not in markdown
    assert "Fused R" not in markdown
