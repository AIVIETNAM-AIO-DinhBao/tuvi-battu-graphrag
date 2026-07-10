from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any, Protocol

from app.rag.config import ExperimentConfig
from app.rag.retrieval import RetrievalCandidate, retrieval_query_text
from app.rag.state import RAGState


RRF_K = 60
PATH_ORDER = ("graph", "dense", "sparse")
DEFAULT_PATH_WEIGHTS = {"graph": 1.0, "dense": 1.0, "sparse": 1.0}
GRAPH_FIRST_PRIORITY = {"graph": 3.0, "dense": 2.0, "sparse": 1.0}
TOKEN_RE = re.compile(r"\w+", re.UNICODE)


class CandidateReranker(Protocol):
    def rerank(
        self,
        query: str,
        candidates: list[dict[str, Any]],
        *,
        config: ExperimentConfig,
        state: RAGState,
    ) -> list[dict[str, Any]]:
        ...


class LexicalOverlapReranker:
    """Deterministic local reranker used as a safe wrapper fallback.

    It is intentionally lightweight for W4-RAG-04: production keeps reranking
    disabled by default, while tests and later model-backed rerankers can inject
    a stronger implementation through the graph/node factory.
    """

    def rerank(
        self,
        query: str,
        candidates: list[dict[str, Any]],
        *,
        config: ExperimentConfig,
        state: RAGState,
    ) -> list[dict[str, Any]]:
        query_terms = tokenize(query)
        scored: list[dict[str, Any]] = []
        for candidate in candidates:
            item = dict(candidate)
            text_terms = tokenize(str(item.get("text") or item.get("text_preview") or ""))
            overlap = lexical_overlap_score(query_terms, text_terms)
            fused_score = coerce_float(item.get("fusion_score", item.get("score")))
            rerank_score = (0.65 * overlap) + (0.35 * fused_score)
            item["rerank_score"] = round(rerank_score, 6)
            item["rerank_features"] = {
                "query_overlap": round(overlap, 6),
                "fusion_score": round(fused_score, 6),
            }
            scored.append(item)
        return sorted(
            scored,
            key=lambda item: (
                coerce_float(item.get("rerank_score")),
                coerce_float(item.get("fusion_score", item.get("score"))),
                -int(item.get("rank") or 0),
            ),
            reverse=True,
        )


def count_candidates_by_path(state: RAGState) -> dict[str, int]:
    return {
        "graph": len(state.get("graph_candidates") or []),
        "dense": len(state.get("dense_candidates") or []),
        "sparse": len(state.get("sparse_candidates") or []),
    }


def collect_candidates_by_path(state: RAGState) -> dict[str, list[dict[str, Any]]]:
    return {
        "graph": [dict(candidate) for candidate in state.get("graph_candidates") or []],
        "dense": [dict(candidate) for candidate in state.get("dense_candidates") or []],
        "sparse": [dict(candidate) for candidate in state.get("sparse_candidates") or []],
    }


def fuse_retrieval_candidates(state: RAGState, config: ExperimentConfig) -> list[dict[str, Any]]:
    candidates_by_path = collect_candidates_by_path(state)
    if config.fusion_method == "rrf":
        return fuse_rrf(candidates_by_path)
    if config.fusion_method == "weighted_sum":
        return fuse_weighted_sum(candidates_by_path)
    if config.fusion_method == "graph_first":
        return fuse_graph_first(candidates_by_path)
    raise ValueError(f"Unsupported fusion method: {config.fusion_method}")


def fuse_rrf(candidates_by_path: dict[str, list[dict[str, Any]]], *, rrf_k: int = RRF_K) -> list[dict[str, Any]]:
    fused: dict[str, dict[str, Any]] = {}
    for path in PATH_ORDER:
        for fallback_rank, candidate in enumerate(candidates_by_path.get(path, []), start=1):
            rank = int(candidate.get("rank") or fallback_rank)
            contribution = 1.0 / (rrf_k + rank)
            add_fusion_contribution(
                fused,
                candidate,
                path=path,
                contribution=contribution,
                rank=rank,
                normalized_score=None,
            )
    return rank_fused_candidates(fused.values(), method="rrf")


