"""Audit W3-INGEST-07 full-corpus acceptance artifacts.

The audit is intentionally file-based: it verifies the acceptance evidence
without calling Gemini, Qwen, Neo4j, or Supabase.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATASET_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset"
DEFAULT_CHUNKS_DIR = ROOT_DIR / "notebooks" / "w3_local_outputs" / "chunks"
DEFAULT_REPORTS_DIR = DEFAULT_DATASET_DIR / "gemini_call" / "reports"
DEFAULT_ENTITIES_DIR = DEFAULT_DATASET_DIR / "gemini_call" / "entities"
DEFAULT_PAYLOADS_DIR = DEFAULT_DATASET_DIR / "gemini_call" / "payloads"
DEFAULT_EMBEDDINGS_DIR = DEFAULT_DATASET_DIR / "gemini_call" / "embeddings"
DEFAULT_SOURCES = ["TVKL", "TVNL", "TVHS", "TVGM"]
DEFAULT_STRATEGIES = [
    "chunk_fixed_512",
    "chunk_structure_parent_child",
    "chunk_semantic_embedding_bge_m3",
]
SEMANTIC_REPORT_STRATEGIES = {"chunk_semantic_embedding_bge_m3"}
PARENT_CHILD_STRATEGY = "chunk_structure_parent_child"
EXPECTED_BASELINE_COUNTS = {
    "chunk_fixed_512": {
        "chunks": 1158,
        "relations": 853,
        "canonical_relations": 493,
        "supabase_source_chunks": 1158,
    },
    "chunk_structure_parent_child": {
        "chunks": 4504,
        "relations": 9410,
        "canonical_relations": 1234,
        "supabase_source_chunks": 4504,
    },
    "chunk_semantic_embedding_bge_m3": {
        "chunks": 1690,
        "relations": 1217,
        "canonical_relations": 690,
        "supabase_source_chunks": 1690,
    },
}
REQUIRED_PAYLOAD_FILES = [
    "source_records.jsonl",
    "chunk_records.jsonl",
    "entity_records.jsonl",
    "mention_records.jsonl",
    "relation_records.jsonl",
    "canonical_relation_records.jsonl",
    "summary.json",
]


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def add_issue(issues: list[dict[str, Any]], check: str, message: str, **context: Any) -> None:
    issue = {"check": check, "message": message}
    if context:
        issue["context"] = context
    issues.append(issue)


def add_warning(warnings: list[dict[str, Any]], check: str, message: str, **context: Any) -> None:
    warning = {"check": check, "message": message}
    if context:
        warning["context"] = context
    warnings.append(warning)


def nested_get(payload: dict[str, Any], path: Iterable[str], default: Any = None) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL record: {exc}") from exc


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return list(iter_jsonl(path))


def count_jsonl(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def safe_read_json(path: Path, issues: list[dict[str, Any]], check: str) -> dict[str, Any] | None:
    if not path.exists():
        add_issue(issues, check, "missing JSON artifact", path=str(path))
        return None
    try:
        return read_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        add_issue(issues, check, "cannot read JSON artifact", path=str(path), error=str(exc))
        return None


def safe_read_jsonl(path: Path, issues: list[dict[str, Any]], check: str) -> list[dict[str, Any]]:
    if not path.exists():
        add_issue(issues, check, "missing JSONL artifact", path=str(path))
        return []
    try:
        return read_jsonl(path)
    except (OSError, ValueError) as exc:
        add_issue(issues, check, "cannot read JSONL artifact", path=str(path), error=str(exc))
        return []


def summarize_chunk_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_source: dict[str, dict[str, Any]] = {}
    for source_id in sorted({str(record.get("source_id")) for record in records}):
        selected = [record for record in records if str(record.get("source_id")) == source_id]
        by_source[source_id] = {
            "chunk_type_counts": dict(sorted(Counter(str(record.get("chunk_type")) for record in selected).items())),
            "retrieval_unit_chunks": sum(1 for record in selected if record.get("metadata", {}).get("retrieval_unit")),
            "total_chunks": len(selected),
        }
    return {
        "chunk_type_counts": dict(sorted(Counter(str(record.get("chunk_type")) for record in records).items())),
        "documents": by_source,
        "total_chunks": len(records),
    }


def compare_chunk_outputs(
    canonical: list[dict[str, Any]],
    regenerated: list[dict[str, Any]],
) -> dict[str, Any]:
    canonical_by_id = {str(record.get("chunk_id")): record for record in canonical}
    regenerated_by_id = {str(record.get("chunk_id")): record for record in regenerated}
    missing = sorted(set(canonical_by_id) - set(regenerated_by_id))
    extra = sorted(set(regenerated_by_id) - set(canonical_by_id))
    mismatches: list[dict[str, Any]] = []
    for chunk_id in sorted(set(canonical_by_id) & set(regenerated_by_id)):
        left = canonical_by_id[chunk_id]
        right = regenerated_by_id[chunk_id]
        for field in ("chunk_hash", "chunk_type", "parent_id"):
            if left.get(field) != right.get(field):
                mismatches.append(
                    {
                        "chunk_id": chunk_id,
                        "field": field,
                        "canonical": left.get(field),
                        "regenerated": right.get(field),
                    }
                )
                break
    return {
        "canonical_count": len(canonical),
        "completed": not missing and not extra and not mismatches and len(canonical) == len(regenerated),
        "extra_chunk_ids": extra[:20],
        "missing_chunk_ids": missing[:20],
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:20],
        "regenerated_count": len(regenerated),
    }


def audit_chunks(
    *,
    chunks_dir: Path,
    reports_dir: Path,
    regen_chunks_dir: Path | None,
    sources: list[str],
    strategies: list[str],
    issues: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for strategy in strategies:
        strategy_records: list[dict[str, Any]] = []
        source_counts: dict[str, int] = {}
        for source in sources:
            path = chunks_dir / strategy / f"{source}_chunks.jsonl"
            records = safe_read_jsonl(path, issues, "chunks")
            source_counts[source] = len(records)
            for record in records:
                if str(record.get("source_id")) != source:
                    add_issue(
                        issues,
                        "chunks",
                        "chunk source_id does not match file source",
                        path=str(path),
                        chunk_id=record.get("chunk_id"),
                        expected=source,
                        actual=record.get("source_id"),
                    )
                if str(record.get("chunk_strategy_id")) != strategy:
                    add_issue(
                        issues,
                        "chunks",
                        "chunk_strategy_id does not match strategy",
                        path=str(path),
                        chunk_id=record.get("chunk_id"),
                        expected=strategy,
                        actual=record.get("chunk_strategy_id"),
                    )
            strategy_records.extend(records)

        summary_path = reports_dir / f"{strategy}_chunk_summary.json"
        summary = safe_read_json(summary_path, issues, "chunk_summary")
        if summary:
            if int(summary.get("total_chunks") or -1) != len(strategy_records):
                add_issue(
                    issues,
                    "chunk_summary",
                    "chunk summary total does not match canonical chunks",
                    strategy=strategy,
                    expected=len(strategy_records),
                    actual=summary.get("total_chunks"),
                )
            for source, expected_count in source_counts.items():
                actual_count = nested_get(summary, ["documents", source, "total_chunks"])
                if actual_count != expected_count:
                    add_issue(
                        issues,
                        "chunk_summary",
                        "chunk summary source total does not match canonical chunks",
                        strategy=strategy,
                        source_id=source,
                        expected=expected_count,
                        actual=actual_count,
                    )

        semantic_report = None
        if strategy in SEMANTIC_REPORT_STRATEGIES:
            semantic_report_path = reports_dir / f"{strategy}_semantic_similarity_report.json"
            semantic_report = safe_read_json(semantic_report_path, issues, "semantic_report")
            if semantic_report:
                if semantic_report.get("chunk_strategy_id") != strategy:
                    add_issue(
                        issues,
                        "semantic_report",
                        "semantic report strategy mismatch",
                        expected=strategy,
                        actual=semantic_report.get("chunk_strategy_id"),
                    )
                if int(semantic_report.get("event_count") or 0) <= 0:
                    add_issue(issues, "semantic_report", "semantic report has no similarity events", strategy=strategy)

        regen_compare = None
        if regen_chunks_dir is not None:
            regen_strategy_dir = regen_chunks_dir / strategy
            if not regen_strategy_dir.exists():
                add_warning(
                    warnings,
                    "chunk_regeneration",
                    "regenerated chunks are not present for strategy; comparison skipped",
                    strategy=strategy,
                )
            else:
                regen_records: list[dict[str, Any]] = []
                for source in sources:
                    regen_path = regen_strategy_dir / f"{source}_chunks.jsonl"
                    regen_records.extend(safe_read_jsonl(regen_path, issues, "chunk_regeneration"))
                regen_compare = compare_chunk_outputs(strategy_records, regen_records)
                if not regen_compare["completed"]:
                    add_issue(
                        issues,
                        "chunk_regeneration",
                        "regenerated chunks do not match canonical chunks",
                        strategy=strategy,
                        comparison=regen_compare,
                    )
        else:
            add_warning(warnings, "chunk_regeneration", "no regenerated chunks dir supplied; comparison skipped", strategy=strategy)

        result[strategy] = {
            **summarize_chunk_records(strategy_records),
            "chunk_summary_output": str(summary_path),
            "regeneration_comparison": regen_compare,
            "semantic_report_output": (
                str(reports_dir / f"{strategy}_semantic_similarity_report.json")
                if strategy in SEMANTIC_REPORT_STRATEGIES
                else None
            ),
            "semantic_report_event_count": semantic_report.get("event_count") if semantic_report else None,
        }
    return result


def audit_entities_and_reviews(
    *,
    entities_dir: Path,
    reports_dir: Path,
    strategies: list[str],
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for strategy in strategies:
        entity_path = entities_dir / strategy / f"{strategy}_entities.jsonl"
        entity_count = count_jsonl(entity_path) if entity_path.exists() else 0
        if not entity_path.exists():
            add_issue(issues, "entities", "missing entity JSONL", strategy=strategy, path=str(entity_path))
        elif entity_count <= 0:
            add_issue(issues, "entities", "entity JSONL is empty", strategy=strategy, path=str(entity_path))
        entity_review = reports_dir / f"{strategy}_entity_review.json"
        relation_review = reports_dir / f"{strategy}_relation_review.json"
        if not entity_review.exists():
            add_issue(issues, "reviews", "missing entity review", strategy=strategy, path=str(entity_review))
        if not relation_review.exists():
            add_issue(issues, "reviews", "missing relation review", strategy=strategy, path=str(relation_review))
        result[strategy] = {
            "entity_count": entity_count,
            "entity_jsonl": str(entity_path),
            "entity_review": str(entity_review),
            "relation_review": str(relation_review),
        }
    return result


def payload_line_counts(payload_dir: Path) -> dict[str, int]:
    return {
        path.stem: count_jsonl(path)
        for path in sorted(payload_dir.glob("*.jsonl"))
    }


def duplicate_chunk_hashes(chunk_records_path: Path) -> list[dict[str, Any]]:
    ids_by_hash: dict[str, list[str]] = defaultdict(list)
    for record in iter_jsonl(chunk_records_path):
        chunk_hash = str(record.get("chunk_hash") or "")
        ids_by_hash[chunk_hash].append(str(record.get("chunk_id")))
    return [
        {"chunk_hash": chunk_hash, "chunk_ids": chunk_ids}
        for chunk_hash, chunk_ids in sorted(ids_by_hash.items())
        if chunk_hash and len(chunk_ids) > 1
    ]


def audit_payloads_and_graph(
    *,
    payloads_dir: Path,
    reports_dir: Path,
    import_checks_dir: Path,
    strategies: list[str],
    enforce_baseline_counts: bool,
    issues: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    supabase_total = 0
    for strategy in strategies:
        payload_dir = payloads_dir / strategy
        for file_name in REQUIRED_PAYLOAD_FILES:
            path = payload_dir / file_name
            if not path.exists():
                add_issue(issues, "payload", "missing payload file", strategy=strategy, path=str(path))

        line_counts = payload_line_counts(payload_dir) if payload_dir.exists() else {}
        duplicates = (
            duplicate_chunk_hashes(payload_dir / "chunk_records.jsonl")
            if (payload_dir / "chunk_records.jsonl").exists()
            else []
        )
        if duplicates and strategy != PARENT_CHILD_STRATEGY:
            add_warning(warnings, "payload", "duplicate chunk hashes outside parent-child strategy", strategy=strategy)

        payload_summary = safe_read_json(payload_dir / "summary.json", issues, "payload_summary")
        graph_summary = safe_read_json(reports_dir / f"{strategy}_graph_write_summary.json", issues, "graph_summary")
        import_graph_summary = safe_read_json(import_checks_dir / f"import_graph_{strategy}.json", issues, "import_graph")

        if payload_summary:
            for stem, actual_count in line_counts.items():
                expected = payload_summary.get("payload_record_counts", {}).get(stem)
                if expected is not None and int(expected) != actual_count:
                    add_issue(
                        issues,
                        "payload_summary",
                        "payload summary line count mismatch",
                        strategy=strategy,
                        file=stem,
                        expected=expected,
                        actual=actual_count,
                    )

        strategy_counts: dict[str, Any] = {}
        if graph_summary:
            if graph_summary.get("completed") is not True:
                add_issue(issues, "graph_summary", "graph summary is not completed", strategy=strategy)
            if graph_summary.get("dry_run") is not False:
                add_issue(issues, "graph_summary", "graph summary was not a real DB write", strategy=strategy)
            db_counts = graph_summary.get("db_write_counts") or {}
            supabase_count = int(db_counts.get("supabase_source_chunks") or 0)
            supabase_total += supabase_count
            strategy_counts = {
                "canonical_relations": nested_get(db_counts, ["neo4j", "canonical_relations"], graph_summary.get("canonical_relation_count")),
                "chunks": nested_get(db_counts, ["neo4j", "chunks"], graph_summary.get("chunk_count")),
                "relations": nested_get(db_counts, ["neo4j", "relations"]),
                "supabase_source_chunks": supabase_count,
            }
            if enforce_baseline_counts and strategy in EXPECTED_BASELINE_COUNTS:
                for key, expected in EXPECTED_BASELINE_COUNTS[strategy].items():
                    actual = strategy_counts.get(key)
                    if int(actual or -1) != expected:
                        add_issue(
                            issues,
                            "baseline_counts",
                            "strategy baseline count mismatch",
                            strategy=strategy,
                            key=key,
                            expected=expected,
                            actual=actual,
                        )
            relation_drop_counts = graph_summary.get("relation_drop_counts")
            if relation_drop_counts == {}:
                add_warning(
                    warnings,
                    "graph_summary",
                    "relation_drop_counts is empty because graph write resumed from previous LLM state",
                    strategy=strategy,
                )

        if import_graph_summary:
            if import_graph_summary.get("dry_run") is not True:
                add_issue(issues, "import_graph", "graph import check was not a dry-run", strategy=strategy)
            import_chunks = import_graph_summary.get("chunk_count")
            if graph_summary and import_chunks != graph_summary.get("chunk_count"):
                add_issue(
                    issues,
                    "import_graph",
                    "graph import dry-run chunk count mismatch",
                    strategy=strategy,
                    expected=graph_summary.get("chunk_count"),
                    actual=import_chunks,
                )

        result[strategy] = {
            "duplicate_chunk_hashes": duplicates,
            "import_graph_summary": str(import_checks_dir / f"import_graph_{strategy}.json"),
            "line_counts": line_counts,
            "payload_dir": str(payload_dir),
            "strategy_counts": strategy_counts,
            "unique_chunk_hash_count": line_counts.get("chunk_records", 0)
            - sum(max(0, len(group["chunk_ids"]) - 1) for group in duplicates),
        }

    result["_totals"] = {"supabase_source_chunks": supabase_total}
    if enforce_baseline_counts and supabase_total != 7352:
        add_issue(
            issues,
            "baseline_counts",
            "total Supabase source_chunks mismatch",
            expected=7352,
            actual=supabase_total,
        )
    return result


def validate_hit_filters(
    *,
    hits: list[dict[str, Any]],
    source: str,
    strategy: str,
    relation: str,
    issues: list[dict[str, Any]],
) -> None:
    for hit in hits:
        if hit.get("source_id") != source:
            add_issue(issues, relation, "retrieval hit source mismatch", expected=source, actual=hit.get("source_id"))
        if hit.get("chunk_strategy_id") != strategy:
            add_issue(
                issues,
                relation,
                "retrieval hit strategy mismatch",
                expected=strategy,
                actual=hit.get("chunk_strategy_id"),
            )
        if hit.get("domain") not in {None, "TUVI"}:
            add_issue(issues, relation, "retrieval hit domain mismatch", expected="TUVI", actual=hit.get("domain"))
        if strategy == PARENT_CHILD_STRATEGY and hit.get("chunk_type") != "child":
            add_issue(issues, relation, "parent-child retrieval hit is not child-only", chunk_id=hit.get("chunk_id"))


def audit_embedding_artifact_file(
    *,
    path: Path,
    source: str,
    strategy: str,
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    if not path.exists():
        add_issue(issues, "offline_embedding", "missing offline embedding JSONL", path=str(path))
        return {"line_count": 0, "chunk_type_counts": {}}
    chunk_type_counts: Counter[str] = Counter()
    line_count = 0
    try:
        for record in iter_jsonl(path):
            line_count += 1
            chunk_type_counts[str(record.get("chunk_type"))] += 1
            if record.get("source_id") != source:
                add_issue(
                    issues,
                    "offline_embedding",
                    "embedding artifact source mismatch",
                    path=str(path),
                    expected=source,
                    actual=record.get("source_id"),
                )
            if record.get("chunk_strategy_id") != strategy:
                add_issue(
                    issues,
                    "offline_embedding",
                    "embedding artifact strategy mismatch",
                    path=str(path),
                    expected=strategy,
                    actual=record.get("chunk_strategy_id"),
                )
            if record.get("embedding_slot") != "bge_m3":
                add_issue(
                    issues,
                    "offline_embedding",
                    "embedding artifact slot mismatch",
                    path=str(path),
                    expected="bge_m3",
                    actual=record.get("embedding_slot"),
                )
            embedding = record.get("embedding")
            if not isinstance(embedding, list) or len(embedding) != 1024:
                add_issue(
                    issues,
                    "offline_embedding",
                    "embedding artifact dimension mismatch",
                    path=str(path),
                    chunk_id=record.get("chunk_id"),
                    expected=1024,
                    actual=len(embedding) if isinstance(embedding, list) else None,
                )
            if strategy == PARENT_CHILD_STRATEGY and record.get("chunk_type") == "parent":
                add_issue(
                    issues,
                    "offline_embedding",
                    "parent-child embedding artifact includes parent chunks",
                    path=str(path),
                    chunk_id=record.get("chunk_id"),
                )
    except (OSError, ValueError) as exc:
        add_issue(issues, "offline_embedding", "cannot validate embedding artifact", path=str(path), error=str(exc))
    return {"line_count": line_count, "chunk_type_counts": dict(sorted(chunk_type_counts.items()))}


def audit_embeddings_and_retrieval(
    *,
    reports_dir: Path,
    embeddings_dir: Path,
    import_checks_dir: Path,
    sources: list[str],
    strategies: list[str],
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for strategy in strategies:
        strategy_result: dict[str, Any] = {}
        for source in sources:
            pair_key = f"{source}:{strategy}"
            embed_summary_path = reports_dir / f"embed_{source}_{strategy}.json"
            retrieval_path = reports_dir / f"retrieval_{source}_{strategy}.json"
            offline_summary_path = reports_dir / "offline_embedding" / f"embed_{source}_{strategy}.json"
            offline_retrieval_path = reports_dir / "offline_embedding" / f"retrieval_{source}_{strategy}.json"
            offline_artifact_path = embeddings_dir / strategy / f"{source}_{strategy}_embeddings.jsonl"
            import_embedding_path = import_checks_dir / f"import_embedding_{source}_{strategy}.json"

            embed_summary = safe_read_json(embed_summary_path, issues, "live_embedding")
            retrieval_summary = safe_read_json(retrieval_path, issues, "live_retrieval")
            offline_summary = safe_read_json(offline_summary_path, issues, "offline_embedding_summary")
            offline_retrieval = safe_read_json(offline_retrieval_path, issues, "offline_retrieval")
            import_embedding = safe_read_json(import_embedding_path, issues, "import_embedding")
            artifact_stats = audit_embedding_artifact_file(
                path=offline_artifact_path,
                source=source,
                strategy=strategy,
                issues=issues,
            )

            selected_chunks = None
            if embed_summary:
                selected_chunks = embed_summary.get("selected_chunks")
                if embed_summary.get("completed") is not True:
                    add_issue(issues, "live_embedding", "live embedding summary is not complete", pair=pair_key)
                for key, expected in {
                    "embedding_slot": "bge_m3",
                    "embedding_backend": "local",
                    "expected_dim": 1024,
                    "vector_index_name": "chunkVectorBgeM3",
                }.items():
                    if embed_summary.get(key) != expected:
                        add_issue(
                            issues,
                            "live_embedding",
                            "live embedding summary field mismatch",
                            pair=pair_key,
                            key=key,
                            expected=expected,
                            actual=embed_summary.get(key),
                        )
                if strategy == PARENT_CHILD_STRATEGY:
                    if int(embed_summary.get("parent_skipped_count") or 0) <= 0:
                        add_issue(issues, "live_embedding", "parent-child live embedding skipped no parents", pair=pair_key)
                    if "parent" in (embed_summary.get("embedded_chunk_type_counts") or {}):
                        add_issue(issues, "live_embedding", "parent-child live embedding wrote parent chunks", pair=pair_key)

            if retrieval_summary:
                diagnostics = retrieval_summary.get("diagnostics") or {}
                if retrieval_summary.get("embedding_slot") != "bge_m3" or diagnostics.get("embedding_slot") != "bge_m3":
                    add_issue(issues, "live_retrieval", "retrieval summary slot mismatch", pair=pair_key)
                if int(diagnostics.get("dense_hit_count") or 0) <= 0:
                    add_issue(issues, "live_retrieval", "dense retrieval produced no hits", pair=pair_key)
                if int(diagnostics.get("sparse_hit_count") or 0) <= 0:
                    add_issue(issues, "live_retrieval", "sparse retrieval produced no hits", pair=pair_key)
                validate_hit_filters(
                    hits=retrieval_summary.get("dense_hits") or [],
                    source=source,
                    strategy=strategy,
                    relation="live_retrieval",
                    issues=issues,
                )
                validate_hit_filters(
                    hits=retrieval_summary.get("sparse_hits") or [],
                    source=source,
                    strategy=strategy,
                    relation="live_retrieval",
                    issues=issues,
                )
                parent_expansion = diagnostics.get("parent_expansion") or {}
                if strategy == PARENT_CHILD_STRATEGY:
                    if float(parent_expansion.get("parent_expansion_hit_rate") or 0.0) < 1.0:
                        add_issue(
                            issues,
                            "live_retrieval",
                            "parent expansion hit rate is below 1.0",
                            pair=pair_key,
                            actual=parent_expansion.get("parent_expansion_hit_rate"),
                        )
                    if not retrieval_summary.get("parent_expansion_records"):
                        add_issue(issues, "live_retrieval", "parent expansion returned no parent records", pair=pair_key)

            if offline_summary:
                if offline_summary.get("completed") is not True:
                    add_issue(issues, "offline_embedding_summary", "offline embedding summary is not complete", pair=pair_key)
                if offline_summary.get("embedding_slot") != "bge_m3":
                    add_issue(issues, "offline_embedding_summary", "offline embedding slot mismatch", pair=pair_key)
                if offline_summary.get("update_count") != artifact_stats["line_count"]:
                    add_issue(
                        issues,
                        "offline_embedding_summary",
                        "offline embedding update count mismatch",
                        pair=pair_key,
                        expected=artifact_stats["line_count"],
                        actual=offline_summary.get("update_count"),
                    )
            if selected_chunks is not None and artifact_stats["line_count"] != selected_chunks:
                add_issue(
                    issues,
                    "offline_embedding",
                    "offline embedding artifact count does not match live selected chunk count",
                    pair=pair_key,
                    expected=selected_chunks,
                    actual=artifact_stats["line_count"],
                )
            if offline_retrieval:
                diagnostics = offline_retrieval.get("diagnostics") or {}
                if diagnostics.get("mode") != "offline_artifact":
                    add_issue(issues, "offline_retrieval", "offline retrieval mode mismatch", pair=pair_key)
                if int(diagnostics.get("dense_hit_count") or 0) <= 0:
                    add_issue(issues, "offline_retrieval", "offline dense smoke produced no positive hits", pair=pair_key)
            if import_embedding:
                if import_embedding.get("dry_run") is not True:
                    add_issue(issues, "import_embedding", "embedding import check was not a dry-run", pair=pair_key)
                if import_embedding.get("embedding_slot") != "bge_m3":
                    add_issue(issues, "import_embedding", "embedding import slot mismatch", pair=pair_key)
                if import_embedding.get("update_count") != artifact_stats["line_count"]:
                    add_issue(
                        issues,
                        "import_embedding",
                        "embedding import update count mismatch",
                        pair=pair_key,
                        expected=artifact_stats["line_count"],
                        actual=import_embedding.get("update_count"),
                    )

            strategy_result[source] = {
                "artifact": str(offline_artifact_path),
                "artifact_stats": artifact_stats,
                "import_embedding_summary": str(import_embedding_path),
                "live_embedding_summary": str(embed_summary_path),
                "live_retrieval_summary": str(retrieval_path),
                "offline_embedding_summary": str(offline_summary_path),
                "offline_retrieval_summary": str(offline_retrieval_path),
            }
        result[strategy] = strategy_result
    return result


def build_audit(args: argparse.Namespace) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    sources = list(args.sources)
    strategies = list(args.strategies)
    enforce_baseline_counts = not args.skip_baseline_counts and sources == DEFAULT_SOURCES and strategies == DEFAULT_STRATEGIES

    chunk_evidence = audit_chunks(
        chunks_dir=args.chunks_dir,
        reports_dir=args.reports_dir,
        regen_chunks_dir=args.regen_chunks_dir,
        sources=sources,
        strategies=strategies,
        issues=issues,
        warnings=warnings,
    )
    entities_and_reviews = audit_entities_and_reviews(
        entities_dir=args.entities_dir,
        reports_dir=args.reports_dir,
        strategies=strategies,
        issues=issues,
    )
    payloads_and_graph = audit_payloads_and_graph(
        payloads_dir=args.payloads_dir,
        reports_dir=args.reports_dir,
        import_checks_dir=args.import_checks_dir,
        strategies=strategies,
        enforce_baseline_counts=enforce_baseline_counts,
        issues=issues,
        warnings=warnings,
    )
    embeddings_and_retrieval = audit_embeddings_and_retrieval(
        reports_dir=args.reports_dir,
        embeddings_dir=args.embeddings_dir,
        import_checks_dir=args.import_checks_dir,
        sources=sources,
        strategies=strategies,
        issues=issues,
    )

    return {
        "branch": "gemini_call",
        "chunk_evidence": chunk_evidence,
        "completed": not issues,
        "embedding_slot": "bge_m3",
        "embeddings_and_retrieval": embeddings_and_retrieval,
        "enforced_baseline_counts": enforce_baseline_counts,
        "entities_and_reviews": entities_and_reviews,
        "generated_at": utc_now(),
        "issues": issues,
        "payloads_and_graph": payloads_and_graph,
        "sources": sources,
        "strategies": strategies,
        "warnings": warnings,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit W3-INGEST-07 acceptance artifacts.")
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    parser.add_argument("--chunks-dir", type=Path, default=DEFAULT_CHUNKS_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--entities-dir", type=Path, default=DEFAULT_ENTITIES_DIR)
    parser.add_argument("--payloads-dir", type=Path, default=DEFAULT_PAYLOADS_DIR)
    parser.add_argument("--embeddings-dir", type=Path, default=DEFAULT_EMBEDDINGS_DIR)
    parser.add_argument("--import-checks-dir", type=Path, default=DEFAULT_REPORTS_DIR / "import_checks")
    parser.add_argument("--regen-chunks-dir", type=Path, default=None)
    parser.add_argument("--sources", nargs="+", default=DEFAULT_SOURCES)
    parser.add_argument("--strategies", nargs="+", default=DEFAULT_STRATEGIES)
    parser.add_argument("--skip-baseline-counts", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORTS_DIR / "w3_ingest_07_acceptance_audit.json")
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> dict[str, Any]:
    args = parse_args(argv)
    audit = build_audit(args)
    if args.output:
        write_json(args.output, audit)
    return audit


def cli(argv: list[str] | None = None) -> int:
    audit = run(argv)
    print(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if audit["completed"] else 2


if __name__ == "__main__":
    raise SystemExit(cli())
