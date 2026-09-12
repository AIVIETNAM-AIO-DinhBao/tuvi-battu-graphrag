"""Create a deterministic decision draft for one completed sequential phase."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from statistics import mean
from typing import Any, Callable


ROOT_DIR = Path(__file__).resolve().parent.parent
CONTROL_BY_PHASE = {
    "p1": "p1_fixed_512",
    "p2": "p2_dense_sparse",
    "p3": "p3_rerank_off",
    "p4": "p4_retention_20",
    "p5": "p5_prompt_2",
}
RETRIEVAL_PHASES = {"p1", "p2", "p3", "p4"}
BOOTSTRAP_TIE_THRESHOLD = 0.01


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a completed one-factor ablation report.")
    parser.add_argument("--phase", choices=sorted(CONTROL_BY_PHASE), required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="Decision draft JSON path.")
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.bootstrap_samples < 1_000:
        parser.error("--bootstrap-samples must be at least 1000.")
    return args


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def completed_items(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item["item_id"]): item
        for item in config.get("items") or []
        if item.get("status") == "completed" and item.get("item_id")
    }


def retrieval_recall(items: list[dict[str, Any]]) -> float:
    details = [detail for item in items for detail in item.get("token_overlap_span_details") or []]
    if not details:
        raise ValueError("No token-overlap gold-span details in bootstrap sample.")
    return sum(bool(detail.get("hit")) for detail in details) / len(details)


def generation_faithfulness(items: list[dict[str, Any]]) -> float:
    values = [float(item["faithfulness"]) for item in items if item.get("faithfulness") is not None]
    if not values:
        raise ValueError("No faithfulness values in bootstrap sample.")
    return mean(values)


def paired_bootstrap(
    winner: dict[str, Any],
    control: dict[str, Any],
    *,
    metric: Callable[[list[dict[str, Any]]], float],
    samples: int,
    seed: int,
) -> dict[str, Any]:
    winner_items = completed_items(winner)
    control_items = completed_items(control)
    paired_ids = sorted(set(winner_items) & set(control_items))
    if len(paired_ids) != 100:
        raise ValueError(f"Paired bootstrap requires exactly 100 shared completed items; found {len(paired_ids)}.")
    rng = random.Random(seed)
    deltas: list[float] = []
    for _ in range(samples):
        sampled_ids = [paired_ids[rng.randrange(len(paired_ids))] for _ in paired_ids]
        left = metric([winner_items[item_id] for item_id in sampled_ids])
        right = metric([control_items[item_id] for item_id in sampled_ids])
        deltas.append(left - right)
    deltas.sort()
    lower = deltas[int(0.025 * (samples - 1))]
    upper = deltas[int(0.975 * (samples - 1))]
    observed_delta = metric(list(winner_items.values())) - metric(list(control_items.values()))
    if lower > 0:
        outcome = "better"
    elif upper < 0:
        outcome = "worse"
    else:
        outcome = "inconclusive"
    return {
        "paired_item_count": len(paired_ids),
        "samples": samples,
        "seed": seed,
        "delta_mean": round(mean(deltas), 6),
        "paired_delta_observed": round(observed_delta, 6),
        "delta_ci95": [round(lower, 6), round(upper, 6)],
        "probability_delta_gt_zero": round(sum(delta > 0 for delta in deltas) / samples, 6),
        "outcome": outcome,
    }


def primary_value(config: dict[str, Any], phase: str) -> float:
    metrics = config.get("metrics") or {}
    key = "recall_at_8" if phase in RETRIEVAL_PHASES else "faithfulness_avg"
    value = metrics.get(key)
    if value is None:
        raise ValueError(f"{config.get('config_name')} is missing {key}.")
    return float(value)


def guardrail(config: dict[str, Any], control: dict[str, Any], phase: str) -> tuple[bool, str]:
    metrics = config.get("metrics") or {}
    control_metrics = control.get("metrics") or {}
    if phase in RETRIEVAL_PHASES:
        value = metrics.get("precision_at_8")
        baseline = control_metrics.get("precision_at_8")
        passed = value is not None and baseline is not None and float(value) >= float(baseline) - 0.02
        return passed, f"precision={value}; floor={None if baseline is None else round(float(baseline) - 0.02, 6)}"
    relevancy = metrics.get("answer_relevancy_avg")
    baseline = control_metrics.get("answer_relevancy_avg")
    invalid_markers = int(metrics.get("invalid_citation_marker_count") or 0)
    passed = (
        relevancy is not None
        and baseline is not None
        and float(relevancy) >= float(baseline) - 0.02
        and invalid_markers == 0
    )
    return passed, (
        f"invalid_markers={invalid_markers}; relevancy={relevancy}; "
        f"relevancy_floor={None if baseline is None else round(float(baseline) - 0.02, 6)}"
    )


def render_markdown(decision: dict[str, Any]) -> str:
    retrieval_phase = decision["phase"] in RETRIEVAL_PHASES
    lines = [
        f"# {decision['phase'].upper()} decision draft",
        "",
        f"- Recommended winner: `{decision['recommended_winner']}`",
        f"- Control: `{decision['control']}`",
        f"- Primary metric: `{decision['primary_metric']}`",
        f"- Report SHA-256: `{decision['report_sha256']}`",
        f"- Selection rule: {decision.get('selection_rule', 'Highest primary metric among candidates that pass the pre-registered guardrail.')}",
        "",
    ]
    if retrieval_phase:
        lines.extend(
            [
                "| Candidate | Evidence Recall | Evidence Precision | Evidence F1 | Guardrail | Note |",
                "|---|---:|---:|---:|---|---|",
            ]
        )
    else:
        lines.extend(
            [
                "| Candidate | Faithfulness | Answer Relevancy | Latency p95 ms | Guardrail | Note |",
                "|---|---:|---:|---:|---|---|",
            ]
        )
    for row in decision["ranking"]:
        if retrieval_phase:
            lines.append(
                f"| {row['config_name']} | {row['primary_value']:.6f} | "
                f"{row['precision_at_8'] if row['precision_at_8'] is not None else 'N/A'} | "
                f"{row['f1_at_8'] if row['f1_at_8'] is not None else 'N/A'} | "
                f"{'PASS' if row['guardrail_passed'] else 'FAIL'} | {row['guardrail_note']} |"
            )
        else:
            lines.append(
                f"| {row['config_name']} | {row['primary_value']:.6f} | "
                f"{row['answer_relevancy'] if row['answer_relevancy'] is not None else 'N/A'} | "
                f"{row['latency_p95_ms'] if row['latency_p95_ms'] is not None else 'N/A'} | "
                f"{'PASS' if row['guardrail_passed'] else 'FAIL'} | {row['guardrail_note']} |"
            )
    bootstrap = decision["winner_vs_challenger_bootstrap"]
    lines.extend(["", "## Paired bootstrap", ""])
    if bootstrap["performed"]:
        lines.extend(
            [
                f"- Comparison: `{decision.get('bootstrap_candidate', decision['recommended_winner'])}` minus `{decision['bootstrap_challenger']}`",
                f"- Mean delta: `{bootstrap['delta_mean']}`",
                f"- Observed paired delta: `{bootstrap['paired_delta_observed']}`",
                f"- 95% CI: `{bootstrap['delta_ci95']}`",
                f"- P(delta > 0): `{bootstrap['probability_delta_gt_zero']}`",
                f"- Outcome: **{bootstrap['outcome']}**",
            ]
        )
    else:
        lines.append(f"- Not performed: {bootstrap['reason']}")
    if decision.get("raw_primary_leader") and decision["raw_primary_leader"] != decision["recommended_winner"]:
        lines.extend(
            [
                "",
                "## Applied P4 tie-break",
                "",
                f"`{decision['raw_primary_leader']}` has the highest raw Evidence Recall, but its paired comparison with "
                f"`{decision['bootstrap_challenger']}` is inconclusive. The pre-registered lower-depth tie-break therefore selects "
                f"`{decision['recommended_winner']}`; raw scores are retained unchanged.",
            ]
        )
    lines.extend(
        [
            "",
            "This file is a deterministic draft. A must review failures, hashes and factor isolation before locking the winner.",
            "",
        ]
    )
    return "\n".join(lines)


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    report_path = resolve(args.report).resolve()
    output_path = resolve(args.output).resolve()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    execution = report.get("execution_summary") or {}
    if report.get("status") != "completed" or int(execution.get("failed_pair_count", -1)) != 0:
        raise SystemExit("Analysis requires a completed report with zero failed pairs.")
    configs = {str(config.get("config_name")): config for config in report.get("configs") or []}
    control_name = CONTROL_BY_PHASE[args.phase]
    if control_name not in configs:
        raise SystemExit(f"Required control {control_name!r} is missing from report.")
    control = configs[control_name]
    ranking: list[dict[str, Any]] = []
    for name, config in configs.items():
        passed, note = guardrail(config, control, args.phase)
        ranking.append(
            {
                "config_name": name,
                "primary_value": primary_value(config, args.phase),
                "precision_at_8": (config.get("metrics") or {}).get("precision_at_8"),
                "f1_at_8": (config.get("metrics") or {}).get("f1_at_8"),
                "citation_evidence_f1": (config.get("metrics") or {}).get("citation_evidence_f1_avg"),
                "answer_relevancy": (config.get("metrics") or {}).get("answer_relevancy_avg"),
                "latency_p95_ms": (config.get("metrics") or {}).get("p95_latency_ms"),
                "guardrail_passed": passed,
                "guardrail_note": note,
            }
        )
    eligible = [row for row in ranking if row["guardrail_passed"]]
    if not eligible:
        raise SystemExit("No candidate passes the pre-registered guardrail.")
    eligible.sort(key=lambda row: (-row["primary_value"], row["config_name"]))
    recommended = eligible[0]["config_name"]
    raw_primary_leader = recommended
    ranking.sort(key=lambda row: (-row["primary_value"], row["config_name"]))
    metric = retrieval_recall if args.phase in RETRIEVAL_PHASES else generation_faithfulness
    challenger = eligible[1]["config_name"] if len(eligible) > 1 else None
    primary_gap = (
        eligible[0]["primary_value"] - eligible[1]["primary_value"] if challenger is not None else None
    )
    if challenger is not None and primary_gap is not None and primary_gap < BOOTSTRAP_TIE_THRESHOLD:
        bootstrap = {
            "performed": True,
            **paired_bootstrap(
                configs[recommended],
                configs[challenger],
                metric=metric,
                samples=args.bootstrap_samples,
                seed=args.seed,
            ),
        }
    else:
        bootstrap = {
            "performed": False,
            "reason": (
                "Only one candidate passed the guardrail."
                if challenger is None
                else f"Top-two primary gap {primary_gap:.6f} is not below {BOOTSTRAP_TIE_THRESHOLD:.2f}."
            ),
        }
    selection_rule = "Highest primary metric among candidates that pass the pre-registered guardrail."
    # P4 registers a complexity tie-break: when the top two retention depths are
    # not distinguishable by the paired bootstrap, retain fewer candidates.
    if args.phase == "p4" and bootstrap.get("performed") and bootstrap.get("outcome") == "inconclusive":
        tied = [eligible[0], eligible[1]]
        recommended = min(
            tied,
            key=lambda row: int((configs[row["config_name"]].get("reranker_top_k") or 0)),
        )["config_name"]
        selection_rule = (
            "P4 pre-registered complexity tie-break: paired bootstrap was inconclusive, "
            "so select the smaller reranked candidate-retention depth."
        )
    decision = {
        "schema_version": "sequential-decision-draft-v1",
        "phase": args.phase,
        "report": str(report_path),
        "report_sha256": sha256_file(report_path),
        "control": control_name,
        "primary_metric": "recall_at_8" if args.phase in RETRIEVAL_PHASES else "faithfulness_avg",
        "recommended_winner": recommended,
        "raw_primary_leader": raw_primary_leader,
        "selection_rule": selection_rule,
        "ranking": ranking,
        "bootstrap_candidate": raw_primary_leader,
        "bootstrap_challenger": challenger,
        "winner_vs_challenger_bootstrap": bootstrap,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    markdown_path = output_path.with_suffix(".md")
    markdown_path.write_text(render_markdown(decision), encoding="utf-8", newline="\n")
    print(json.dumps({"recommended_winner": recommended, "json": str(output_path), "markdown": str(markdown_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
