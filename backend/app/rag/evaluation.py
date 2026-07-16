from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol

from app.rag.ablation import (
    CITATION_MARKER_RE,
    AblationConfigSpec,
    AblationDatasetItem,
    AblationManifest,
    EmptyNeo4jDriver,
    ExperimentRunStore,
    NullExperimentRunStore,
    SupabaseExperimentRunStore,
    ZeroDenseEmbeddingService,
    citation_source_alignment,
    gold_doc_coverage_rate,
    gold_page_hit_rate,
    gold_quote_overlap_avg,
    load_ablation_dataset,
    load_ablation_manifest,
)
from app.rag.config import ExperimentConfig, config_hash
from app.rag.gemini_keys import get_primary_runtime_gemini_api_key, load_runtime_gemini_api_keys
from app.rag.generation import DeterministicGenerationClient
from app.rag.graph import run_rag_dry_run
from app.rag.rewrite import PassthroughQueryRewriter


ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_W6_EVAL_OUTPUT_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "reports" / "w6_eval_02"
DEFAULT_JUDGE_MODEL = "gemini-3.1-flash-lite-preview"
JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)
RETRIEVAL_NODE_NAMES = {
    "graph_retrieval",
    "dense_retrieval",
    "sparse_retrieval",
    "fusion",
    "rerank",
    "document_grading",
}


def utc_now() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def clamp_score(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if numeric < 0:
        return 0.0
    if numeric > 1:
        return 1.0
    return round(numeric, 4)


def average_defined(values: list[float | int | bool | None]) -> float | None:
    defined = [float(value) for value in values if value is not None]
    if not defined:
        return None
    return round(sum(defined) / len(defined), 4)


def rate_defined(values: list[bool | None]) -> float | None:
    defined = [value for value in values if value is not None]
    if not defined:
        return None
    return round(sum(1 for value in defined if value) / len(defined), 4)


def percentile_defined(values: list[float | int | None], percentile: float) -> float | None:
    defined = sorted(float(value) for value in values if value is not None)
    if not defined:
        return None
    if len(defined) == 1:
        return round(defined[0], 2)
    rank = (len(defined) - 1) * percentile
    lower = int(rank)
    upper = min(lower + 1, len(defined) - 1)
    fraction = rank - lower
    value = defined[lower] * (1 - fraction) + defined[upper] * fraction
    return round(value, 2)


def compact_json(payload: Any, *, max_chars: int = 4_000) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "...[truncated]"


def extract_json_object(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        match = JSON_OBJECT_RE.search(text)
        if not match:
            raise ValueError("Gemini judge response did not contain a JSON object.")
        payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise ValueError("Gemini judge response JSON must be an object.")
    return payload


@dataclass(frozen=True)
class EvaluationJudgeResult:
    faithfulness: float | None
    answer_relevancy: float | None
    context_recall: float | None
    reasons: dict[str, str] = field(default_factory=dict)
    backend: str = "unknown"
    model: str | None = None
    raw_response: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "faithfulness": self.faithfulness,
            "answer_relevancy": self.answer_relevancy,
            "context_recall": self.context_recall,
            "reasons": self.reasons,
            "backend": self.backend,
            "model": self.model,
            "raw_response_present": bool(self.raw_response),
        }


class EvaluationJudge(Protocol):
    backend: str

    def evaluate(
        self,
        *,
        item: AblationDatasetItem,
        state: dict[str, Any],
        config: ExperimentConfig,
    ) -> EvaluationJudgeResult:
        ...


class StaticEvaluationJudge:
    """Deterministic judge for offline smoke tests only; not an official W6 metric judge."""

    backend = "static-smoke"

    def evaluate(
        self,
        *,
        item: AblationDatasetItem,
        state: dict[str, Any],
        config: ExperimentConfig,
    ) -> EvaluationJudgeResult:
        answer = str(state.get("answer") or "").strip()
        sources = state.get("sources") or []
        context_chunks = state.get("context_chunks") or []
        answer_present = bool(answer)
        has_support = bool(sources or context_chunks or item.chart_data)
        has_expected = bool(item.expected_answer_summary or item.gold_answer)
        return EvaluationJudgeResult(
            faithfulness=1.0 if answer_present and has_support else 0.0,
            answer_relevancy=1.0 if answer_present and has_expected else 0.0,
            context_recall=1.0 if has_support else 0.0,
            reasons={
                "faithfulness": "Static smoke score; official W6 runs must use Gemini judge.",
                "answer_relevancy": "Static smoke score; official W6 runs must use Gemini judge.",
                "context_recall": "Static smoke score; official W6 runs must use Gemini judge.",
            },
            backend=self.backend,
            model="static-smoke",
        )


class GeminiEvaluationJudge:
    backend = "gemini"

    def __init__(
        self,
        *,
        model: str = DEFAULT_JUDGE_MODEL,
        api_key: str | None = None,
        temperature: float = 0.0,
        max_output_tokens: int = 768,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    def _api_key(self) -> str:
        return get_primary_runtime_gemini_api_key("W6 Gemini evaluation judge", explicit_api_key=self.api_key)

    def _api_keys(self) -> list[str]:
        if self.api_key:
            return [self.api_key]
        keys = load_runtime_gemini_api_keys()
        if not keys:
            self._api_key()
        return keys

    def evaluate(
        self,
        *,
        item: AblationDatasetItem,
        state: dict[str, Any],
        config: ExperimentConfig,
    ) -> EvaluationJudgeResult:
        try:
            import google.generativeai as genai
        except Exception as exc:
            raise RuntimeError("google-generativeai is required for W6 Gemini evaluation judge.") from exc

        prompt = build_gemini_judge_prompt(item=item, state=state, config=config)
        last_exc: Exception | None = None
        keys = self._api_keys()
        response: Any | None = None
        for index, api_key in enumerate(keys, start=1):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(self.model)
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": self.temperature,
                        "max_output_tokens": self.max_output_tokens,
                    },
                    request_options={"timeout": 20},
                )
                break
            except Exception as exc:
                last_exc = exc
                if self.api_key or index >= len(keys):
                    break
                continue
        if response is None:
            if last_exc is not None:
                raise RuntimeError(f"W6 Gemini evaluation judge failed after {len(keys)} runtime key(s): {last_exc}") from last_exc
            raise RuntimeError("GEMINI_API_KEY or GEMINI_API_KEYS is required for W6 Gemini evaluation judge.")
        raw_text = str(getattr(response, "text", "") or "").strip()
        payload = extract_json_object(raw_text)
        reasons_payload = payload.get("reasons") if isinstance(payload.get("reasons"), dict) else {}
        reasons = {
            key: str(value)
            for key, value in reasons_payload.items()
            if key in {"faithfulness", "answer_relevancy", "context_recall"}
        }
        return EvaluationJudgeResult(
            faithfulness=clamp_score(payload.get("faithfulness")),
            answer_relevancy=clamp_score(payload.get("answer_relevancy")),
            context_recall=clamp_score(payload.get("context_recall")),
            reasons=reasons,
            backend=self.backend,
            model=self.model,
            raw_response=raw_text,
        )


