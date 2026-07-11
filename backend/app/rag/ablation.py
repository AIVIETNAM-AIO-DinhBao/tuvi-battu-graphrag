from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Protocol

import yaml

from app.clients import get_supabase_client
from app.rag.config import ExperimentConfig, config_hash, load_experiment_config
from app.rag.generation import DeterministicGenerationClient
from app.rag.graph import run_rag_dry_run
from app.rag.rewrite import PassthroughQueryRewriter


ROOT_DIR = Path(__file__).resolve().parents[3]
ROOT_RELATIVE_PREFIXES = {
    "backend",
    "benchmark",
    "configs",
    "data",
    "docs",
    "frontend",
    "infra",
    "notebooks",
    "scripts",
}
CITATION_MARKER_RE = re.compile(r"\[(S\d+)\]")
TOKEN_RE = re.compile(r"\w+", re.UNICODE)
VIETNAMESE_STOPWORDS = {
    "a",
    "anh",
    "có",
    "của",
    "cũng",
    "cho",
    "đã",
    "được",
    "để",
    "điều",
    "do",
    "hay",
    "khi",
    "là",
    "lá",
    "này",
    "nên",
    "người",
    "những",
    "nói",
    "ở",
    "số",
    "sự",
    "tại",
    "thì",
    "trong",
    "và",
    "về",
    "với",
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def resolve_ablation_path(raw_path: str | Path, *, manifest_dir: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    if path.parts and path.parts[0] in ROOT_RELATIVE_PREFIXES:
        return ROOT_DIR / path
    return manifest_dir / path


def deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def tokenize(text: str | None, *, drop_stopwords: bool = False) -> list[str]:
    tokens = [token.lower() for token in TOKEN_RE.findall(text or "")]
    if drop_stopwords:
        return [token for token in tokens if token not in VIETNAMESE_STOPWORDS and len(token) > 1]
    return tokens


def token_recall(candidate: str | None, reference: str | None) -> float | None:
    reference_tokens = set(tokenize(reference, drop_stopwords=True))
    if not reference_tokens:
        return None
    candidate_tokens = set(tokenize(candidate, drop_stopwords=True))
    return round(len(candidate_tokens & reference_tokens) / len(reference_tokens), 4)


def char_ngram_similarity(candidate: str | None, reference: str | None, *, n: int = 3) -> float | None:
    def ngrams(text: str | None) -> set[str]:
        compact = re.sub(r"\s+", " ", (text or "").lower()).strip()
        if len(compact) < n:
            return {compact} if compact else set()
        return {compact[index : index + n] for index in range(len(compact) - n + 1)}

    left = ngrams(candidate)
    right = ngrams(reference)
    if not right:
        return None
    union = left | right
    if not union:
        return None
    return round(len(left & right) / len(union), 4)


def rouge_l_recall(candidate: str | None, reference: str | None, *, max_tokens: int = 256) -> float | None:
    candidate_tokens = tokenize(candidate)[:max_tokens]
    reference_tokens = tokenize(reference)[:max_tokens]
    if not reference_tokens:
        return None
    previous = [0] * (len(reference_tokens) + 1)
    for candidate_token in candidate_tokens:
        current = [0]
        for column, reference_token in enumerate(reference_tokens, start=1):
            if candidate_token == reference_token:
                current.append(previous[column - 1] + 1)
            else:
                current.append(max(previous[column], current[-1]))
        previous = current
    return round(previous[-1] / len(reference_tokens), 4)


def average_defined(values: list[float | int | None]) -> float | None:
    defined = [float(value) for value in values if value is not None]
    if not defined:
        return None
    return round(sum(defined) / len(defined), 4)


def bool_rate(values: list[bool]) -> float:
    if not values:
        return 0.0
    return round(sum(1 for value in values if value) / len(values), 4)


def source_doc_id(source: dict[str, Any]) -> str | None:
    provenance = source.get("provenance") if isinstance(source.get("provenance"), dict) else {}
    value = source.get("source_id") or provenance.get("source_id") or provenance.get("doc_id")
    return str(value) if value not in (None, "") else None


def source_page(source: dict[str, Any]) -> int | None:
    for key in ("source_page", "page_book", "page_pdf"):
        value = source.get(key)
        if value in (None, ""):
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def gold_doc_coverage_rate(sources: list[dict[str, Any]], gold_spans: list[dict[str, Any]]) -> float | None:
    gold_docs = {str(span.get("doc_id")) for span in gold_spans if span.get("doc_id")}
    if not gold_docs:
        return None
    source_docs = {doc_id for doc_id in (source_doc_id(source) for source in sources) if doc_id}
    return round(len(gold_docs & source_docs) / len(gold_docs), 4)


def gold_page_hit_rate(
    sources: list[dict[str, Any]],
    gold_spans: list[dict[str, Any]],
    *,
    tolerance: int = 1,
) -> float | None:
    gold_pairs: set[tuple[str, int]] = set()
    for span in gold_spans:
        doc_id = span.get("doc_id")
        if not doc_id:
            continue
        for key in ("page_book", "page_pdf"):
            value = span.get(key)
            if value in (None, ""):
                continue
            try:
                gold_pairs.add((str(doc_id), int(value)))
            except (TypeError, ValueError):
                continue
    if not gold_pairs:
        return None

    source_pairs = [
        (doc_id, page)
        for source in sources
        if (doc_id := source_doc_id(source)) and (page := source_page(source)) is not None
    ]
    hits = 0
    for gold_doc_id, gold_page in gold_pairs:
        if any(source_doc_id == gold_doc_id and abs(source_page_value - gold_page) <= tolerance for source_doc_id, source_page_value in source_pairs):
            hits += 1
    return round(hits / len(gold_pairs), 4)


def gold_quote_overlap_avg(sources: list[dict[str, Any]], gold_spans: list[dict[str, Any]]) -> float | None:
    quotes = [str(span.get("quote") or "") for span in gold_spans if str(span.get("quote") or "").strip()]
    if not quotes:
        return None
    excerpts = [str(source.get("excerpt") or source.get("text") or "") for source in sources]
    if not excerpts:
        return 0.0
    per_quote_scores: list[float] = []
    for quote in quotes:
        best = max((token_recall(excerpt, quote) or 0.0 for excerpt in excerpts), default=0.0)
        per_quote_scores.append(best)
    return average_defined(per_quote_scores)


def citation_source_alignment(markers: list[str], sources: list[dict[str, Any]]) -> bool:
    if not markers:
        return False
    source_markers = {str(source.get("citation_marker")) for source in sources if source.get("citation_marker")}
    return all(marker in source_markers for marker in markers)


@dataclass(frozen=True)
class AblationDatasetItem:
    id: str
    query: str
    chart_id: str
    user_id: str | None = None
    chart_data: dict[str, Any] | None = None
    gold_answer: str | None = None
    expected_answer_summary: str | None = None
    gold_context_spans: list[dict[str, Any]] = field(default_factory=list)
    labels: dict[str, Any] = field(default_factory=dict)
    question_complexity: str | None = None
    birth_info: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any], *, line_number: int) -> "AblationDatasetItem":
        item_id = str(payload.get("id") or f"item-{line_number:04d}").strip()
        query = str(payload.get("query") or payload.get("question") or "").strip()
        chart_id = str(payload.get("chart_id") or "").strip()
        if not query:
            raise ValueError(f"Ablation dataset line {line_number} requires a non-empty query.")
        if not chart_id:
            raise ValueError(f"Ablation dataset line {line_number} requires chart_id.")
        chart_data = payload.get("chart_data") or payload.get("chart_repr")
        if chart_data is not None and not isinstance(chart_data, dict):
            raise ValueError(
                f"Ablation dataset record {line_number} chart_data/chart_repr must be an object when provided."
            )
        gold_context_spans = payload.get("gold_context_spans") or payload.get("gold_spans") or []
        if not isinstance(gold_context_spans, list):
            raise ValueError(f"Ablation dataset record {line_number} gold_context_spans must be a list.")
        labels = payload.get("labels") or {}
        birth_info = payload.get("birth_info") or {}
        if not isinstance(labels, dict):
            raise ValueError(f"Ablation dataset record {line_number} labels must be an object when provided.")
        if not isinstance(birth_info, dict):
            raise ValueError(f"Ablation dataset record {line_number} birth_info must be an object when provided.")
        reserved = {
            "id",
            "query",
            "question",
            "chart_id",
            "user_id",
            "chart_data",
            "chart_repr",
            "gold_answer",
            "expected_answer_summary",
            "gold_context_spans",
            "gold_spans",
            "labels",
            "question_complexity",
            "birth_info",
            "metadata",
        }
        metadata = dict(payload.get("metadata") or {})
        metadata.update({key: value for key, value in payload.items() if key not in reserved})
        return cls(
            id=item_id,
            query=query,
            chart_id=chart_id,
            user_id=payload.get("user_id"),
            chart_data=chart_data,
            gold_answer=payload.get("gold_answer"),
            expected_answer_summary=payload.get("expected_answer_summary"),
            gold_context_spans=[span for span in gold_context_spans if isinstance(span, dict)],
            labels=labels,
            question_complexity=payload.get("question_complexity"),
            birth_info=birth_info,
            metadata=metadata,
        )


