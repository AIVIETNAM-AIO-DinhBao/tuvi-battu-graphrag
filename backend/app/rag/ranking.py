from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Protocol

from app.rag.config import DEFAULT_FUSION_PATH_WEIGHTS, ROOT_DIR, ExperimentConfig, RerankerConfig
from app.rag.retrieval import RetrievalCandidate, retrieval_query_text
from app.rag.role_retrieval import candidate_roles, merge_candidate_role_metadata
from app.rag.state import RAGState


RRF_K = 60
PATH_ORDER = ("graph", "dense", "sparse")
GRAPH_FIRST_PRIORITY = {"graph": 3.0, "dense": 2.0, "sparse": 1.0}
TOKEN_RE = re.compile(r"\w+", re.UNICODE)
_RERANKER_BACKEND_CACHE: dict[tuple[str, str | None, int, int, bool], tuple[str, Any]] = {}


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
    """Deterministic test helper; production configs must use a model reranker."""

    def rerank(
        self,
        query: str,
        candidates: list[dict[str, Any]],
        *,
        config: ExperimentConfig,
        state: RAGState,
    ) -> list[dict[str, Any]]:
        query_terms = tokenize(query)
        canonical_entities = canonical_query_entities(state)
        meaning_intent = has_meaning_intent(query)
        scored: list[dict[str, Any]] = []
        for candidate in candidates:
            item = dict(candidate)
            text = str(item.get("text") or item.get("text_preview") or "")
            text_terms = tokenize(text)
            overlap = lexical_overlap_score(query_terms, text_terms)
            entity_exact = entity_exact_score(canonical_entities, text)
            definition_heading = definition_heading_score(canonical_entities, text)
            definition_quality = definition_quality_score(canonical_entities, text) if meaning_intent else 0.0
            meaning_signal = meaning_signal_score(text) if meaning_intent else 0.0
            fused_score = coerce_float(item.get("fusion_score", item.get("score")))
            raw_rerank_score = (
                (0.50 * definition_quality)
                + (0.25 * definition_heading)
                + (0.15 * entity_exact)
                + (0.05 * overlap)
                + (0.03 * meaning_signal)
                + (0.05 * fused_score)
            )
            # Normalize to [0, 1] range to ensure valid confidence scores
            rerank_score = max(0.0, min(1.0, raw_rerank_score))
            item["rerank_score"] = round(rerank_score, 6)
            item["rerank_features"] = {
                "entity_exact": round(entity_exact, 6),
                "definition_heading": round(definition_heading, 6),
                "definition_quality": round(definition_quality, 6),
                "query_overlap": round(overlap, 6),
                "meaning_signal": round(meaning_signal, 6),
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


class CrossEncoderReranker:
    """Lazy model-backed reranker for query/document cross-encoder scoring."""

    def __init__(
        self,
        model_name: str,
        *,
        local_model_path: Path | str | None = None,
        batch_size: int = 16,
        max_length: int = 1024,
        local_files_only: bool = True,
    ) -> None:
        self.model_name = model_name
        self.local_model_path = resolve_local_model_path(local_model_path)
        self.batch_size = batch_size
        self.max_length = max_length
        self.local_files_only = local_files_only
        self._backend: Any | None = None
        self._predict_fn: Any | None = None

    def rerank(
        self,
        query: str,
        candidates: list[dict[str, Any]],
        *,
        config: ExperimentConfig,
        state: RAGState,
    ) -> list[dict[str, Any]]:
        if not candidates:
            return []
        pairs = [(query, candidate_text(candidate)) for candidate in candidates]
        scores = self._predict_scores(pairs)
        scored: list[dict[str, Any]] = []
        for candidate, score in zip(candidates, scores, strict=False):
            item = dict(candidate)
            item["rerank_score"] = round(float(score), 6)
            item["rerank_features"] = {
                "model": self.model_name,
                "score_backend": self._backend_name(),
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

    def _predict_scores(self, pairs: list[tuple[str, str]]) -> list[float]:
        if self._predict_fn is None:
            self._load_backend()
        assert self._predict_fn is not None
        return [float(score) for score in self._predict_fn(pairs)]

    def _backend_name(self) -> str:
        return str(self._backend or "unloaded")

    def _load_backend(self) -> None:
        model_source = self._model_source()
        local_source = str(model_source) if isinstance(model_source, Path) else None
        cache_key = (self.model_name, local_source, self.batch_size, self.max_length, self.local_files_only)
        cached = _RERANKER_BACKEND_CACHE.get(cache_key)
        if cached is not None:
            self._backend, self._predict_fn = cached
            return

        try:
            import torch  # type: ignore
            from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore

            tokenizer = AutoTokenizer.from_pretrained(
                model_source,
                local_files_only=self.local_files_only,
                trust_remote_code=True,
            )
            try:
                model = AutoModelForSequenceClassification.from_pretrained(
                    model_source,
                    local_files_only=self.local_files_only,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True,
                )
            except (ImportError, TypeError):
                model = AutoModelForSequenceClassification.from_pretrained(
                    model_source,
                    local_files_only=self.local_files_only,
                    trust_remote_code=True,
                )
            model.eval()

            def predict_with_transformers(pairs: list[tuple[str, str]]) -> list[float]:
                output: list[float] = []
                with torch.inference_mode():
                    for start in range(0, len(pairs), self.batch_size):
                        batch = pairs[start : start + self.batch_size]
                        encoded = tokenizer(
                            [left for left, _ in batch],
                            [right for _, right in batch],
                            padding=True,
                            truncation=True,
                            max_length=self.max_length,
                            return_tensors="pt",
                        )
                        logits = model(**encoded).logits
                        if logits.ndim == 1 or logits.shape[-1] == 1:
                            batch_scores = logits.reshape(-1)
                        else:
                            batch_scores = logits[:, -1]
                        output.extend(float(score) for score in batch_scores.tolist())
                return output

            self._backend = "transformers.AutoModelForSequenceClassification"
            self._predict_fn = predict_with_transformers
            _RERANKER_BACKEND_CACHE[cache_key] = (self._backend, self._predict_fn)
            return
        except Exception as hf_exc:
            hf_error = hf_exc

        try:
            from FlagEmbedding import FlagReranker  # type: ignore

            reranker = FlagReranker(str(model_source), use_fp16=False)

            def predict_with_flagembedding(pairs: list[tuple[str, str]]) -> list[float]:
                scores = reranker.compute_score([list(pair) for pair in pairs], normalize=False)
                if isinstance(scores, (float, int)):
                    return [float(scores)]
                return [float(score) for score in scores]

            self._backend = "FlagEmbedding.FlagReranker"
            self._predict_fn = predict_with_flagembedding
            _RERANKER_BACKEND_CACHE[cache_key] = (self._backend, self._predict_fn)
            return
        except Exception as flag_exc:
            flag_error = flag_exc

        try:
            from sentence_transformers import CrossEncoder  # type: ignore

            try:
                model = CrossEncoder(
                    model_source,
                    max_length=self.max_length,
                    local_files_only=self.local_files_only,
                    trust_remote_code=True,
                )
            except TypeError:
                model = CrossEncoder(model_source, max_length=self.max_length)

            def predict_with_sentence_transformers(pairs: list[tuple[str, str]]) -> list[float]:
                scores = model.predict(
                    pairs,
                    batch_size=self.batch_size,
                    show_progress_bar=False,
                    convert_to_numpy=False,
                )
                if isinstance(scores, (float, int)):
                    return [float(scores)]
                return [float(score) for score in list(scores)]

            self._backend = "sentence_transformers.CrossEncoder"
            self._predict_fn = predict_with_sentence_transformers
            _RERANKER_BACKEND_CACHE[cache_key] = (self._backend, self._predict_fn)
            return
        except Exception as st_exc:
            raise RuntimeError(
                "Unable to load model-backed reranker "
                f"{self.model_name!r}. Install/cache FlagEmbedding or sentence-transformers/transformers. "
                f"transformers error: {type(hf_error).__name__}: {hf_error}; "
                f"FlagEmbedding error: {type(flag_error).__name__}: {flag_error}; "
                f"sentence-transformers error: {type(st_exc).__name__}: {st_exc}"
            ) from st_exc

    def _model_source(self) -> str | Path:
        if self.local_model_path and self.local_model_path.exists():
            return self.local_model_path
        return self.model_name


def make_default_candidate_reranker(config: RerankerConfig) -> CandidateReranker:
    model_name = (config.model or "").strip()
    if not model_name:
        raise RuntimeError("enabled reranker requires reranker_config.model.")
    if model_name in {"lexical", "lexical-overlap-v1"}:
        raise RuntimeError("lexical reranker is disabled for runtime use; configure a cross-encoder model.")
    return CrossEncoderReranker(
        model_name,
        local_model_path=config.local_model_path,
        batch_size=config.batch_size,
        max_length=config.max_length,
        local_files_only=config.local_files_only,
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
        return fuse_weighted_sum(candidates_by_path, path_weights=config.fusion_path_weights)
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
    weights = path_weights or DEFAULT_FUSION_PATH_WEIGHTS
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
    record["evidence_roles"] = candidate_roles(candidate)
    record["evidence_role"] = next((role for role in record["evidence_roles"] if role != "generic"), record["evidence_roles"][0])
    record["retrieval_intent"] = candidate.get("retrieval_intent")
    if candidate.get("role_query"):
        record["role_query"] = candidate.get("role_query")
    record["provenance"] = dict(candidate.get("provenance") or {})
    return record


def merge_candidate_metadata(record: dict[str, Any], candidate: dict[str, Any]) -> None:
    record["matched_entities"] = unique_strings(
        [*(record.get("matched_entities") or []), *(candidate.get("matched_entities") or [])]
    )
    record["relation_types"] = unique_strings(
        [*(record.get("relation_types") or []), *(candidate.get("relation_types") or [])]
    )
    merge_candidate_role_metadata(record, candidate)
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
    if not fused_candidates:
        return []

    query = retrieval_query_text(state)
    reranker = candidate_reranker or make_default_candidate_reranker(config.reranker_config)
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
    required_entities = canonical_query_entities(state)
    graded: list[dict[str, Any]] = []
    for candidate in candidates:
        item = dict(candidate)
        grade = grade_candidate(query_terms, item, required_entities=required_entities)
        item["document_grade"] = grade
        item["grade_score"] = grade["score"]
        if grade["accepted"]:
            graded.append(item)

    for index, candidate in enumerate(graded, start=1):
        candidate["rank"] = index
        candidate["graded_rank"] = index
    return graded


def grade_candidate(
    query_terms: set[str],
    candidate: dict[str, Any],
    *,
    required_entities: list[str] | None = None,
) -> dict[str, Any]:
    text = str(candidate.get("text") or candidate.get("text_preview") or "")
    if not text.strip():
        return {"accepted": False, "label": "empty", "score": 0.0, "reason": "missing_text"}

    text_terms = tokenize(text)
    overlap = lexical_overlap_score(query_terms, text_terms)
    matched_entities = [str(entity) for entity in candidate.get("matched_entities") or [] if str(entity).strip()]
    matched_entity_in_text = any(tokenize(entity) <= text_terms for entity in matched_entities)
    required_entity_exact = entity_exact_score(required_entities or [], text)
    has_positive_rank_score = coerce_float(candidate.get("score")) > 0
    grade_score = min(
        1.0,
        overlap
        + (0.35 * required_entity_exact)
        + (0.15 if matched_entity_in_text else 0.0)
        + (0.05 if has_positive_rank_score else 0.0),
    )
    accepted = (required_entity_exact > 0) if required_entities else (overlap > 0 or matched_entity_in_text)
    label = "relevant" if accepted and grade_score >= 0.25 else "weak"
    return {
        "accepted": accepted,
        "label": label,
        "score": round(grade_score, 6),
        "reason": "deterministic_stub_overlap",
        "matched_entity_in_text": matched_entity_in_text,
        "query_overlap": round(overlap, 6),
        "required_entity_exact": round(required_entity_exact, 6),
    }


MEANING_QUERY_TERMS = {"ý nghĩa", "nghĩa", "tượng trưng", "chủ về", "là gì", "giải thích"}
MEANING_TEXT_TERMS = {"ý nghĩa", "nghĩa", "tượng trưng", "chủ về", "biểu tượng", "tính", "tính tình", "đặc tính"}


def canonical_query_entities(state: RAGState) -> list[str]:
    entities: list[str] = []
    seen: set[str] = set()
    for record in state.get("query_entities") or []:
        name = str(record.get("canonical_name") or "").strip()
        if not name:
            continue
        key = normalize_for_match(name)
        if key in seen:
            continue
        seen.add(key)
        entities.append(name)
    return entities


def entity_exact_score(canonical_entities: list[str], text: str) -> float:
    if not canonical_entities:
        return 0.0
    normalized_text = normalize_for_match(text)
    hits = [entity for entity in canonical_entities if normalize_for_match(entity) in normalized_text]
    return len(hits) / len(canonical_entities)


def definition_heading_score(canonical_entities: list[str], text: str) -> float:
    if not canonical_entities:
        return 0.0
    normalized_text = normalize_for_match(text)
    score = 0.0
    for entity in canonical_entities:
        normalized_entity = normalize_for_match(entity)
        if f"{normalized_entity}:" in normalized_text:
            score += 1.0
        elif f"{normalized_entity} -" in normalized_text:
            score += 0.8
    return min(1.0, score / len(canonical_entities))


def definition_quality_score(canonical_entities: list[str], text: str) -> float:
    if not canonical_entities:
        return 0.0
    normalized_text = normalize_for_match(text)
    quality_markers = ("tánh chất", "tính chất", "tánh tình", "tính tình", "địa vị", "tiền tài", "thế đứng")
    score = 0.0
    for entity in canonical_entities:
        normalized_entity = normalize_for_match(entity)
        positions = [
            pos for needle in (f"{normalized_entity}:", f"{normalized_entity} -")
            if (pos := normalized_text.find(needle)) >= 0
        ]
        if not positions:
            continue
        window = normalized_text[min(positions): min(len(normalized_text), min(positions) + 900)]
        marker_hits = sum(1 for marker in quality_markers if marker in window)
        if marker_hits >= 2:
            score += 1.0
        elif marker_hits == 1:
            score += 0.6
    return min(1.0, score / len(canonical_entities))


def has_meaning_intent(query: str) -> bool:
    normalized_query = normalize_for_match(query)
    return any(term in normalized_query for term in MEANING_QUERY_TERMS)


def meaning_signal_score(text: str) -> float:
    normalized_text = normalize_for_match(text)
    return 1.0 if any(term in normalized_text for term in MEANING_TEXT_TERMS) else 0.0


def normalize_for_match(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").casefold()).strip()


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


def candidate_text(candidate: dict[str, Any]) -> str:
    return str(candidate.get("text") or candidate.get("text_preview") or "")


def resolve_local_model_path(path: Path | str | None) -> Path | None:
    if path is None:
        return None
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT_DIR / candidate
    return candidate


def tokenize(text: str) -> set[str]:
    return {token.casefold() for token in TOKEN_RE.findall(text or "") if len(token) > 1}


def lexical_overlap_score(query_terms: set[str], text_terms: set[str]) -> float:
    if not query_terms or not text_terms:
        return 0.0
    return len(query_terms & text_terms) / len(query_terms)


def as_retrieval_candidates(candidates: list[dict[str, Any]]) -> list[RetrievalCandidate]:
    return [dict(candidate) for candidate in candidates]