def build_gemini_judge_prompt(
    *,
    item: AblationDatasetItem,
    state: dict[str, Any],
    config: ExperimentConfig,
) -> str:
    answer = str(state.get("answer") or "")
    source_context = build_source_context_for_judge(state)
    chart_context = compact_json(item.chart_data or state.get("chart_data") or {}, max_chars=4_000)
    gold_context = compact_json(item.gold_context_spans, max_chars=4_000)
    expected_summary = item.expected_answer_summary or ""
    gold_answer = item.gold_answer or ""
    question_family = (item.labels or {}).get("question_family")
    chart_only_note = (
        "This item has no gold_context_spans; evaluate context_recall using CHART_CONTEXT and retrieved SOURCE_CONTEXT."
        if not item.gold_context_spans
        else "Evaluate context_recall primarily against GOLD_CONTEXT_SPANS and the needed evidence in EXPECTED/GOLD answer."
    )

    return f"""
You are an impartial RAG evaluator for a Vietnamese Tử Vi question-answering system.

Return ONLY a valid JSON object with this exact shape:
{{
  "faithfulness": 0.0,
  "answer_relevancy": 0.0,
  "context_recall": 0.0,
  "reasons": {{
    "faithfulness": "short reason",
    "answer_relevancy": "short reason",
    "context_recall": "short reason"
  }}
}}

Scoring rules:
- faithfulness: 1 means the answer is fully supported by CHART_CONTEXT and/or SOURCE_CONTEXT; 0 means unsupported or hallucinated.
- answer_relevancy: 1 means the answer directly and completely answers QUESTION compared with EXPECTED_SUMMARY/GOLD_ANSWER; 0 means irrelevant.
- context_recall: 1 means retrieved context contains the evidence needed for EXPECTED_SUMMARY/GOLD_ANSWER; 0 means missing key evidence.
- Scores may be decimals between 0 and 1.
- Do not reward astrology claims that are absent from provided context.
- Keep reasons concise.

Domain: TUVI
Experiment config: {config.name} | chunk_strategy_id={config.chunk_strategy_id}
Question complexity: {item.question_complexity}
Question family: {question_family}
Context recall note: {chart_only_note}

QUESTION:
{item.query}

ANSWER_TO_EVALUATE:
{answer}

EXPECTED_SUMMARY:
{expected_summary}

GOLD_ANSWER:
{gold_answer}

CHART_CONTEXT_JSON:
{chart_context}

GOLD_CONTEXT_SPANS_JSON:
{gold_context}

RETRIEVED_SOURCE_CONTEXT:
{source_context}
""".strip()


def build_source_context_for_judge(state: dict[str, Any], *, max_chars: int = 5_000) -> str:
    chunks = state.get("context_chunks") or []
    if not chunks:
        chunks = state.get("sources") or []
    blocks: list[str] = []
    for index, chunk in enumerate(chunks[:10], start=1):
        marker = chunk.get("citation_marker") or f"S{index}"
        source_id = chunk.get("source_id") or (chunk.get("provenance") or {}).get("source_id")
        page = chunk.get("source_page") or chunk.get("page_book") or chunk.get("page_pdf")
        excerpt = chunk.get("excerpt") or chunk.get("text") or ""
        paths = chunk.get("retrieval_paths") or chunk.get("retrieval_path") or []
        blocks.append(
            f"[{marker}] source_id={source_id}; page={page}; retrieval_paths={paths}\n{excerpt}"
        )
    text = "\n\n".join(blocks)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated]"


RagRunCallable = Callable[[AblationDatasetItem, ExperimentConfig], dict[str, Any]]