@dataclass(frozen=True)
class AblationConfigSpec:
    name: str
    base_config_path: Path
    overrides: dict[str, Any] = field(default_factory=dict)

    def build_config(self) -> ExperimentConfig:
        base_config = load_experiment_config(self.base_config_path)
        payload = deep_merge(base_config.model_dump(mode="json"), self.overrides)
        payload["cache_disabled"] = True
        payload["domain"] = "TUVI"
        return ExperimentConfig.model_validate(payload)


@dataclass(frozen=True)
class AblationManifest:
    name: str
    dataset_path: Path
    output_dir: Path
    configs: list[AblationConfigSpec]
    notes: str | None = None


def load_ablation_manifest(path: Path | str) -> AblationManifest:
    manifest_path = Path(path)
    if not manifest_path.is_absolute():
        manifest_path = ROOT_DIR / manifest_path
    payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Ablation manifest must be a YAML object: {manifest_path}")
    manifest_dir = manifest_path.parent
    config_specs: list[AblationConfigSpec] = []
    for index, raw_spec in enumerate(payload.get("configs") or [], start=1):
        if not isinstance(raw_spec, dict):
            raise ValueError(f"Ablation manifest config #{index} must be an object.")
        name = str(raw_spec.get("name") or f"config-{index}").strip()
        base_config_path = resolve_ablation_path(
            raw_spec.get("base_config_path") or "configs/default_production.yaml",
            manifest_dir=manifest_dir,
        )
        overrides = dict(raw_spec.get("overrides") or {})
        config_specs.append(AblationConfigSpec(name=name, base_config_path=base_config_path, overrides=overrides))
    if not config_specs:
        raise ValueError(f"Ablation manifest must include at least one config: {manifest_path}")
    return AblationManifest(
        name=str(payload.get("name") or manifest_path.stem),
        notes=payload.get("notes"),
        dataset_path=resolve_ablation_path(payload.get("dataset_path"), manifest_dir=manifest_dir),
        output_dir=resolve_ablation_path(
            payload.get("output_dir") or "benchmark/tuvi_golden_dataset/reports/w4_abl_01",
            manifest_dir=manifest_dir,
        ),
        configs=config_specs,
    )


