from __future__ import annotations

from typing import Any

from app.rag.chart_facts import build_chart_fact_context_block
from app.rag.config import ExperimentConfig
from app.rag.state import RAGState


DEFAULT_MAX_CONTEXT_CHARS = 8_000
DEFAULT_MAX_CHUNKS = 8
EXCERPT_CHARS = 700


def assemble_context(state: RAGState, config: ExperimentConfig) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    candidates = select_candidate_pool(state)
    ordered = order_candidates(candidates, strategy=config.context_assembly_strategy)
    required_roles = required_evidence_roles_from_plan(state)
    role_aware_enabled = bool(required_roles)
    if role_aware_enabled:
        selected = select_role_aware_with_budget(
            ordered,
            required_roles=required_roles,
            max_chars=DEFAULT_MAX_CONTEXT_CHARS,
            max_chunks=DEFAULT_MAX_CHUNKS,
        )
    else:
        selected = select_with_budget(ordered, max_chars=DEFAULT_MAX_CONTEXT_CHARS, max_chunks=DEFAULT_MAX_CHUNKS)

    context_chunks: list[dict[str, Any]] = []
    blocks: list[str] = []
    chart_fact_block = build_chart_fact_context_block(state.get("chart_facts") or {})
    if chart_fact_block.strip():
        chart_chunk = make_chart_context_chunk(state, config=config)
        context_chunks.append(chart_chunk)
    for index, candidate in enumerate(selected, start=1):
        chunk = make_context_chunk(candidate, index=index, config=config)
        context_chunks.append(chunk)
        blocks.append(format_context_block(chunk))

    chart_summary = summarize_chart_context(state.get("chart_data") or {})
    final_context = "\n\n".join([part for part in [chart_summary, chart_fact_block, *blocks] if part.strip()])
    role_summary = build_context_role_summary(
        context_chunks,
        required_roles=required_roles,
        role_aware_enabled=role_aware_enabled,
    )
    summary = {
        "candidate_pool_count": len(candidates),
        "context_assembly_strategy": config.context_assembly_strategy,
        "chart_context_priority": "before_corpus_chunks",
        "has_chart_summary": bool(chart_summary.strip()),
        "has_chart_facts": bool(chart_fact_block.strip()),
        "chart_fact_house_count": len((state.get("chart_facts") or {}).get("house_facts") or []),
        "chart_fact_target_houses": (state.get("chart_facts") or {}).get("target_houses") or [],
        "chart_fact_target_stars": (state.get("chart_facts") or {}).get("target_stars") or [],
        "max_chunks": DEFAULT_MAX_CHUNKS,
        "max_context_chars": DEFAULT_MAX_CONTEXT_CHARS,
        "selected_count": len(selected),
        "selected_chunk_ids": [chunk.get("chunk_id") for chunk in context_chunks if chunk.get("source_id") != "CHART"],
        "total_context_chars": len(final_context),
    }
    summary.update(role_summary)
    return final_context, context_chunks, summary


def select_candidate_pool(state: RAGState) -> list[dict[str, Any]]:
    for key in ("ranked_candidates", "graded_candidates", "reranked_candidates", "fused_candidates"):
        candidates = [dict(candidate) for candidate in state.get(key) or []]
        if candidates:
            return backfill_required_roles(candidates, state)
    return []


def backfill_required_roles(candidates: list[dict[str, Any]], state: RAGState) -> list[dict[str, Any]]:
    """Preserve at least one candidate per required role after rerank/grade pruning.

    Reranking and grading may cap/drop lower-scored role-specific candidates. For
    one-hop/two-hop questions this causes role-aware context assembly to miss
    required evidence even though the raw fused pool had it. We append the best
    missing-role candidates from `fused_candidates` as a controlled backfill; the
    context selector still enforces chunk/char budgets.
    """
    required_roles = required_evidence_roles_from_plan(state)
    if not required_roles:
        return candidates
    covered = {role for candidate in candidates for role in candidate_roles(candidate)}
    missing = [role for role in required_roles if role not in covered]
    if not missing:
        return candidates
    output = list(candidates)
    seen = {candidate_identity(candidate) for candidate in output}
    fused = order_candidates([dict(candidate) for candidate in state.get("fused_candidates") or []], strategy="balanced")
    for role in missing:
        for candidate in fused:
            key = candidate_identity(candidate)
            if key in seen or role not in candidate_roles(candidate):
                continue
            backfilled = dict(candidate)
            backfilled["role_backfilled"] = True
            output.append(backfilled)
            seen.add(key)
            break
    return output