def make_evaluation_rag_runner(
    *,
    offline_smoke: bool = False,
    retrieval_fallback_on_error: bool = True,
) -> RagRunCallable:
    def run_item(item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
        initial_state: dict[str, Any] = {"chart_id": item.chart_id, "query": item.query}
        if item.user_id:
            initial_state["user_id"] = item.user_id
        if item.question_complexity:
            initial_state["question_complexity"] = item.question_complexity
        question_family = (item.labels or {}).get("question_family")
        if question_family:
            initial_state["question_family"] = question_family

        chart_loader = None
        if item.chart_data is not None:
            chart_loader = lambda chart_id, user_id=None: {  # noqa: E731 - small per-item adapter
                "id": chart_id,
                "user_id": user_id,
                "chart_system": "TUVI",
                "chart_data": item.chart_data,
            }

        kwargs: dict[str, Any] = {
            "experiment_config": config,
            "chart_loader": chart_loader,
            "retrieval_fallback_on_error": retrieval_fallback_on_error,
        }
        if offline_smoke:
            kwargs.update(
                {
                    "query_rewriter": PassthroughQueryRewriter(),
                    "neo4j_driver": EmptyNeo4jDriver(),
                    "dense_embedding_service": ZeroDenseEmbeddingService(),
                    "generation_client": DeterministicGenerationClient(),
                }
            )
        return dict(run_rag_dry_run(initial_state, **kwargs))

    return run_item


@dataclass(frozen=True)
class EvaluationRunner:
    run_store: ExperimentRunStore = field(default_factory=NullExperimentRunStore)
    rag_runner: RagRunCallable = field(default_factory=make_evaluation_rag_runner)
    judge: EvaluationJudge = field(default_factory=GeminiEvaluationJudge)
    fail_fast: bool = False
    write_reports: bool = True

    def run(
        self,
        manifest: AblationManifest,
        *,
        limit: int | None = None,
        output_dir: Path | None = None,
    ) -> dict[str, Any]:
        items = load_ablation_dataset(manifest.dataset_path, limit=limit)
        effective_output_dir = output_dir or manifest.output_dir
        started_at = utc_now()
        config_results: list[dict[str, Any]] = []

        for spec in manifest.configs:
            config = spec.build_config()
            run_id = self.run_store.create_run(config=config, manifest=manifest, notes=manifest.notes)
            item_results: list[dict[str, Any]] = []
            config_started = utc_now()
            config_error: str | None = None
            try:
                for item in items:
                    item_results.append(self._run_item(item, config))
            except Exception as exc:
                config_error = f"{type(exc).__name__}: {exc}"
                if self.fail_fast:
                    metrics = aggregate_evaluation_metrics(item_results, expected_item_count=len(items))
                    trace = build_evaluation_trace(manifest=manifest, spec=spec, config=config, item_results=item_results)
                    self.run_store.fail_run(run_id, metrics=metrics, trace=trace, error=config_error)
                    raise

            metrics = aggregate_evaluation_metrics(item_results, expected_item_count=len(items))
            grouped_metrics = aggregate_grouped_metrics(item_results)
            trace = build_evaluation_trace(
                manifest=manifest,
                spec=spec,
                config=config,
                item_results=item_results,
                grouped_metrics=grouped_metrics,
            )
            if config_error:
                self.run_store.fail_run(run_id, metrics=metrics, trace=trace, error=config_error)
                status = "failed"
            else:
                self.run_store.complete_run(run_id, metrics=metrics, trace=trace)
                status = "completed"
            config_results.append(
                {
                    "config_name": spec.name,
                    "experiment_id": config.experiment_id,
                    "config_hash": config_hash(config),
                    "chunk_strategy_id": config.chunk_strategy_id,
                    "graph_retrieval_enabled": config.graph_retrieval_enabled,
                    "dense_retrieval_enabled": config.dense_retrieval_enabled,
                    "sparse_retrieval_enabled": config.sparse_retrieval_enabled,
                    "fusion_method": config.fusion_method,
                    "reranker_enabled": config.reranker_enabled,
                    "document_grading_enabled": config.document_grading_enabled,
                    "context_assembly_strategy": config.context_assembly_strategy,
                    "prompt_template_id": config.prompt_template_id,
                    "generation_model": config.generation_model,
                    "run_id": run_id,
                    "status": status,
                    "started_at": config_started,
                    "completed_at": utc_now(),
                    "metrics": metrics,
                    "grouped_metrics": grouped_metrics,
                    "items": item_results,
                    "error": config_error,
                }
            )

        report = {
            "manifest_name": manifest.name,
            "notes": manifest.notes,
            "dataset_path": str(manifest.dataset_path),
            "output_dir": str(effective_output_dir),
            "started_at": started_at,
            "completed_at": utc_now(),
            "dataset_item_count": len(items),
            "config_count": len(config_results),
            "judge_backend": self.judge.backend,
            "metric_definitions": metric_definitions(self.judge.backend),
            "configs": config_results,
        }
        report["ablation_analysis"] = build_ablation_analysis(report)
        chunking_analysis = build_chunking_ablation_analysis(report)
        if chunking_analysis:
            report["chunking_ablation_analysis"] = chunking_analysis
        generation_analysis = build_generation_prompt_ablation_analysis(report)
        if generation_analysis:
            report["generation_prompt_ablation_analysis"] = generation_analysis
        if self.write_reports:
            write_evaluation_reports(report, effective_output_dir)
        return report

    def _run_item(self, item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
        started = time.perf_counter()
        try:
            state = self.rag_runner(item, config)
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            judge_result = self.judge.evaluate(item=item, state=state, config=config)
            return summarize_evaluation_item(item, state, judge_result, latency_ms=latency_ms)
        except Exception as exc:
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            result = summarize_evaluation_error(item, exc, latency_ms=latency_ms)
            if self.fail_fast:
                raise
            return result


def summarize_evaluation_item(
    item: AblationDatasetItem,
    state: dict[str, Any],
    judge_result: EvaluationJudgeResult,
    *,
    latency_ms: float,
) -> dict[str, Any]:
    answer = state.get("answer") or ""
    sources = state.get("sources") or []
    context_chunks = state.get("context_chunks") or []
    citation_metadata = state.get("citation_metadata") or {}
    context_summary = state.get("context_summary") or {}
    diagnostics = state.get("retrieval_diagnostics") or {}
    markers = list(dict.fromkeys(CITATION_MARKER_RE.findall(str(answer))))
    chart_only = len(item.gold_context_spans) == 0
    retrieval_paths = selected_retrieval_paths(state)
    graph_hit = None if chart_only else (bool(state.get("graph_candidates")) or "graph" in retrieval_paths)
    citation_coverage = None if chart_only else citation_coverage_value(markers, sources, citation_metadata)
    context_recall = None if chart_only else judge_result.context_recall
    chart_context_grounding = judge_result.context_recall if chart_only else None
    question_family = str((item.labels or {}).get("question_family") or "") or None

    return {
        "item_id": item.id,
        "chart_id": item.chart_id,
        "query": item.query,
        "question_complexity": item.question_complexity,
        "question_family": question_family,
        "labels": item.labels,
        "chart_only": chart_only,
        "gold_span_count": len(item.gold_context_spans),
        "status": "completed",
        "latency_ms": latency_ms,
        "retrieval_latency_ms": retrieval_latency_ms(state),
        "answer_present": bool(str(answer).strip()),
        "answer_length_chars": len(str(answer)),
        "faithfulness": judge_result.faithfulness,
        "answer_relevancy": judge_result.answer_relevancy,
        "context_recall": context_recall,
        "chart_context_grounding": chart_context_grounding,
        "judge": judge_result.as_dict(),
        "graph_hit": graph_hit,
        "citation_coverage": citation_coverage,
        "source_count": len(sources),
        "citation_marker_count": len(markers),
        "citation_marker_presence": bool(markers),
        "citation_source_alignment": citation_source_alignment(markers, sources),
        "citation_fallback": bool(citation_metadata.get("citation_fallback")),
        "context_selected_count": int(context_summary.get("selected_count") or len(context_chunks) or 0),
        "selected_retrieval_paths": retrieval_paths,
        "retrieval_diagnostics": diagnostics,
        "diagnostic_question_complexity": diagnostics.get("question_complexity"),
        "diagnostic_question_family": diagnostics.get("question_family"),
        "diagnostic_candidate_counts": diagnostics.get("candidate_counts") or {},
        "diagnostic_selected_retrieval_paths": diagnostics.get("final_selected_retrieval_paths") or [],
        "diagnostic_selected_evidence_roles": diagnostics.get("selected_evidence_roles") or [],
        "diagnostic_family_match": diagnostics.get("question_family") == question_family if question_family else None,
        "diagnostic_complexity_match": diagnostics.get("question_complexity") == item.question_complexity if item.question_complexity else None,
        "gold_doc_coverage_rate": gold_doc_coverage_rate(sources, item.gold_context_spans),
        "gold_page_hit_rate": gold_page_hit_rate(sources, item.gold_context_spans),
        "gold_quote_overlap_avg": gold_quote_overlap_avg(sources, item.gold_context_spans),
        "trace_node_statuses": trace_node_statuses(state),
        "error": None,
    }


def summarize_evaluation_error(item: AblationDatasetItem, exc: Exception, *, latency_ms: float) -> dict[str, Any]:
    question_family = str((item.labels or {}).get("question_family") or "") or None
    return {
        "item_id": item.id,
        "chart_id": item.chart_id,
        "query": item.query,
        "question_complexity": item.question_complexity,
        "question_family": question_family,
        "labels": item.labels,
        "chart_only": len(item.gold_context_spans) == 0,
        "gold_span_count": len(item.gold_context_spans),
        "status": "failed",
        "latency_ms": latency_ms,
        "retrieval_latency_ms": None,
        "answer_present": False,
        "answer_length_chars": 0,
        "faithfulness": None,
        "answer_relevancy": None,
        "context_recall": None,
        "chart_context_grounding": None,
        "judge": {},
        "graph_hit": None,
        "citation_coverage": None,
        "source_count": 0,
        "citation_marker_count": 0,
        "citation_marker_presence": False,
        "citation_source_alignment": False,
        "citation_fallback": False,
        "context_selected_count": 0,
        "selected_retrieval_paths": [],
        "retrieval_diagnostics": {},
        "diagnostic_question_complexity": None,
        "diagnostic_question_family": None,
        "diagnostic_candidate_counts": {},
        "diagnostic_selected_retrieval_paths": [],
        "diagnostic_selected_evidence_roles": [],
        "diagnostic_family_match": None,
        "diagnostic_complexity_match": None,
        "gold_doc_coverage_rate": None,
        "gold_page_hit_rate": None,
        "gold_quote_overlap_avg": None,
        "trace_node_statuses": [],
        "error": f"{type(exc).__name__}: {exc}",
    }


def citation_coverage_value(markers: list[str], sources: list[dict[str, Any]], citation_metadata: dict[str, Any]) -> float:
    if not sources:
        return 0.0
    if markers:
        return 1.0 if citation_source_alignment(markers, sources) else 0.0
    return 1.0 if citation_metadata.get("citation_fallback") else 0.75


def selected_retrieval_paths(state: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for collection_name in ("context_chunks", "sources"):
        for item in state.get(collection_name) or []:
            raw_paths = item.get("retrieval_paths") or []
            if isinstance(raw_paths, str):
                raw_paths = [raw_paths]
            for path in raw_paths:
                value = str(path).strip()
                if value and value not in paths:
                    paths.append(value)
            raw_path = item.get("retrieval_path")
            if raw_path and str(raw_path) not in paths:
                paths.append(str(raw_path))
    return paths


def retrieval_latency_ms(state: dict[str, Any]) -> float | None:
    trace = state.get("retrieval_trace") or {}
    explicit = trace.get("retrieval_latency_ms") or trace.get("retrieval_duration_ms")
    if explicit is not None:
        try:
            return round(float(explicit), 2)
        except (TypeError, ValueError):
            return None
    durations: list[float] = []
    for node in trace.get("nodes") or []:
        if node.get("node") not in RETRIEVAL_NODE_NAMES:
            continue
        raw_duration = node.get("duration_ms") or node.get("latency_ms")
        if raw_duration is None:
            continue
        try:
            durations.append(float(raw_duration))
        except (TypeError, ValueError):
            continue
    if not durations:
        return None
    return round(sum(durations), 2)


def trace_node_statuses(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"node": node.get("node"), "status": node.get("status", "completed")}
        for node in (state.get("retrieval_trace") or {}).get("nodes", [])
    ]


def average_diagnostic_candidate_count(item_results: list[dict[str, Any]], key: str) -> float | None:
    return average_defined([
        (item.get("diagnostic_candidate_counts") or {}).get(key)
        for item in item_results
    ])


def selected_path_rate(item_results: list[dict[str, Any]], path: str) -> float | None:
    values: list[bool | None] = []
    for item in item_results:
        paths = item.get("diagnostic_selected_retrieval_paths")
        if paths is None:
            values.append(None)
        else:
            values.append(path in paths)
    return rate_defined(values)


def aggregate_evaluation_metrics(
    item_results: list[dict[str, Any]],
    *,
    expected_item_count: int | None = None,
) -> dict[str, Any]:
    item_count = expected_item_count if expected_item_count is not None else len(item_results)
    completed = [item for item in item_results if item.get("status") == "completed"]
    failed_count = item_count - len(completed)
    denominator = item_count or 1
    chart_only_count = sum(1 for item in item_results if item.get("chart_only"))
    corpus_items = [item for item in item_results if not item.get("chart_only")]
    corpus_denominator = len(corpus_items) or 1
    return {
        "item_count": item_count,
        "completed_count": len(completed),
        "failed_count": failed_count,
        "chart_only_count": chart_only_count,
        "corpus_grounded_item_count": item_count - chart_only_count,
        "answer_present_rate": round(sum(1 for item in item_results if item.get("answer_present")) / denominator, 4),
        "faithfulness_avg": average_defined([item.get("faithfulness") for item in item_results]),
        "answer_relevancy_avg": average_defined([item.get("answer_relevancy") for item in item_results]),
        "context_recall_avg": average_defined([item.get("context_recall") for item in item_results]),
        "chart_context_grounding_avg": average_defined([item.get("chart_context_grounding") for item in item_results]),
        "graph_hit_rate": rate_defined([item.get("graph_hit") for item in item_results]),
        "citation_coverage_rate": average_defined([item.get("citation_coverage") for item in item_results]),
        "corpus_source_coverage_rate": round(
            sum(1 for item in corpus_items if item.get("source_count", 0) > 0) / corpus_denominator,
            4,
        ) if corpus_items else None,
        "source_coverage_rate": round(sum(1 for item in item_results if item.get("source_count", 0) > 0) / denominator, 4),
        "avg_source_count": round(sum(float(item.get("source_count") or 0) for item in item_results) / denominator, 4),
        "avg_gold_doc_coverage_rate": average_defined([item.get("gold_doc_coverage_rate") for item in item_results]),
        "avg_gold_page_hit_rate": average_defined([item.get("gold_page_hit_rate") for item in item_results]),
        "avg_gold_quote_overlap": average_defined([item.get("gold_quote_overlap_avg") for item in item_results]),
        "p95_latency_ms": percentile_defined([item.get("latency_ms") for item in item_results], 0.95),
        "avg_latency_ms": average_defined([item.get("latency_ms") for item in item_results]),
        "retrieval_p95_ms": percentile_defined([item.get("retrieval_latency_ms") for item in item_results], 0.95),
        "avg_retrieval_latency_ms": average_defined([item.get("retrieval_latency_ms") for item in item_results]),
        "citation_marker_presence_rate": round(
            sum(1 for item in corpus_items if item.get("citation_marker_presence")) / corpus_denominator,
            4,
        ) if corpus_items else None,
        "citation_source_alignment_rate": round(
            sum(1 for item in corpus_items if item.get("citation_source_alignment")) / corpus_denominator,
            4,
        ) if corpus_items else None,
        "context_selected_count_avg": average_defined([item.get("context_selected_count") for item in item_results]),
        "avg_graph_candidate_count": average_diagnostic_candidate_count(item_results, "graph"),
        "avg_dense_candidate_count": average_diagnostic_candidate_count(item_results, "dense"),
        "avg_sparse_candidate_count": average_diagnostic_candidate_count(item_results, "sparse"),
        "avg_fused_candidate_count": average_diagnostic_candidate_count(item_results, "fused"),
        "avg_ranked_candidate_count": average_diagnostic_candidate_count(item_results, "ranked"),
        "avg_context_selected_diagnostic_count": average_diagnostic_candidate_count(item_results, "context_selected"),
        "selected_graph_path_rate": selected_path_rate(item_results, "graph"),
        "selected_dense_path_rate": selected_path_rate(item_results, "dense"),
        "selected_sparse_path_rate": selected_path_rate(item_results, "sparse"),
    }


def aggregate_grouped_metrics(item_results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "by_question_complexity": aggregate_by_key(item_results, "question_complexity"),
        "by_question_family": aggregate_by_key(item_results, "question_family"),
    }


def aggregate_by_key(item_results: list[dict[str, Any]], key: str) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in item_results:
        value = str(item.get(key) or "unknown")
        groups.setdefault(value, []).append(item)
    return {
        group: aggregate_evaluation_metrics(items, expected_item_count=len(items))
        for group, items in sorted(groups.items())
    }


def build_evaluation_trace(
    *,
    manifest: AblationManifest,
    spec: AblationConfigSpec,
    config: ExperimentConfig,
    item_results: list[dict[str, Any]],
    grouped_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "manifest_name": manifest.name,
        "dataset_path": str(manifest.dataset_path),
        "config_spec_name": spec.name,
        "experiment_id": config.experiment_id,
        "config_hash": config_hash(config),
        "chunk_strategy_id": config.chunk_strategy_id,
        "grouped_metrics": grouped_metrics or aggregate_grouped_metrics(item_results),
        "items": item_results,
    }


def metric_definitions(judge_backend: str) -> dict[str, Any]:
    return {
        "faithfulness": f"Gemini judge score in official runs; current judge_backend={judge_backend}.",
        "answer_relevancy": f"Gemini judge score in official runs; current judge_backend={judge_backend}.",
        "context_recall": "Gemini judge score for corpus-grounded items; chart-only Direct items are excluded from this aggregate and reported as chart_context_grounding.",
        "graph_hit_rate": "Rate of non-chart-only items with graph candidates or graph-selected context.",
        "citation_coverage_rate": "Average citation/source coverage for non-chart-only corpus-grounded items; Direct chart-only items are excluded.",
        "p95_latency_ms": "95th percentile end-to-end runner latency per item.",
        "retrieval_p95_ms": "95th percentile retrieval latency if node timing is present; null until W6-RAG-01 timing diagnostics are available.",
    }


def metric_value(config_result: dict[str, Any], metric_name: str) -> float | None:
    value = (config_result.get("metrics") or {}).get(metric_name)
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def rank_configs_by_metric(
    configs: list[dict[str, Any]],
    metric_name: str,
    *,
    higher_is_better: bool = True,
) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for config in configs:
        value = metric_value(config, metric_name)
        if value is None:
            continue
        ranked.append(
            {
                "config_name": config.get("config_name"),
                "experiment_id": config.get("experiment_id"),
                "metric": metric_name,
                "value": value,
            }
        )
    return sorted(ranked, key=lambda item: item["value"], reverse=higher_is_better)


def rank_chunk_strategies_by_metric(
    configs: list[dict[str, Any]],
    metric_name: str,
    *,
    higher_is_better: bool = True,
) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for config in configs:
        strategy = config.get("chunk_strategy_id")
        value = metric_value(config, metric_name)
        if not strategy or value is None:
            continue
        ranked.append(
            {
                "chunk_strategy_id": strategy,
                "config_name": config.get("config_name"),
                "experiment_id": config.get("experiment_id"),
                "metric": metric_name,
                "value": value,
            }
        )
    return sorted(ranked, key=lambda item: item["value"], reverse=higher_is_better)


def summarize_retrieval_misses(config: dict[str, Any], *, max_examples: int = 5) -> dict[str, Any]:
    misses: list[dict[str, Any]] = []
    for item in config.get("items") or []:
        if item.get("chart_only") or item.get("status") != "completed":
            continue
        doc_coverage = item.get("gold_doc_coverage_rate")
        source_count = int(item.get("source_count") or 0)
        context_recall = item.get("context_recall")
        candidate_counts = item.get("diagnostic_candidate_counts") or {}
        has_low_context_recall = context_recall is not None and float(context_recall) < 0.5
        has_doc_miss = doc_coverage in (None, 0, 0.0)
        has_no_sources = source_count == 0
        if not (has_doc_miss or has_no_sources or has_low_context_recall):
            continue
        reasons: list[str] = []
        if has_doc_miss:
            reasons.append("gold_doc_miss")
        if has_no_sources:
            reasons.append("no_sources")
        if has_low_context_recall:
            reasons.append("low_context_recall")
        misses.append(
            {
                "item_id": item.get("item_id"),
                "question_complexity": item.get("question_complexity"),
                "question_family": item.get("question_family"),
                "reasons": reasons,
                "context_recall": context_recall,
                "gold_doc_coverage_rate": doc_coverage,
                "source_count": source_count,
                "candidate_counts": candidate_counts,
                "selected_retrieval_paths": item.get("diagnostic_selected_retrieval_paths") or [],
            }
        )
    return {
        "config_name": config.get("config_name"),
        "miss_count": len(misses),
        "examples": misses[:max_examples],
    }


def summarize_rerank_misses(config: dict[str, Any], *, max_examples: int = 5) -> dict[str, Any]:
    misses: list[dict[str, Any]] = []
    if not config.get("reranker_enabled"):
        return {"config_name": config.get("config_name"), "miss_count": 0, "examples": []}
    for item in config.get("items") or []:
        if item.get("chart_only") or item.get("status") != "completed":
            continue
        candidate_counts = item.get("diagnostic_candidate_counts") or {}
        fused_count = int(candidate_counts.get("fused") or 0)
        ranked_count = int(candidate_counts.get("ranked") or candidate_counts.get("reranked") or 0)
        selected_count = int(candidate_counts.get("context_selected") or item.get("context_selected_count") or 0)
        doc_coverage = item.get("gold_doc_coverage_rate")
        citation_coverage = item.get("citation_coverage")
        if fused_count <= 0 and ranked_count <= 0:
            continue
        if selected_count <= 0:
            continue
        if doc_coverage not in (None, 0, 0.0) and citation_coverage not in (None, 0, 0.0):
            continue
        misses.append(
            {
                "item_id": item.get("item_id"),
                "question_complexity": item.get("question_complexity"),
                "question_family": item.get("question_family"),
                "gold_doc_coverage_rate": doc_coverage,
                "citation_coverage": citation_coverage,
                "candidate_counts": candidate_counts,
                "selected_retrieval_paths": item.get("diagnostic_selected_retrieval_paths") or [],
                "note": "Heuristic rerank miss: candidates existed and context was selected, but gold/citation coverage remained low.",
            }
        )
    return {
        "config_name": config.get("config_name"),
        "miss_count": len(misses),
        "examples": misses[:max_examples],
    }


def choose_preliminary_recommendation(configs: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [config for config in configs if config.get("status") == "completed"]
    if not completed:
        return {
            "recommended_candidate": None,
            "reasoning": ["No completed configs were available for recommendation."],
        }

    def score(config: dict[str, Any]) -> float:
        metrics = config.get("metrics") or {}
        quality = (
            float(metrics.get("context_recall_avg") or 0) * 0.35
            + float(metrics.get("citation_coverage_rate") or 0) * 0.25
            + float(metrics.get("faithfulness_avg") or 0) * 0.2
            + float(metrics.get("answer_relevancy_avg") or 0) * 0.15
            + float(metrics.get("graph_hit_rate") or 0) * 0.05
        )
        latency = float(metrics.get("p95_latency_ms") or 0)
        latency_penalty = min(latency / 30_000, 0.2) if latency else 0.0
        return quality - latency_penalty

    best = max(completed, key=score)
    metrics = best.get("metrics") or {}
    return {
        "recommended_candidate": best.get("config_name"),
        "score": round(score(best), 4),
        "reasoning": [
            "Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.",
            f"Selected `{best.get('config_name')}` with context_recall_avg={metrics.get('context_recall_avg')}, citation_coverage_rate={metrics.get('citation_coverage_rate')}, p95_latency_ms={metrics.get('p95_latency_ms')}.",
            "Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.",
        ],
    }


def build_ablation_analysis(report: dict[str, Any]) -> dict[str, Any]:
    configs = list(report.get("configs") or [])
    baseline_name = "baseline_graph_sparse_rrf"
    return {
        "baseline_config_name": baseline_name,
        "ranking_by_context_recall": rank_configs_by_metric(configs, "context_recall_avg"),
        "ranking_by_citation_coverage": rank_configs_by_metric(configs, "citation_coverage_rate"),
        "ranking_by_graph_hit_rate": rank_configs_by_metric(configs, "graph_hit_rate"),
        "ranking_by_p95_latency": rank_configs_by_metric(configs, "p95_latency_ms", higher_is_better=False),
        "retrieval_miss_summary": [summarize_retrieval_misses(config) for config in configs],
        "rerank_miss_summary": [summarize_rerank_misses(config) for config in configs],
        "preliminary_recommendation": choose_preliminary_recommendation(configs),
    }


def choose_chunking_candidate(configs: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [config for config in configs if config.get("status") == "completed" and config.get("chunk_strategy_id")]
    if not completed:
        return {
            "recommended_chunk_strategy_id": None,
            "recommended_config_name": None,
            "reasoning_vi": ["Chưa có cấu hình chunking nào hoàn tất để chọn ứng viên."],
        }

    def score(config: dict[str, Any]) -> float:
        metrics = config.get("metrics") or {}
        quality = (
            float(metrics.get("context_recall_avg") or 0) * 0.4
            + float(metrics.get("citation_coverage_rate") or 0) * 0.25
            + float(metrics.get("graph_hit_rate") or 0) * 0.15
            + float(metrics.get("faithfulness_avg") or 0) * 0.1
            + float(metrics.get("answer_relevancy_avg") or 0) * 0.1
        )
        latency = float(metrics.get("p95_latency_ms") or 0)
        latency_penalty = min(latency / 30_000, 0.2) if latency else 0.0
        return quality - latency_penalty

    best = max(completed, key=score)
    metrics = best.get("metrics") or {}
    return {
        "recommended_chunk_strategy_id": best.get("chunk_strategy_id"),
        "recommended_config_name": best.get("config_name"),
        "score": round(score(best), 4),
        "reasoning_vi": [
            "Đây là gợi ý sơ bộ do máy tính tổng hợp, không phải quyết định production cuối cùng.",
            "Điểm ưu tiên Context Recall, Citation Coverage, Graph Hit Rate, sau đó mới xét Faithfulness, Answer Relevancy và phạt nhẹ p95 latency.",
            f"Ứng viên hiện tại là `{best.get('chunk_strategy_id')}` qua config `{best.get('config_name')}` với context_recall_avg={metrics.get('context_recall_avg')}, citation_coverage_rate={metrics.get('citation_coverage_rate')}, graph_hit_rate={metrics.get('graph_hit_rate')}, p95_latency_ms={metrics.get('p95_latency_ms')}.",
            "Chỉ được dùng làm bằng chứng chính thức sau khi chạy Gemini judge/live database trên cùng golden dataset và đủ 12 cặp source-strategy.",
        ],
    }


def build_chunking_ablation_analysis(report: dict[str, Any]) -> dict[str, Any] | None:
    configs = list(report.get("configs") or [])
    strategies = sorted({str(config.get("chunk_strategy_id")) for config in configs if config.get("chunk_strategy_id")})
    manifest_name = str(report.get("manifest_name") or "")
    if len(strategies) < 2 and "w6_abl_03" not in manifest_name:
        return None
    if "w6_abl_03" not in manifest_name and len(strategies) < 3:
        return None
    return {
        "analysis_language": "vi",
        "scope_vi": "So sánh chiến lược chunking trên cùng corpus TVKL/TVNL/TVHS/TVGM; biến chính là chunk_strategy_id.",
        "semantic_strategy_note_vi": "PLAN.md gọi chiến lược semantic là chunk_semantic_embedding; runtime hiện dùng mã chunk_semantic_embedding_bge_m3.",
        "dense_policy_vi": "Matrix chính tắt dense retrieval để không trộn lẫn biến chunking với biến dense retrieval. Retrieval stack cố định là Graph + Sparse + RRF + reranker.",
        "strategies": strategies,
        "ranking_by_context_recall": rank_chunk_strategies_by_metric(configs, "context_recall_avg"),
        "ranking_by_citation_coverage": rank_chunk_strategies_by_metric(configs, "citation_coverage_rate"),
        "ranking_by_graph_hit_rate": rank_chunk_strategies_by_metric(configs, "graph_hit_rate"),
        "ranking_by_p95_latency": rank_chunk_strategies_by_metric(configs, "p95_latency_ms", higher_is_better=False),
        "preliminary_chunking_candidate": choose_chunking_candidate(configs),
    }


def choose_generation_prompt_candidate(configs: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [config for config in configs if config.get("status") == "completed" and config.get("prompt_template_id")]
    if not completed:
        return {
            "recommended_prompt_template_id": None,
            "recommended_generation_model": None,
            "recommended_config_name": None,
            "reasoning_vi": ["Chưa có cấu hình generation/prompt nào hoàn tất để chọn ứng viên."],
        }

    def score(config: dict[str, Any]) -> float:
        metrics = config.get("metrics") or {}
        quality = (
            float(metrics.get("faithfulness_avg") or 0) * 0.4
            + float(metrics.get("answer_relevancy_avg") or 0) * 0.3
            + float(metrics.get("citation_coverage_rate") or 0) * 0.2
            + float(metrics.get("chart_context_grounding_avg") or 0) * 0.1
        )
        latency = float(metrics.get("p95_latency_ms") or 0)
        latency_penalty = min(latency / 30_000, 0.2) if latency else 0.0
        return quality - latency_penalty

    best = max(completed, key=score)
    metrics = best.get("metrics") or {}
    return {
        "recommended_prompt_template_id": best.get("prompt_template_id"),
        "recommended_generation_model": best.get("generation_model"),
        "recommended_config_name": best.get("config_name"),
        "score": round(score(best), 4),
        "reasoning_vi": [
            "Đây là gợi ý sơ bộ cho W7-ABL-01 dựa trên partial run, không phải quyết định production cuối cùng.",
            "Điểm ưu tiên Faithfulness, Answer Relevancy, Citation Coverage và Chart Context Grounding; p95 latency bị phạt nhẹ.",
            f"Ứng viên hiện tại là prompt `{best.get('prompt_template_id')}` với model `{best.get('generation_model')}` qua config `{best.get('config_name')}`: faithfulness_avg={metrics.get('faithfulness_avg')}, answer_relevancy_avg={metrics.get('answer_relevancy_avg')}, citation_coverage_rate={metrics.get('citation_coverage_rate')}, p95_latency_ms={metrics.get('p95_latency_ms')}.",
            "W7-CONFIG-01 sẽ tổng hợp thêm evidence retrieval/chunking/latency trước khi lock default_production.yaml.",
        ],
    }


def rank_generation_prompts_by_metric(
    configs: list[dict[str, Any]],
    metric_name: str,
    *,
    higher_is_better: bool = True,
) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for config in configs:
        prompt_template_id = config.get("prompt_template_id")
        value = metric_value(config, metric_name)
        if not prompt_template_id or value is None:
            continue
        ranked.append(
            {
                "prompt_template_id": prompt_template_id,
                "generation_model": config.get("generation_model"),
                "config_name": config.get("config_name"),
                "experiment_id": config.get("experiment_id"),
                "metric": metric_name,
                "value": value,
            }
        )
    return sorted(ranked, key=lambda item: item["value"], reverse=higher_is_better)


def build_generation_prompt_ablation_analysis(report: dict[str, Any]) -> dict[str, Any] | None:
    configs = list(report.get("configs") or [])
    manifest_name = str(report.get("manifest_name") or "")
    prompt_ids = sorted({str(config.get("prompt_template_id")) for config in configs if config.get("prompt_template_id")})
    if "w7_abl_01" not in manifest_name and len(prompt_ids) < 2:
        return None
    return {
        "analysis_language": "vi",
        "scope_vi": "So sánh prompt template và generation model, giữ retrieval config cố định để cô lập ảnh hưởng generation.",
        "retrieval_control_vi": "Retrieval stack cố định theo W6 integration candidate: chunk_semantic_embedding_bge_m3, Graph + Sparse + RRF + lexical reranker, dense off.",
        "partial_run_policy_vi": "Run chính của task này là Gemini judge partial 10 câu balanced; full/expanded run sẽ để W7-CONFIG-01/W8 hoặc khi quota cho phép.",
        "prompt_template_ids": prompt_ids,
        "generation_models": sorted({str(config.get("generation_model")) for config in configs if config.get("generation_model")}),
        "ranking_by_faithfulness": rank_generation_prompts_by_metric(configs, "faithfulness_avg"),
        "ranking_by_answer_relevancy": rank_generation_prompts_by_metric(configs, "answer_relevancy_avg"),
        "ranking_by_citation_coverage": rank_generation_prompts_by_metric(configs, "citation_coverage_rate"),
        "ranking_by_p95_latency": rank_generation_prompts_by_metric(configs, "p95_latency_ms", higher_is_better=False),
        "preliminary_generation_candidate": choose_generation_prompt_candidate(configs),
    }


def write_evaluation_reports(report: dict[str, Any], output_dir: Path | str) -> None:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "evaluation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (destination / "evaluation_report.md").write_text(render_markdown_report(report), encoding="utf-8")


def render_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        f"# W6 Evaluation report: {report.get('manifest_name')}",
        "",
        f"- Dataset: `{report.get('dataset_path')}`",
        f"- Dataset items: {report.get('dataset_item_count')}",
        f"- Configs: {report.get('config_count')}",
        f"- Judge backend: `{report.get('judge_backend')}`",
        f"- Started: {report.get('started_at')}",
        f"- Completed: {report.get('completed_at')}",
    ]
    if report.get("notes"):
        lines.append(f"- Notes: {report['notes']}")
    if report.get("judge_backend") != "gemini":
        lines.extend(
            [
                "",
                "> **Caveat:** This is not an official W6 metric run because RAGAS-like metrics were not judged by Gemini.",
            ]
        )
    lines.extend(
        [
            "",
            "> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.",
        ]
    )

    lines.extend(
        [
            "",
            "## Overall metrics",
            "",
            "| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for config in report.get("configs") or []:
        metrics = config.get("metrics") or {}
        lines.append(
            "| {name} | {status} | {items} | {faith} | {rel} | {recall} | {graph} | {cite} | {latency} | {retrieval} |".format(
                name=config.get("config_name"),
                status=config.get("status"),
                items=metrics.get("item_count"),
                faith=metrics.get("faithfulness_avg"),
                rel=metrics.get("answer_relevancy_avg"),
                recall=metrics.get("context_recall_avg"),
                graph=metrics.get("graph_hit_rate"),
                cite=metrics.get("citation_coverage_rate"),
                latency=metrics.get("p95_latency_ms"),
                retrieval=metrics.get("retrieval_p95_ms"),
            )
        )

    append_ablation_analysis(lines, report)
    append_chunking_ablation_analysis(lines, report)
    append_generation_prompt_ablation_analysis(lines, report)

    lines.extend(["", "## Metrics by question complexity", ""])
    append_grouped_metrics_table(lines, report, group_key="by_question_complexity")
    lines.extend(["", "## Metrics by question family", ""])
    append_grouped_metrics_table(lines, report, group_key="by_question_family")

    lines.extend(["", "## Per-question results", ""])
    for config in report.get("configs") or []:
        lines.extend(
            [
                f"### {config.get('config_name')}",
                "",
                "| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |",
                "|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for item in config.get("items") or []:
            lines.append(
                "| {item_id} | {status} | {complexity} | {family} | {chart_only} | {faith} | {rel} | {recall} | {graph} | {cite} | {sources} | {latency} | {error} |".format(
                    item_id=item.get("item_id"),
                    status=item.get("status"),
                    complexity=item.get("question_complexity") or "",
                    family=item.get("question_family") or "",
                    chart_only=item.get("chart_only"),
                    faith=item.get("faithfulness"),
                    rel=item.get("answer_relevancy"),
                    recall=item.get("context_recall"),
                    graph=item.get("graph_hit"),
                    cite=item.get("citation_coverage"),
                    sources=item.get("source_count"),
                    latency=item.get("latency_ms"),
                    error=item.get("error") or "",
                )
            )
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def append_ablation_analysis(lines: list[str], report: dict[str, Any]) -> None:
    analysis = report.get("ablation_analysis") or {}
    if not analysis:
        return
    recommendation = analysis.get("preliminary_recommendation") or {}
    lines.extend(
        [
            "",
            "## Ablation analysis",
            "",
            f"- Baseline config: `{analysis.get('baseline_config_name')}`",
            f"- Preliminary recommendation: `{recommendation.get('recommended_candidate')}`",
        ]
    )
    for reason in recommendation.get("reasoning") or []:
        lines.append(f"  - {reason}")

    ranking_specs = [
        ("ranking_by_context_recall", "Context recall ranking"),
        ("ranking_by_citation_coverage", "Citation coverage ranking"),
        ("ranking_by_graph_hit_rate", "Graph hit ranking"),
        ("ranking_by_p95_latency", "p95 latency ranking"),
    ]
    for key, title in ranking_specs:
        lines.extend(["", f"### {title}", "", "| Rank | Config | Value |", "|---:|---|---:|"])
        for index, item in enumerate(analysis.get(key) or [], start=1):
            lines.append(f"| {index} | {item.get('config_name')} | {item.get('value')} |")

    lines.extend(
        [
            "",
            "### Retrieval miss summary",
            "",
            "| Config | Miss count | Example item IDs |",
            "|---|---:|---|",
        ]
    )
    for summary in analysis.get("retrieval_miss_summary") or []:
        examples = ", ".join(str(example.get("item_id")) for example in summary.get("examples") or [])
        lines.append(f"| {summary.get('config_name')} | {summary.get('miss_count')} | {examples} |")

    lines.extend(
        [
            "",
            "### Rerank miss summary",
            "",
            "| Config | Miss count | Example item IDs |",
            "|---|---:|---|",
        ]
    )
    for summary in analysis.get("rerank_miss_summary") or []:
        examples = ", ".join(str(example.get("item_id")) for example in summary.get("examples") or [])
        lines.append(f"| {summary.get('config_name')} | {summary.get('miss_count')} | {examples} |")


def append_chunking_ablation_analysis(lines: list[str], report: dict[str, Any]) -> None:
    analysis = report.get("chunking_ablation_analysis") or {}
    if not analysis:
        return
    candidate = analysis.get("preliminary_chunking_candidate") or {}
    lines.extend(
        [
            "",
            "## Phân tích ablation chiến lược chunking",
            "",
            f"- Phạm vi: {analysis.get('scope_vi')}",
            f"- Ghi chú tên strategy: {analysis.get('semantic_strategy_note_vi')}",
            f"- Chính sách dense: {analysis.get('dense_policy_vi')}",
            f"- Các chiến lược được so sánh: `{', '.join(analysis.get('strategies') or [])}`",
            f"- Ứng viên chunking sơ bộ: `{candidate.get('recommended_chunk_strategy_id')}` qua config `{candidate.get('recommended_config_name')}`",
        ]
    )
    for reason in candidate.get("reasoning_vi") or []:
        lines.append(f"  - {reason}")

    ranking_specs = [
        ("ranking_by_context_recall", "Xếp hạng theo Context Recall"),
        ("ranking_by_citation_coverage", "Xếp hạng theo Citation Coverage"),
        ("ranking_by_graph_hit_rate", "Xếp hạng theo Graph Hit Rate"),
        ("ranking_by_p95_latency", "Xếp hạng theo p95 latency"),
    ]
    for key, title in ranking_specs:
        lines.extend(
            [
                "",
                f"### {title}",
                "",
                "| Hạng | Chunk strategy | Config | Giá trị |",
                "|---:|---|---|---:|",
            ]
        )
        for index, item in enumerate(analysis.get(key) or [], start=1):
            lines.append(
                f"| {index} | {item.get('chunk_strategy_id')} | {item.get('config_name')} | {item.get('value')} |"
            )


def append_generation_prompt_ablation_analysis(lines: list[str], report: dict[str, Any]) -> None:
    analysis = report.get("generation_prompt_ablation_analysis") or {}
    if not analysis:
        return
    candidate = analysis.get("preliminary_generation_candidate") or {}
    lines.extend(
        [
            "",
            "## Phân tích ablation generation prompt/model",
            "",
            f"- Phạm vi: {analysis.get('scope_vi')}",
            f"- Retrieval control: {analysis.get('retrieval_control_vi')}",
            f"- Chính sách run: {analysis.get('partial_run_policy_vi')}",
            f"- Prompt templates: `{', '.join(analysis.get('prompt_template_ids') or [])}`",
            f"- Generation models: `{', '.join(analysis.get('generation_models') or [])}`",
            f"- Ứng viên generation sơ bộ: prompt `{candidate.get('recommended_prompt_template_id')}` với model `{candidate.get('recommended_generation_model')}` qua config `{candidate.get('recommended_config_name')}`",
        ]
    )
    for reason in candidate.get("reasoning_vi") or []:
        lines.append(f"  - {reason}")

    ranking_specs = [
        ("ranking_by_faithfulness", "Xếp hạng theo Faithfulness"),
        ("ranking_by_answer_relevancy", "Xếp hạng theo Answer Relevancy"),
        ("ranking_by_citation_coverage", "Xếp hạng theo Citation Coverage"),
        ("ranking_by_p95_latency", "Xếp hạng theo p95 latency"),
    ]
    for key, title in ranking_specs:
        lines.extend(
            [
                "",
                f"### {title}",
                "",
                "| Hạng | Prompt template | Model | Config | Giá trị |",
                "|---:|---|---|---|---:|",
            ]
        )
        for index, item in enumerate(analysis.get(key) or [], start=1):
            lines.append(
                f"| {index} | {item.get('prompt_template_id')} | {item.get('generation_model')} | {item.get('config_name')} | {item.get('value')} |"
            )


def append_grouped_metrics_table(lines: list[str], report: dict[str, Any], *, group_key: str) -> None:
    lines.extend(
        [
            "| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for config in report.get("configs") or []:
        groups = ((config.get("grouped_metrics") or {}).get(group_key) or {})
        for group, metrics in groups.items():
            lines.append(
                "| {config} | {group} | {items} | {faith} | {rel} | {recall} | {graph} | {cite} | {latency} |".format(
                    config=config.get("config_name"),
                    group=group,
                    items=metrics.get("item_count"),
                    faith=metrics.get("faithfulness_avg"),
                    rel=metrics.get("answer_relevancy_avg"),
                    recall=metrics.get("context_recall_avg"),
                    graph=metrics.get("graph_hit_rate"),
                    cite=metrics.get("citation_coverage_rate"),
                    latency=metrics.get("p95_latency_ms"),
                )
            )


def build_single_config_manifest(
    *,
    dataset_path: Path,
    config_path: Path,
    output_dir: Path | None = None,
    name: str = "w6_eval_02_single_config",
) -> AblationManifest:
    resolved_dataset = dataset_path if dataset_path.is_absolute() else ROOT_DIR / dataset_path
    resolved_config = config_path if config_path.is_absolute() else ROOT_DIR / config_path
    return AblationManifest(
        name=name,
        dataset_path=resolved_dataset,
        output_dir=output_dir or DEFAULT_W6_EVAL_OUTPUT_DIR,
        configs=[AblationConfigSpec(name=resolved_config.stem, base_config_path=resolved_config)],
        notes="W6-EVAL-02 single-config evaluation run.",
    )


def make_evaluation_judge(*, backend: str, model: str = DEFAULT_JUDGE_MODEL) -> EvaluationJudge:
    if backend == "gemini":
        return GeminiEvaluationJudge(model=model)
    if backend == "static":
        return StaticEvaluationJudge()
    raise ValueError(f"Unsupported evaluation judge backend: {backend}")


__all__ = [
    "DEFAULT_JUDGE_MODEL",
    "DEFAULT_W6_EVAL_OUTPUT_DIR",
    "EvaluationJudge",
    "EvaluationJudgeResult",
    "EvaluationRunner",
    "GeminiEvaluationJudge",
    "NullExperimentRunStore",
    "StaticEvaluationJudge",
    "SupabaseExperimentRunStore",
    "aggregate_evaluation_metrics",
    "aggregate_grouped_metrics",
    "build_generation_prompt_ablation_analysis",
    "build_single_config_manifest",
    "load_ablation_manifest",
    "make_evaluation_judge",
    "make_evaluation_rag_runner",
    "render_markdown_report",
    "write_evaluation_reports",
]