def load_ablation_dataset(path: Path | str, *, limit: int | None = None) -> list[AblationDatasetItem]:
    dataset_path = Path(path)
    items: list[AblationDatasetItem] = []
    content = dataset_path.read_text(encoding="utf-8")
    decoder = json.JSONDecoder()
    offset = 0
    record_number = 0
    while offset < len(content):
        while offset < len(content) and content[offset].isspace():
            offset += 1
        if offset >= len(content):
            break
        payload, next_offset = decoder.raw_decode(content, offset)
        record_number += 1
        if not isinstance(payload, dict):
            raise ValueError(f"Ablation dataset record {record_number} must be a JSON object.")
        items.append(AblationDatasetItem.from_payload(payload, line_number=record_number))
        if limit is not None and len(items) >= limit:
            break
        offset = next_offset
    if not items:
        raise ValueError(f"Ablation dataset is empty: {dataset_path}")
    return items


class ExperimentRunStore(Protocol):
    def create_run(self, *, config: ExperimentConfig, manifest: AblationManifest, notes: str | None = None) -> str | None:
        ...

    def complete_run(self, run_id: str | None, *, metrics: dict[str, Any], trace: dict[str, Any]) -> None:
        ...

    def fail_run(
        self,
        run_id: str | None,
        *,
        metrics: dict[str, Any],
        trace: dict[str, Any],
        error: str,
    ) -> None:
        ...