def fuse_weighted_sum(
    candidates_by_path: dict[str, list[dict[str, Any]]],
    *,
    path_weights: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    weights = path_weights or DEFAULT_PATH_WEIGHTS
    max_score_by_path = {
        path: max([coerce_float(candidate.get("score")) for candidate in candidates] or [0.0])
        for path, candidates in candidates_by_path.items()
    }
    fused: dict[str, dict[str, Any]] = {}
    for path in PATH_ORDER:
        max_score = max_score_by_path.get(path, 0.0)
        for fallback_rank, candidate in enumerate(candidates_by_path.get(path, []), start=1):
            raw_score = coerce_float(candidate.get("score"))
            normalized_score = raw_score / max_score if max_score > 0 else 0.0
            contribution = normalized_score * weights.get(path, 1.0)
            add_fusion_contribution(
                fused,
                candidate,
                path=path,
                contribution=contribution,
                rank=int(candidate.get("rank") or fallback_rank),
                normalized_score=normalized_score,
            )
    return rank_fused_candidates(fused.values(), method="weighted_sum")


def fuse_graph_first(candidates_by_path: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    fused: dict[str, dict[str, Any]] = {}
    for path in PATH_ORDER:
        for fallback_rank, candidate in enumerate(candidates_by_path.get(path, []), start=1):
            rank = int(candidate.get("rank") or fallback_rank)
            contribution = 1.0 / (RRF_K + rank)
            record = add_fusion_contribution(
                fused,
                candidate,
                path=path,
                contribution=contribution,
                rank=rank,
                normalized_score=None,
            )
            record["graph_first_priority"] = max(
                coerce_float(record.get("graph_first_priority")),
                GRAPH_FIRST_PRIORITY.get(path, 0.0),
            )
            record["fusion_score"] = coerce_float(record.get("graph_first_priority")) + coerce_float(
                record.get("path_contribution_score")
            )
            record["score"] = round(coerce_float(record["fusion_score"]), 6)
    return rank_fused_candidates(fused.values(), method="graph_first")


def add_fusion_contribution(
    fused: dict[str, dict[str, Any]],
    candidate: dict[str, Any],
    *,
    path: str,
    contribution: float,
    rank: int,
    normalized_score: float | None,
) -> dict[str, Any]:
    identity = candidate_identity(candidate)
    record = fused.get(identity)
    if record is None:
        record = make_fused_record(candidate, identity=identity)
        fused[identity] = record
    merge_candidate_metadata(record, candidate)

    score_breakdown = dict(record.get("score_breakdown") or {})
    current_path_breakdown = score_breakdown.get(path)
    raw_score = coerce_float(candidate.get("score"))
    path_payload = {
        "rank": rank,
        "score": round(raw_score, 6),
        "contribution": round(contribution, 6),
    }
    if normalized_score is not None:
        path_payload["normalized_score"] = round(normalized_score, 6)

    if current_path_breakdown is None or contribution > coerce_float(current_path_breakdown.get("contribution")):
        score_breakdown[path] = path_payload
    record["score_breakdown"] = score_breakdown

    retrieval_paths = list(record.get("retrieval_paths") or [])
    if path not in retrieval_paths:
        retrieval_paths.append(path)
    record["retrieval_paths"] = [path_name for path_name in PATH_ORDER if path_name in retrieval_paths]

    record["path_contribution_score"] = round(
        coerce_float(record.get("path_contribution_score")) + contribution,
        6,
    )
    if "graph_first_priority" not in record:
        record["fusion_score"] = record["path_contribution_score"]
        record["score"] = record["fusion_score"]

    if raw_score > coerce_float(record.get("best_retrieval_score")):
        record["best_retrieval_score"] = raw_score
        record["best_retrieval_path"] = path
    return record


def make_fused_record(candidate: dict[str, Any], *, identity: str) -> dict[str, Any]:
    record = dict(candidate)
    record["candidate_key"] = identity
    record["fusion_score"] = 0.0
    record["path_contribution_score"] = 0.0
    record["best_retrieval_score"] = coerce_float(candidate.get("score"))
    record["best_retrieval_path"] = candidate.get("retrieval_path")
    record["retrieval_paths"] = []
    record["score_breakdown"] = {}
    record["matched_entities"] = unique_strings(candidate.get("matched_entities") or [])
    record["relation_types"] = unique_strings(candidate.get("relation_types") or [])
    record["provenance"] = dict(candidate.get("provenance") or {})
    return record


def merge_candidate_metadata(record: dict[str, Any], candidate: dict[str, Any]) -> None:
    record["matched_entities"] = unique_strings(
        [*(record.get("matched_entities") or []), *(candidate.get("matched_entities") or [])]
    )
    record["relation_types"] = unique_strings(
        [*(record.get("relation_types") or []), *(candidate.get("relation_types") or [])]
    )
    provenance = dict(record.get("provenance") or {})
    provenance.update({key: value for key, value in dict(candidate.get("provenance") or {}).items() if value is not None})
    record["provenance"] = provenance
    for field in (
        "chunk_id",
        "chunk_hash",
        "chunk_type",
        "parent_id",
        "chunk_strategy_id",
        "domain",
        "source_id",
        "source_name",
        "source_page",
        "title",
        "text",
        "text_preview",
    ):
        if not record.get(field) and candidate.get(field) is not None:
            record[field] = candidate.get(field)


def rank_fused_candidates(records: Iterable[dict[str, Any]], *, method: str) -> list[dict[str, Any]]:
    if method == "graph_first":
        key = lambda item: (
            coerce_float(item.get("graph_first_priority")),
            coerce_float(item.get("fusion_score")),
            len(item.get("retrieval_paths") or []),
            -min_breakdown_rank(item),
        )
    else:
        key = lambda item: (
            coerce_float(item.get("fusion_score")),
            len(item.get("retrieval_paths") or []),
            -min_breakdown_rank(item),
        )

    ranked = [dict(record) for record in sorted(records, key=key, reverse=True)]
    for index, candidate in enumerate(ranked, start=1):
        candidate["rank"] = index
        candidate["fusion_rank"] = index
        candidate["fusion_method"] = method
        candidate["fusion_score"] = round(coerce_float(candidate.get("fusion_score")), 6)
        candidate["score"] = candidate["fusion_score"]
    return ranked


def apply_reranking(
    state: RAGState,
    config: ExperimentConfig,
    *,
    candidate_reranker: CandidateReranker | None = None,
) -> list[dict[str, Any]]:
    fused_candidates = [dict(candidate) for candidate in state.get("fused_candidates") or []]
    if not config.reranker_enabled:
        return fused_candidates

    query = retrieval_query_text(state)
    reranker = candidate_reranker or LexicalOverlapReranker()
    reranked = reranker.rerank(query, fused_candidates, config=config, state=state)
    capped = [dict(candidate) for candidate in reranked[: config.reranker_config.top_k]]
    for index, candidate in enumerate(capped, start=1):
        candidate.setdefault("fusion_rank", candidate.get("rank"))
        candidate["rank"] = index
        candidate["rerank_rank"] = index
        candidate["reranked"] = True
        if "rerank_score" not in candidate:
            candidate["rerank_score"] = coerce_float(candidate.get("score"))
    return capped


def apply_document_grading(state: RAGState, config: ExperimentConfig) -> list[dict[str, Any]]:
    candidates = [dict(candidate) for candidate in state.get("reranked_candidates") or []]
    if not config.document_grading_enabled:
        return candidates

    query_terms = tokenize(retrieval_query_text(state))
    graded: list[dict[str, Any]] = []
    for candidate in candidates:
        item = dict(candidate)
        grade = grade_candidate(query_terms, item)
        item["document_grade"] = grade
        item["grade_score"] = grade["score"]
        if grade["accepted"]:
            graded.append(item)

    for index, candidate in enumerate(graded, start=1):
        candidate["rank"] = index
        candidate["graded_rank"] = index
    return graded


def grade_candidate(query_terms: set[str], candidate: dict[str, Any]) -> dict[str, Any]:
    text = str(candidate.get("text") or candidate.get("text_preview") or "")
    if not text.strip():
        return {"accepted": False, "label": "empty", "score": 0.0, "reason": "missing_text"}

    text_terms = tokenize(text)
    overlap = lexical_overlap_score(query_terms, text_terms)
    has_entity_match = bool(candidate.get("matched_entities"))
    has_positive_rank_score = coerce_float(candidate.get("score")) > 0
    grade_score = min(1.0, overlap + (0.2 if has_entity_match else 0.0) + (0.1 if has_positive_rank_score else 0.0))
    label = "relevant" if grade_score >= 0.2 else "weak"
    return {
        "accepted": True,
        "label": label,
        "score": round(grade_score, 6),
        "reason": "deterministic_stub_overlap",
        "query_overlap": round(overlap, 6),
    }


def fusion_trace_summary(candidates: list[dict[str, Any]], *, limit: int = 20) -> list[dict[str, Any]]:
    return [compact_candidate_trace(candidate) for candidate in candidates[:limit]]


def ranking_trace_summary(candidates: list[dict[str, Any]], *, limit: int = 20) -> list[dict[str, Any]]:
    return [
        {
            "rank": candidate.get("rank"),
            "chunk_id": candidate.get("chunk_id"),
            "chunk_hash": candidate.get("chunk_hash"),
            "score": round(coerce_float(candidate.get("score")), 6),
            "fusion_rank": candidate.get("fusion_rank"),
            "rerank_score": candidate.get("rerank_score"),
            "grade_score": candidate.get("grade_score"),
        }
        for candidate in candidates[:limit]
    ]


def compact_candidate_trace(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "rank": candidate.get("rank"),
        "chunk_id": candidate.get("chunk_id"),
        "chunk_hash": candidate.get("chunk_hash"),
        "score": round(coerce_float(candidate.get("score")), 6),
        "retrieval_paths": list(candidate.get("retrieval_paths") or []),
        "score_breakdown": candidate.get("score_breakdown") or {},
    }


def candidate_identity(candidate: dict[str, Any]) -> str:
    for field in ("chunk_hash", "chunk_id"):
        value = candidate.get(field)
        if value:
            return f"{field}:{value}"
    text_key = str(candidate.get("text") or candidate.get("text_preview") or "")[:120]
    return f"anon:{candidate.get('retrieval_path') or 'unknown'}:{candidate.get('rank') or 0}:{text_key}"


def min_breakdown_rank(candidate: dict[str, Any]) -> int:
    ranks = [
        int(payload.get("rank") or 10_000)
        for payload in dict(candidate.get("score_breakdown") or {}).values()
    ]
    return min(ranks or [10_000])


def coerce_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def unique_strings(values: Iterable[Any]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        output.append(text)
    return output


def tokenize(text: str) -> set[str]:
    return {token.casefold() for token in TOKEN_RE.findall(text or "") if len(token) > 1}


def lexical_overlap_score(query_terms: set[str], text_terms: set[str]) -> float:
    if not query_terms or not text_terms:
        return 0.0
    return len(query_terms & text_terms) / len(query_terms)


def as_retrieval_candidates(candidates: list[dict[str, Any]]) -> list[RetrievalCandidate]:
    return [dict(candidate) for candidate in candidates]