def order_candidates(candidates: list[dict[str, Any]], *, strategy: str) -> list[dict[str, Any]]:
    if strategy == "graph_first":
        return sorted(candidates, key=lambda item: (path_priority(item, "graph"), score_value(item), -rank_value(item)), reverse=True)
    if strategy == "dense_first":
        return sorted(candidates, key=lambda item: (path_priority(item, "dense"), score_value(item), -rank_value(item)), reverse=True)
    if strategy == "compact":
        return sorted(candidates, key=lambda item: (score_value(item), -len(str(item.get("text") or "")), -rank_value(item)), reverse=True)
    # balanced keeps ranking stable but uses rerank/grade relevance before the
    # weaker multi-path bonus. Otherwise a mediocre graph+sparse hit can outrank
    # a high-quality exact-definition hit found by one path.
    return sorted(candidates, key=lambda item: (score_value(item), len(item.get("retrieval_paths") or []), -rank_value(item)), reverse=True)


def select_with_budget(candidates: list[dict[str, Any]], *, max_chars: int, max_chunks: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    used_chars = 0
    for candidate in candidates:
        accepted, used_chars = try_add_candidate_with_budget(
            selected,
            candidate,
            used_chars=used_chars,
            max_chars=max_chars,
            max_chunks=max_chunks,
        )
        if not accepted:
            continue
        if len(selected) >= max_chunks:
            break
    return selected


def select_role_aware_with_budget(
    candidates: list[dict[str, Any]],
    *,
    required_roles: list[str],
    max_chars: int,
    max_chunks: int,
) -> list[dict[str, Any]]:
    """Select context chunks by covering required evidence roles, then fill by rank.

    The input `candidates` is already ordered by the configured context strategy.
    Role-aware selection treats role coverage as a soft constraint: it attempts to
    select at least one candidate for each required role when budget allows, then
    fills remaining slots using the original global ordering. Final output is
    sorted by original ordering to preserve relevance/citation stability.
    """
    selected: list[dict[str, Any]] = []
    selected_keys: set[str] = set()
    used_chars = 0

    for role in required_roles:
        if len(selected) >= max_chunks:
            break
        for candidate in candidates:
            key = candidate_identity(candidate)
            if key in selected_keys or role not in candidate_roles(candidate):
                continue
            accepted, used_chars = try_add_candidate_with_budget(
                selected,
                candidate,
                used_chars=used_chars,
                max_chars=max_chars,
                max_chunks=max_chunks,
            )
            if accepted:
                selected_keys.add(key)
                break

    for candidate in candidates:
        if len(selected) >= max_chunks:
            break
        key = candidate_identity(candidate)
        if key in selected_keys:
            continue
        accepted, used_chars = try_add_candidate_with_budget(
            selected,
            candidate,
            used_chars=used_chars,
            max_chars=max_chars,
            max_chunks=max_chunks,
        )
        if accepted:
            selected_keys.add(key)

    order = {candidate_identity(candidate): index for index, candidate in enumerate(candidates)}
    return sorted(selected, key=lambda item: order.get(candidate_identity(item), 10_000))


def try_add_candidate_with_budget(
    selected: list[dict[str, Any]],
    candidate: dict[str, Any],
    *,
    used_chars: int,
    max_chars: int,
    max_chunks: int,
) -> tuple[bool, int]:
    if len(selected) >= max_chunks:
        return False, used_chars
    text = candidate_text(candidate)
    if not text:
        return False, used_chars
    projected = used_chars + min(len(text), EXCERPT_CHARS)
    if selected and projected > max_chars:
        return False, used_chars
    selected.append(candidate)
    return True, projected


def make_context_chunk(candidate: dict[str, Any], *, index: int, config: ExperimentConfig) -> dict[str, Any]:
    excerpt = candidate_text(candidate)[:EXCERPT_CHARS].strip()
    marker = f"S{index}"
    return {
        "citation_marker": marker,
        "chunk_id": candidate.get("chunk_id"),
        "chunk_hash": candidate.get("chunk_hash"),
        "chunk_strategy_id": candidate.get("chunk_strategy_id") or config.chunk_strategy_id,
        "chunk_type": candidate.get("chunk_type"),
        "domain": candidate.get("domain") or config.domain,
        "excerpt": excerpt,
        "fusion_score": candidate.get("fusion_score"),
        "grade_score": candidate.get("grade_score"),
        "evidence_role": candidate.get("evidence_role"),
        "evidence_roles": list(candidate.get("evidence_roles") or []),
        "retrieval_intent": candidate.get("retrieval_intent"),
        "matched_entities": list(candidate.get("matched_entities") or []),
        "parent_id": candidate.get("parent_id"),
        "provenance": dict(candidate.get("provenance") or {}),
        "rank": candidate.get("rank"),
        "rerank_score": candidate.get("rerank_score"),
        "retrieval_paths": candidate_retrieval_paths(candidate),
        "score": candidate.get("score"),
        "source_id": candidate.get("source_id"),
        "source_name": candidate.get("source_name"),
        "source_page": candidate.get("source_page"),
        "title": candidate.get("title"),
    }


def make_chart_context_chunk(state: RAGState, *, config: ExperimentConfig) -> dict[str, Any]:
    chart_facts = state.get("chart_facts") or {}
    return {
        "citation_marker": "CHART",
        "chunk_id": "chart_facts",
        "chunk_hash": None,
        "chunk_strategy_id": config.chunk_strategy_id,
        "chunk_type": "chart_facts",
        "domain": config.domain,
        "excerpt": build_chart_fact_context_block(chart_facts),
        "evidence_role": "chart_facts",
        "evidence_roles": ["chart_facts", *required_evidence_roles_from_plan(state)],
        "provenance": {"source_id": "CHART", "source_name": "Dữ kiện lá số", "source_type": "chart_facts"},
        "retrieval_intent": "chart_facts",
        "retrieval_paths": ["chart"],
        "score": 1.0,
        "source_id": "CHART",
        "source_name": "Dữ kiện lá số",
        "source_page": None,
        "title": "Dữ kiện lá số đã trích xuất",
    }


def format_context_block(chunk: dict[str, Any]) -> str:
    source_label = chunk.get("source_name") or chunk.get("source_id") or "Không rõ nguồn"
    page = chunk.get("source_page")
    page_label = f", trang {page}" if page not in (None, "") else ""
    title = f" - {chunk.get('title')}" if chunk.get("title") else ""
    role_line = format_role_metadata_line(chunk)
    metadata_lines = [
        f"chunk_id: {chunk.get('chunk_id')} | strategy: {chunk.get('chunk_strategy_id')}",
    ]
    if role_line:
        metadata_lines.append(role_line)
    return (
        f"[{chunk['citation_marker']}] {source_label}{page_label}{title}\n"
        f"{'\n'.join(metadata_lines)}\n"
        f"{chunk.get('excerpt') or ''}"
    )


def format_role_metadata_line(chunk: dict[str, Any]) -> str:
    roles = unique_strings([*(chunk.get("evidence_roles") or []), chunk.get("evidence_role")])
    intent = str(chunk.get("retrieval_intent") or "").strip()
    parts: list[str] = []
    if roles:
        parts.append(f"evidence_roles: {', '.join(roles)}")
    if intent:
        parts.append(f"retrieval_intent: {intent}")
    return " | ".join(parts)


def required_evidence_roles_from_plan(state: RAGState) -> list[str]:
    plan = state.get("retrieval_plan") or {}
    roles = plan.get("required_evidence_roles") if isinstance(plan, dict) else []
    return unique_strings(list(roles or []))


def candidate_roles(candidate: dict[str, Any]) -> list[str]:
    return unique_strings([*(candidate.get("evidence_roles") or []), candidate.get("evidence_role")])


def candidate_identity(candidate: dict[str, Any]) -> str:
    for field in ("chunk_hash", "chunk_id"):
        value = str(candidate.get(field) or "").strip()
        if value:
            return f"{field}:{value}"
    return f"object:{id(candidate)}"


def build_context_role_summary(
    context_chunks: list[dict[str, Any]],
    *,
    required_roles: list[str],
    role_aware_enabled: bool,
) -> dict[str, Any]:
    selected_by_role: dict[str, list[str]] = {}
    selected_roles: list[str] = []
    for chunk in context_chunks:
        chunk_id = str(chunk.get("chunk_id") or chunk.get("chunk_hash") or "").strip()
        for role in candidate_roles(chunk):
            if role not in selected_roles:
                selected_roles.append(role)
            if not chunk_id:
                continue
            selected_by_role.setdefault(role, [])
            if chunk_id not in selected_by_role[role]:
                selected_by_role[role].append(chunk_id)

    missing_roles = [role for role in required_roles if role not in selected_roles]
    required_count = len(required_roles)
    covered_count = required_count - len(missing_roles)
    coverage_rate = round(covered_count / required_count, 4) if required_count else 1.0
    role_selected_chunk_ids = set(
        chunk_id
        for role in required_roles
        for chunk_id in selected_by_role.get(role, [])
    )
    fallback_fill_count = sum(
        1
        for chunk in context_chunks
        if str(chunk.get("chunk_id") or chunk.get("chunk_hash") or "").strip() not in role_selected_chunk_ids
    )
    return {
        "role_aware_enabled": role_aware_enabled,
        "required_evidence_roles": required_roles,
        "selected_evidence_roles": selected_roles,
        "missing_evidence_roles": missing_roles,
        "role_coverage_rate": coverage_rate,
        "selected_chunks_by_role": selected_by_role,
        "role_selection": {
            "required_role_count": required_count,
            "covered_role_count": covered_count,
            "fallback_fill_count": fallback_fill_count,
        },
    }


def summarize_chart_context(chart_data: dict[str, Any]) -> str:
    if not isinstance(chart_data, dict) or not chart_data:
        return ""
    metadata = chart_data.get("metadata") if isinstance(chart_data.get("metadata"), dict) else {}
    fields = {
        "chart_type": chart_data.get("chart_type") or chart_data.get("chart_system") or "TUVI",
        "label": metadata.get("label") or chart_data.get("label"),
        "gender": metadata.get("gender") or chart_data.get("gender"),
        "birth_date": metadata.get("birth_date") or chart_data.get("birth_date"),
        "birth_time": metadata.get("birth_time") or chart_data.get("birth_time"),
    }
    compact = {key: value for key, value in fields.items() if value not in (None, "", [])}
    if not compact:
        return ""
    lines = ["[CHART] Thông tin lá số Tử Vi", *[f"{key}: {value}" for key, value in compact.items()]]
    return "\n".join(lines)


def candidate_text(candidate: dict[str, Any]) -> str:
    return str(candidate.get("text") or candidate.get("excerpt") or candidate.get("text_preview") or "").strip()


def score_value(candidate: dict[str, Any]) -> float:
    for field in ("rerank_score", "grade_score", "fusion_score", "score"):
        value = candidate.get(field)
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
    return 0.0


def rank_value(candidate: dict[str, Any]) -> int:
    try:
        return int(candidate.get("rank") or 10_000)
    except (TypeError, ValueError):
        return 10_000


def path_priority(candidate: dict[str, Any], path: str) -> int:
    paths = candidate_retrieval_paths(candidate)
    return 1 if path in paths else 0


def candidate_retrieval_paths(candidate: dict[str, Any]) -> list[str]:
    paths = [str(path) for path in candidate.get("retrieval_paths") or [] if str(path).strip()]
    retrieval_path = candidate.get("retrieval_path")
    if retrieval_path and str(retrieval_path) not in paths:
        paths.append(str(retrieval_path))
    return paths


def unique_strings(values: list[Any]) -> list[str]:
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in result:
            result.append(text)
    return result