class NullExperimentRunStore:
    def create_run(self, *, config: ExperimentConfig, manifest: AblationManifest, notes: str | None = None) -> str | None:
        return None

    def complete_run(self, run_id: str | None, *, metrics: dict[str, Any], trace: dict[str, Any]) -> None:
        return None

    def fail_run(
        self,
        run_id: str | None,
        *,
        metrics: dict[str, Any],
        trace: dict[str, Any],
        error: str,
    ) -> None:
        return None


class InMemoryExperimentRunStore:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def create_run(self, *, config: ExperimentConfig, manifest: AblationManifest, notes: str | None = None) -> str:
        run_id = f"memory-run-{len(self.rows) + 1}"
        row = build_experiment_run_payload(config=config, manifest=manifest, status="running", notes=notes)
        row["id"] = run_id
        self.rows.append(row)
        return run_id

    def complete_run(self, run_id: str | None, *, metrics: dict[str, Any], trace: dict[str, Any]) -> None:
        self._update(run_id, status="completed", metrics=metrics, trace=trace, error=None)

    def fail_run(
        self,
        run_id: str | None,
        *,
        metrics: dict[str, Any],
        trace: dict[str, Any],
        error: str,
    ) -> None:
        self._update(run_id, status="failed", metrics=metrics, trace=trace, error=error)

    def _update(
        self,
        run_id: str | None,
        *,
        status: str,
        metrics: dict[str, Any],
        trace: dict[str, Any],
        error: str | None,
    ) -> None:
        if run_id is None:
            return
        for row in self.rows:
            if row.get("id") == run_id:
                row.update(
                    {
                        "status": status,
                        "metrics": metrics,
                        "trace": trace,
                        "error": error,
                        "completed_at": utc_now(),
                    }
                )
                return
        raise KeyError(f"Unknown in-memory experiment run id: {run_id}")


class SupabaseExperimentRunStore:
    def __init__(self, client: Any | None = None) -> None:
        self.client = client or get_supabase_client()

    def create_run(self, *, config: ExperimentConfig, manifest: AblationManifest, notes: str | None = None) -> str | None:
        payload = build_experiment_run_payload(config=config, manifest=manifest, status="running", notes=notes)
        response = self.client.table("experiment_runs").insert(payload).execute()
        data = getattr(response, "data", None) or []
        if isinstance(data, list) and data:
            return data[0].get("id")
        if isinstance(data, dict):
            return data.get("id")
        return None

    def complete_run(self, run_id: str | None, *, metrics: dict[str, Any], trace: dict[str, Any]) -> None:
        self._update(run_id, {"status": "completed", "metrics": metrics, "trace": trace, "error": None, "completed_at": utc_now()})

    def fail_run(
        self,
        run_id: str | None,
        *,
        metrics: dict[str, Any],
        trace: dict[str, Any],
        error: str,
    ) -> None:
        self._update(run_id, {"status": "failed", "metrics": metrics, "trace": trace, "error": error, "completed_at": utc_now()})

    def _update(self, run_id: str | None, payload: dict[str, Any]) -> None:
        if run_id is None:
            return
        query = self.client.table("experiment_runs").update(payload)
        query = query.eq("id", run_id)
        query.execute()


def build_experiment_run_payload(
    *,
    config: ExperimentConfig,
    manifest: AblationManifest,
    status: str,
    notes: str | None = None,
) -> dict[str, Any]:
    return {
        "experiment_id": config.experiment_id,
        "config_name": config.name,
        "config_hash": config_hash(config),
        "config": config.model_dump(mode="json"),
        "status": status,
        "metrics": {},
        "trace": {"manifest_name": manifest.name, "dataset_path": str(manifest.dataset_path)},
        "notes": notes or manifest.notes,
        "error": None,
        "started_at": utc_now(),
        "completed_at": None,
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


class ZeroDenseEmbeddingService:
    def embed_query(self, text: str) -> list[float]:
        return [0.0] * 1024


RagRunCallable = Callable[[AblationDatasetItem, ExperimentConfig], dict[str, Any]]


def make_default_rag_runner(*, offline_smoke: bool = False) -> RagRunCallable:
    def run_item(item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
        initial_state: dict[str, Any] = {"chart_id": item.chart_id, "query": item.query}
        if item.user_id:
            initial_state["user_id"] = item.user_id

        chart_loader = None
        if item.chart_data is not None:
            chart_loader = lambda chart_id, user_id=None: {  # noqa: E731 - small per-item adapter
                "id": chart_id,
                "user_id": user_id,
                "chart_system": "TUVI",
                "chart_data": item.chart_data,
            }

        kwargs: dict[str, Any] = {"experiment_config": config, "chart_loader": chart_loader}
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
class AblationRunner:
    run_store: ExperimentRunStore = field(default_factory=NullExperimentRunStore)
    rag_runner: RagRunCallable = field(default_factory=make_default_rag_runner)
    fail_fast: bool = False
    write_reports: bool = True

    def run(self, manifest: AblationManifest, *, limit: int | None = None, output_dir: Path | None = None) -> dict[str, Any]:
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
                    metrics = aggregate_item_metrics(item_results, expected_item_count=len(items))
                    trace = build_config_trace(manifest=manifest, spec=spec, config=config, item_results=item_results)
                    self.run_store.fail_run(run_id, metrics=metrics, trace=trace, error=config_error)
                    raise

            metrics = aggregate_item_metrics(item_results, expected_item_count=len(items))
            trace = build_config_trace(manifest=manifest, spec=spec, config=config, item_results=item_results)
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
                    "fusion_method": config.fusion_method,
                    "context_assembly_strategy": config.context_assembly_strategy,
                    "run_id": run_id,
                    "status": status,
                    "started_at": config_started,
                    "completed_at": utc_now(),
                    "metrics": metrics,
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
            "configs": config_results,
        }
        if self.write_reports:
            write_ablation_reports(report, effective_output_dir)
        return report

    def _run_item(self, item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
        started = time.perf_counter()
        try:
            state = self.rag_runner(item, config)
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            return summarize_item_state(item, state, latency_ms=latency_ms)
        except Exception as exc:
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            result = summarize_item_error(item, exc, latency_ms=latency_ms)
            if self.fail_fast:
                raise
            return result


def summarize_item_state(item: AblationDatasetItem, state: dict[str, Any], *, latency_ms: float) -> dict[str, Any]:
    answer = state.get("answer") or ""
    sources = state.get("sources") or []
    citation_metadata = state.get("citation_metadata") or {}
    context_summary = state.get("context_summary") or {}
    trace_nodes = [
        {"node": node.get("node"), "status": node.get("status", "completed")}
        for node in (state.get("retrieval_trace") or {}).get("nodes", [])
    ]
    markers = list(dict.fromkeys(CITATION_MARKER_RE.findall(answer)))
    answer_recall_gold = token_recall(answer, item.gold_answer)
    answer_recall_summary = token_recall(answer, item.expected_answer_summary)
    summary_coverage_binary = answer_recall_summary is not None and answer_recall_summary >= 0.35
    doc_coverage = gold_doc_coverage_rate(sources, item.gold_context_spans)
    page_hit = gold_page_hit_rate(sources, item.gold_context_spans)
    quote_overlap = gold_quote_overlap_avg(sources, item.gold_context_spans)
    return {
        "item_id": item.id,
        "chart_id": item.chart_id,
        "query": item.query,
        "question_complexity": item.question_complexity,
        "labels": item.labels,
        "gold_span_count": len(item.gold_context_spans),
        "status": "completed",
        "latency_ms": latency_ms,
        "answer_present": bool(str(answer).strip()),
        "answer_length_chars": len(str(answer)),
        "answer_token_recall_vs_gold": answer_recall_gold,
        "answer_token_recall_vs_summary": answer_recall_summary,
        "summary_coverage_binary": summary_coverage_binary,
        "char_ngram_similarity_vs_summary": char_ngram_similarity(answer, item.expected_answer_summary),
        "rouge_l_like_vs_summary": rouge_l_recall(answer, item.expected_answer_summary),
        "source_count": len(sources),
        "citation_marker_count": len(markers),
        "citation_marker_presence": bool(markers),
        "citation_source_alignment": citation_source_alignment(markers, sources),
        "citation_fallback": bool(citation_metadata.get("citation_fallback")),
        "context_selected_count": int(context_summary.get("selected_count") or 0),
        "gold_doc_coverage_rate": doc_coverage,
        "gold_page_hit_rate": page_hit,
        "gold_quote_overlap_avg": quote_overlap,
        "trace_node_statuses": trace_nodes,
        "error": None,
    }


def summarize_item_error(item: AblationDatasetItem, exc: Exception, *, latency_ms: float) -> dict[str, Any]:
    return {
        "item_id": item.id,
        "chart_id": item.chart_id,
        "query": item.query,
        "question_complexity": item.question_complexity,
        "labels": item.labels,
        "gold_span_count": len(item.gold_context_spans),
        "status": "failed",
        "latency_ms": latency_ms,
        "answer_present": False,
        "answer_length_chars": 0,
        "answer_token_recall_vs_gold": None,
        "answer_token_recall_vs_summary": None,
        "summary_coverage_binary": False,
        "char_ngram_similarity_vs_summary": None,
        "rouge_l_like_vs_summary": None,
        "source_count": 0,
        "citation_marker_count": 0,
        "citation_marker_presence": False,
        "citation_source_alignment": False,
        "citation_fallback": False,
        "context_selected_count": 0,
        "gold_doc_coverage_rate": None,
        "gold_page_hit_rate": None,
        "gold_quote_overlap_avg": None,
        "trace_node_statuses": [],
        "error": f"{type(exc).__name__}: {exc}",
    }


def aggregate_item_metrics(item_results: list[dict[str, Any]], *, expected_item_count: int | None = None) -> dict[str, Any]:
    item_count = expected_item_count if expected_item_count is not None else len(item_results)
    completed = [item for item in item_results if item.get("status") == "completed"]
    failed_count = item_count - len(completed)
    denominator = item_count or 1
    return {
        "item_count": item_count,
        "completed_count": len(completed),
        "failed_count": failed_count,
        "answer_present_rate": round(sum(1 for item in item_results if item.get("answer_present")) / denominator, 4),
        "avg_answer_length_chars": round(sum(float(item.get("answer_length_chars") or 0) for item in item_results) / denominator, 2),
        "avg_answer_token_recall_vs_gold": average_defined(
            [item.get("answer_token_recall_vs_gold") for item in item_results]
        ),
        "avg_answer_token_recall_vs_summary": average_defined(
            [item.get("answer_token_recall_vs_summary") for item in item_results]
        ),
        "summary_coverage_rate": round(
            sum(1 for item in item_results if item.get("summary_coverage_binary")) / denominator,
            4,
        ),
        "avg_char_ngram_similarity_vs_summary": average_defined(
            [item.get("char_ngram_similarity_vs_summary") for item in item_results]
        ),
        "avg_rouge_l_like_vs_summary": average_defined(
            [item.get("rouge_l_like_vs_summary") for item in item_results]
        ),
        "source_coverage_rate": round(sum(1 for item in item_results if item.get("source_count", 0) > 0) / denominator, 4),
        "avg_source_count": round(sum(float(item.get("source_count") or 0) for item in item_results) / denominator, 4),
        "avg_gold_doc_coverage_rate": average_defined([item.get("gold_doc_coverage_rate") for item in item_results]),
        "avg_gold_page_hit_rate": average_defined([item.get("gold_page_hit_rate") for item in item_results]),
        "avg_gold_quote_overlap": average_defined([item.get("gold_quote_overlap_avg") for item in item_results]),
        "citation_marker_presence_rate": round(
            sum(1 for item in item_results if item.get("citation_marker_presence")) / denominator,
            4,
        ),
        "citation_source_alignment_rate": round(
            sum(1 for item in item_results if item.get("citation_source_alignment")) / denominator,
            4,
        ),
        "avg_latency_ms": round(sum(float(item.get("latency_ms") or 0) for item in item_results) / denominator, 2),
        "citation_fallback_count": sum(1 for item in item_results if item.get("citation_fallback")),
        "context_selected_count_avg": round(
            sum(float(item.get("context_selected_count") or 0) for item in item_results) / denominator,
            4,
        ),
    }


def build_config_trace(
    *,
    manifest: AblationManifest,
    spec: AblationConfigSpec,
    config: ExperimentConfig,
    item_results: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "manifest_name": manifest.name,
        "dataset_path": str(manifest.dataset_path),
        "config_spec_name": spec.name,
        "experiment_id": config.experiment_id,
        "config_hash": config_hash(config),
        "chunk_strategy_id": config.chunk_strategy_id,
        "items": item_results,
    }


def write_ablation_reports(report: dict[str, Any], output_dir: Path | str) -> None:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "ablation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (destination / "ablation_report.md").write_text(render_markdown_report(report), encoding="utf-8")


def render_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        f"# Ablation report: {report.get('manifest_name')}",
        "",
        f"- Dataset: `{report.get('dataset_path')}`",
        f"- Dataset items: {report.get('dataset_item_count')}",
        f"- Configs: {report.get('config_count')}",
        f"- Started: {report.get('started_at')}",
        f"- Completed: {report.get('completed_at')}",
    ]
    if report.get("notes"):
        lines.extend([f"- Notes: {report['notes']}"])
    lines.extend(
        [
            "",
            "## Config summary",
            "",
            "| Config | Status | Items | Answer rate | Source coverage | Avg sources | Avg latency ms |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for config in report.get("configs") or []:
        metrics = config.get("metrics") or {}
        lines.append(
            "| {name} | {status} | {items} | {answer_rate} | {source_rate} | {avg_sources} | {latency} |".format(
                name=config.get("config_name"),
                status=config.get("status"),
                items=metrics.get("item_count"),
                answer_rate=metrics.get("answer_present_rate"),
                source_rate=metrics.get("source_coverage_rate"),
                avg_sources=metrics.get("avg_source_count"),
                latency=metrics.get("avg_latency_ms"),
            )
        )
    lines.extend(
        [
            "",
            "## Golden answer metrics",
            "",
            "| Config | Avg recall vs gold | Avg recall vs summary | Summary coverage | Avg char ngram sim | Avg ROUGE-L-like |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for config in report.get("configs") or []:
        metrics = config.get("metrics") or {}
        lines.append(
            "| {name} | {gold_recall} | {summary_recall} | {summary_coverage} | {char_sim} | {rouge_l} |".format(
                name=config.get("config_name"),
                gold_recall=metrics.get("avg_answer_token_recall_vs_gold"),
                summary_recall=metrics.get("avg_answer_token_recall_vs_summary"),
                summary_coverage=metrics.get("summary_coverage_rate"),
                char_sim=metrics.get("avg_char_ngram_similarity_vs_summary"),
                rouge_l=metrics.get("avg_rouge_l_like_vs_summary"),
            )
        )
    lines.extend(
        [
            "",
            "## Gold context and citation metrics",
            "",
            "| Config | Gold doc coverage | Gold page hit | Gold quote overlap | Citation marker presence | Citation source alignment |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for config in report.get("configs") or []:
        metrics = config.get("metrics") or {}
        lines.append(
            "| {name} | {doc_coverage} | {page_hit} | {quote_overlap} | {marker_presence} | {alignment} |".format(
                name=config.get("config_name"),
                doc_coverage=metrics.get("avg_gold_doc_coverage_rate"),
                page_hit=metrics.get("avg_gold_page_hit_rate"),
                quote_overlap=metrics.get("avg_gold_quote_overlap"),
                marker_presence=metrics.get("citation_marker_presence_rate"),
                alignment=metrics.get("citation_source_alignment_rate"),
            )
        )
    lines.extend(["", "## Per-question results", ""])
    for config in report.get("configs") or []:
        lines.extend(
            [
                f"### {config.get('config_name')}",
                "",
                "| Item | Status | Complexity | Gold spans | Sources | Summary recall | Doc coverage | Page hit | Citation markers | Context chunks | Latency ms | Error |",
                "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for item in config.get("items") or []:
            lines.append(
                "| {item_id} | {status} | {complexity} | {gold_spans} | {sources} | {summary_recall} | {doc_coverage} | {page_hit} | {markers} | {contexts} | {latency} | {error} |".format(
                    item_id=item.get("item_id"),
                    status=item.get("status"),
                    complexity=item.get("question_complexity") or "",
                    gold_spans=item.get("gold_span_count"),
                    sources=item.get("source_count"),
                    summary_recall=item.get("answer_token_recall_vs_summary"),
                    doc_coverage=item.get("gold_doc_coverage_rate"),
                    page_hit=item.get("gold_page_hit_rate"),
                    markers=item.get("citation_marker_count"),
                    contexts=item.get("context_selected_count"),
                    latency=item.get("latency_ms"),
                    error=(item.get("error") or ""),
                )
            )
        lines.append("")
    return "\n".join(lines).strip() + "\n"


__all__ = [
    "AblationConfigSpec",
    "AblationDatasetItem",
    "AblationManifest",
    "AblationRunner",
    "ExperimentRunStore",
    "InMemoryExperimentRunStore",
    "NullExperimentRunStore",
    "SupabaseExperimentRunStore",
    "aggregate_item_metrics",
    "build_experiment_run_payload",
    "load_ablation_dataset",
    "load_ablation_manifest",
    "make_default_rag_runner",
    "render_markdown_report",
    "write_ablation_reports",
]