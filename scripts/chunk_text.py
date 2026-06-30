"""Strategy-aware chunk generation for W3-INGEST-02/03.

The script reads canonical cleaned corpus files and emits deterministic JSONL
chunks with strategy metadata for official baseline and auxiliary ablation
strategies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import time
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

from gemini_keys import is_daily_quota_error, is_rate_limit_error, load_gemini_api_keys


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = ROOT_DIR / "configs" / "chunking_strategies.yaml"
DEFAULT_CORPUS_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "corpus"
DEFAULT_SOURCE_REGISTRY = (
    ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "guideline" / "source_registry.json"
)
DEFAULT_CHUNK_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "chunks"
STRATEGY_PARENT_CHILD = "chunk_structure_parent_child"
FIXED_STRATEGIES = {"chunk_fixed_256", "chunk_fixed_512", "chunk_fixed_1024"}
STRATEGY_SENTENCE_MERGE = "chunk_sentence_merge"
STRATEGY_SEMANTIC_EMBEDDING = "chunk_semantic_embedding"
STRATEGY_SEMANTIC = "chunk_semantic"
MOCK_SEMANTIC_EMBEDDING_DIM = 64

TOKEN_RE = re.compile(r"\S+")
SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?…])\s+")
DOMAIN_MAP = {
    "tu_vi": "TUVI",
    "tuvi": "TUVI",
    "tử vi": "TUVI",
}


@dataclass(frozen=True)
class SourceUnit:
    doc_id: str
    section_id: str
    text: str
    source_name: str
    source_page: int | None
    domain: str
    input_format: str
    page_pdf_start: int | None
    page_pdf_end: int | None
    page_book: int | None
    metadata: dict[str, Any]


@dataclass(frozen=True)
class Atom:
    text: str
    start: int
    end: int
    token_count: int


@dataclass(frozen=True)
class SemanticWindow:
    unit: SourceUnit
    atoms: list[Atom]
    break_score: float | None
    break_reason: str


@dataclass(frozen=True)
class SemanticSimilarityEvent:
    doc_id: str
    section_id: str
    atom_index: int
    similarity: float
    current_tokens: int
    next_atom_tokens: int
    break_reason: str | None


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")


def count_tokens(text: str) -> int:
    return len(TOKEN_RE.findall(text))


def canonical_token(token: str) -> str:
    return re.sub(r"^\W+|\W+$", "", token, flags=re.UNICODE).casefold()


def load_chunking_config(path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Chunking config does not exist: {path}")
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    if "strategies" not in config or not isinstance(config["strategies"], dict):
        raise ValueError("Chunking config must define a 'strategies' mapping.")
    if "default_strategy" not in config:
        raise ValueError("Chunking config must define 'default_strategy'.")
    return config


def get_strategy_config(config: dict[str, Any], strategy_id: str) -> dict[str, Any]:
    strategies = config.get("strategies", {})
    if strategy_id not in strategies:
        known = ", ".join(sorted(strategies))
        raise ValueError(f"Unknown chunking strategy '{strategy_id}'. Known strategies: {known}")

    strategy = strategies[strategy_id]
    if not strategy.get("implemented", False):
        raise NotImplementedError(
            f"Chunking strategy '{strategy_id}' is configured but not implemented in W3-INGEST-02."
        )
    return strategy


def flatten_protected_terms(config: dict[str, Any]) -> list[str]:
    terms: list[str] = []
    for values in (config.get("protected_terms") or {}).values():
        if isinstance(values, list):
            terms.extend(str(value) for value in values if str(value).strip())

    unique = {unicodedata.normalize("NFC", term.strip()): None for term in terms}
    return sorted(unique, key=lambda item: (count_tokens(item), len(item)), reverse=True)


def load_source_registry(path: Path = DEFAULT_SOURCE_REGISTRY) -> dict[str, dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Source registry does not exist: {path}")
    with path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)
    return {record["doc_id"]: record for record in records}


def normalize_domain(value: str | None) -> str:
    if not value:
        return "TUVI"
    normalized = unicodedata.normalize("NFC", value).strip().casefold()
    domain = DOMAIN_MAP.get(normalized, value.strip().upper())
    if domain != "TUVI":
        raise ValueError(f"Unsupported corpus domain for Tử Vi-only scope: {value}")
    return domain


def discover_input_files(inputs: Iterable[Path] | None = None) -> list[Path]:
    paths = list(inputs or [DEFAULT_CORPUS_DIR])
    discovered: list[Path] = []

    for path in paths:
        if not path.exists():
            hint = ""
            if path.name.casefold() == "thnl_clean.json":
                hint = " Did you mean TVNL_clean.json?"
            raise FileNotFoundError(f"Input path does not exist: {path}.{hint}")

        if path.is_dir():
            clean_files = sorted(path.rglob("*_clean.json"))
            if clean_files:
                discovered.extend(clean_files)
                continue
            discovered.extend(sorted(path.rglob("*_sections.jsonl")))
            continue

        if path.suffix.lower() not in {".json", ".jsonl"}:
            raise ValueError(f"Unsupported input file type: {path}")
        discovered.append(path)

    unique: dict[Path, None] = {}
    for path in discovered:
        unique[path.resolve()] = None
    return sorted(unique)


def load_source_units(path: Path, registry: dict[str, dict[str, Any]]) -> list[SourceUnit]:
    if path.suffix.lower() == ".jsonl":
        return load_sections_jsonl(path, registry)
    return load_clean_json(path, registry)


def load_clean_json(path: Path, registry: dict[str, dict[str, Any]]) -> list[SourceUnit]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"Clean JSON must contain a list of records: {path}")

    units: list[SourceUnit] = []
    for index, record in enumerate(data, start=1):
        text = normalize_text(str(record.get("content") or ""))
        if not text.strip():
            continue

        doc_id = str(record.get("doc_id") or path.stem.split("_")[0])
        source = registry.get(doc_id, {})
        metadata = dict(record.get("metadata") or {})
        page_pdf = as_optional_int(metadata.get("page_pdf"))
        page_book = as_optional_int(metadata.get("page_book"))

        units.append(
            SourceUnit(
                doc_id=doc_id,
                section_id=str(record.get("section_id") or f"{doc_id}_SEC_{index:06d}"),
                text=text,
                source_name=str(source.get("title") or doc_id),
                source_page=page_book if page_book is not None else page_pdf,
                domain=normalize_domain(source.get("domain")),
                input_format="clean_json",
                page_pdf_start=page_pdf,
                page_pdf_end=page_pdf,
                page_book=page_book,
                metadata=metadata,
            )
        )
    return units


def load_sections_jsonl(path: Path, registry: dict[str, dict[str, Any]]) -> list[SourceUnit]:
    units: list[SourceUnit] = []
    with path.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            text = normalize_text(str(record.get("content_text") or record.get("content") or ""))
            if not text.strip():
                continue

            doc_id = str(record.get("doc_id") or path.stem.split("_")[0])
            source = registry.get(doc_id, {})
            metadata = dict(record.get("metadata") or {})
            page_pdf_start = as_optional_int(metadata.get("page_pdf_start"))
            page_pdf_end = as_optional_int(metadata.get("page_pdf_end")) or page_pdf_start

            units.append(
                SourceUnit(
                    doc_id=doc_id,
                    section_id=str(record.get("section_id") or f"{doc_id}_SEC_{index:06d}"),
                    text=text,
                    source_name=str(source.get("title") or doc_id),
                    source_page=page_pdf_start,
                    domain=normalize_domain(source.get("domain")),
                    input_format="sections_jsonl",
                    page_pdf_start=page_pdf_start,
                    page_pdf_end=page_pdf_end,
                    page_book=None,
                    metadata=metadata,
                )
            )
    return units


def as_optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def strip_with_span(text: str, absolute_start: int) -> tuple[str, int, int]:
    left = len(text) - len(text.lstrip())
    right = len(text.rstrip())
    return text[left:right], absolute_start + left, absolute_start + right


def atomize_text(text: str, protected_terms: list[str], max_tokens: int) -> list[Atom]:
    atoms: list[Atom] = []
    normalized = normalize_text(text)

    for paragraph_match in re.finditer(r"\S(?:.*?\S)?(?=\s*(?:\n\s*\n|\Z))", normalized, flags=re.S):
        paragraph = paragraph_match.group(0)
        paragraph_start = paragraph_match.start()
        line_matches = list(re.finditer(r"[^\n]+", paragraph))

        if len(line_matches) > 1:
            for line_match in line_matches:
                line = line_match.group(0)
                if line.strip():
                    atoms.extend(
                        sentence_atoms(
                            line,
                            paragraph_start + line_match.start(),
                            protected_terms,
                            max_tokens,
                        )
                    )
        else:
            atoms.extend(sentence_atoms(paragraph, paragraph_start, protected_terms, max_tokens))

    return [atom for atom in atoms if atom.text.strip()]


def sentence_atoms(
    text: str,
    absolute_start: int,
    protected_terms: list[str],
    max_tokens: int,
) -> list[Atom]:
    atoms: list[Atom] = []
    start = 0

    for boundary in SENTENCE_BOUNDARY_RE.finditer(text):
        segment = text[start : boundary.start()]
        atoms.extend(make_atoms_from_segment(segment, absolute_start + start, protected_terms, max_tokens))
        start = boundary.end()

    atoms.extend(make_atoms_from_segment(text[start:], absolute_start + start, protected_terms, max_tokens))
    return atoms


def make_atoms_from_segment(
    segment: str,
    absolute_start: int,
    protected_terms: list[str],
    max_tokens: int,
) -> list[Atom]:
    stripped, start, end = strip_with_span(segment, absolute_start)
    if not stripped:
        return []

    token_count = count_tokens(stripped)
    if token_count <= max_tokens:
        return [Atom(text=stripped, start=start, end=end, token_count=token_count)]

    return split_long_segment(stripped, start, protected_terms, max_tokens)


def split_long_segment(
    segment: str,
    absolute_start: int,
    protected_terms: list[str],
    max_tokens: int,
) -> list[Atom]:
    token_matches = list(TOKEN_RE.finditer(segment))
    if not token_matches:
        return []

    protected_spans = find_protected_token_spans(
        [match.group(0) for match in token_matches], protected_terms
    )
    atoms: list[Atom] = []
    start_index = 0

    while start_index < len(token_matches):
        end_index = min(start_index + max_tokens, len(token_matches))
        adjusted_end = adjust_token_boundary(start_index, end_index, protected_spans)
        if adjusted_end <= start_index:
            adjusted_end = end_index

        char_start = token_matches[start_index].start()
        char_end = token_matches[adjusted_end - 1].end()
        part = segment[char_start:char_end].strip()
        if part:
            atoms.append(
                Atom(
                    text=part,
                    start=absolute_start + char_start,
                    end=absolute_start + char_end,
                    token_count=adjusted_end - start_index,
                )
            )
        start_index = adjusted_end

    return atoms


def find_protected_token_spans(tokens: list[str], protected_terms: list[str]) -> list[tuple[int, int]]:
    normalized_tokens = [canonical_token(token) for token in tokens]
    protected_sequences = [
        [canonical_token(token) for token in TOKEN_RE.findall(term) if canonical_token(token)]
        for term in protected_terms
    ]
    spans: list[tuple[int, int]] = []

    for sequence in protected_sequences:
        if not sequence:
            continue
        width = len(sequence)
        for index in range(0, len(normalized_tokens) - width + 1):
            if normalized_tokens[index : index + width] == sequence:
                spans.append((index, index + width))
    return spans


def adjust_token_boundary(
    start_index: int,
    end_index: int,
    protected_spans: list[tuple[int, int]],
) -> int:
    for protected_start, protected_end in protected_spans:
        if protected_start < end_index < protected_end:
            if protected_start > start_index:
                return protected_start
            return protected_end
    return end_index


def select_overlap_atoms(atoms: list[Atom], overlap_tokens: int) -> list[Atom]:
    if overlap_tokens <= 0:
        return []

    selected: list[Atom] = []
    total = 0
    for atom in reversed(atoms):
        selected.append(atom)
        total += atom.token_count
        if total >= overlap_tokens:
            break
    return list(reversed(selected))


def build_token_windows(
    atoms: list[Atom],
    *,
    min_tokens: int,
    max_tokens: int,
    overlap_tokens: int,
) -> list[list[Atom]]:
    windows: list[list[Atom]] = []
    current: list[Atom] = []
    current_tokens = 0
    added_since_emit = False

    def emit_current() -> None:
        nonlocal current, current_tokens, added_since_emit
        if current:
            windows.append(list(current))
            current = select_overlap_atoms(current, overlap_tokens)
            current_tokens = sum(atom.token_count for atom in current)
            added_since_emit = False

    for atom in atoms:
        if current and current_tokens + atom.token_count > max_tokens and current_tokens >= min_tokens:
            emit_current()

        if current and current_tokens + atom.token_count > max_tokens:
            if added_since_emit:
                emit_current()
            else:
                current = []
                current_tokens = 0

        current.append(atom)
        current_tokens += atom.token_count
        added_since_emit = True

        if current_tokens >= max_tokens:
            emit_current()

    if current and added_since_emit:
        windows.append(list(current))

    return windows


def chunk_text_from_atoms(atoms: list[Atom]) -> str:
    text = " ".join(atom.text.strip() for atom in atoms if atom.text.strip())
    return re.sub(r"[ \t]+", " ", text).strip()


def find_preserved_entities(text: str, protected_terms: list[str]) -> list[str]:
    text_casefold = text.casefold()
    found = [term for term in protected_terms if term.casefold() in text_casefold]
    return sorted(set(found), key=lambda item: (item.casefold(), item))


def normalized_token_set(text: str) -> set[str]:
    return {
        token
        for token in (canonical_token(match.group(0)) for match in TOKEN_RE.finditer(text))
        if token
    }


def lexical_similarity(left: str, right: str) -> float:
    left_tokens = normalized_token_set(left)
    right_tokens = normalized_token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def normalize_vector(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return [0.0 for _ in vector]
    return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError(f"Vector dimension mismatch: {len(left)} != {len(right)}")
    left_norm = normalize_vector(left)
    right_norm = normalize_vector(right)
    return sum(a * b for a, b in zip(left_norm, right_norm, strict=True))


def centroid(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        return []
    dimension = len(vectors[0])
    sums = [0.0] * dimension
    for vector in vectors:
        if len(vector) != dimension:
            raise ValueError("Cannot build centroid from vectors with different dimensions.")
        for index, value in enumerate(vector):
            sums[index] += value
    return [value / len(vectors) for value in sums]


class MockSemanticEmbeddingClient:
    """Deterministic lexical-hash embedding client for offline tests and smoke runs."""

    def __init__(self, dimension: int = MOCK_SEMANTIC_EMBEDDING_DIM) -> None:
        self.model_name = f"mock-semantic-hash-{dimension}"
        self.dimension = dimension

    def embed_document(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        tokens = sorted(normalized_token_set(text))
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign
        return normalize_vector(vector)


class GeminiSemanticEmbeddingClient:
    def __init__(self, api_key: str | None, model_name: str, output_dimensionality: int) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required unless --mock-embedding is used.")
        try:
            from google import genai  # type: ignore[import-not-found]
            from google.genai import types  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("google-genai is not installed. Install backend dependencies or use --mock-embedding.") from exc
        self._client = genai.Client(api_key=api_key)
        self._types = types
        self.model_name = model_name
        self.output_dimensionality = output_dimensionality

    def embed_document(self, text: str) -> list[float]:
        response = self._client.models.embed_content(
            model=self.model_name,
            contents=text,
            config=self._types.EmbedContentConfig(output_dimensionality=self.output_dimensionality),
        )
        embeddings = getattr(response, "embeddings", None)
        if not embeddings:
            raise ValueError("Embedding response does not contain embeddings.")
        values = getattr(embeddings[0], "values", None)
        if not isinstance(values, list):
            raise ValueError("Embedding response does not contain embedding values.")
        return [float(value) for value in values]


class MultiKeyGeminiSemanticEmbeddingClient:
    def __init__(
        self,
        clients: list[Any],
        *,
        max_retries: int = 6,
        retry_base_seconds: float = 10.0,
        max_retry_sleep_seconds: float = 300.0,
        stop_on_daily_quota: bool = True,
        sleep_fn: Any = time.sleep,
        time_fn: Any = time.monotonic,
    ) -> None:
        if not clients:
            raise ValueError("GEMINI_API_KEYS or GEMINI_API_KEY is required unless --mock-embedding is used.")
        self.clients = clients
        self.model_name = str(getattr(clients[0], "model_name", "gemini-embedding-2"))
        self.max_retries = max(0, max_retries)
        self.retry_base_seconds = max(0.0, retry_base_seconds)
        self.max_retry_sleep_seconds = max(0.0, max_retry_sleep_seconds)
        self.stop_on_daily_quota = stop_on_daily_quota
        self._sleep = sleep_fn
        self._time = time_fn
        self._cursor = 0
        self._disabled = [False for _ in clients]
        self._available_after = [0.0 for _ in clients]
        self._rate_limit_attempts = [0 for _ in clients]
        self.api_key_usage_counts = {self._key_label(index): 0 for index in range(len(clients))}
        self.quota_failover_count = 0

    @property
    def api_key_count(self) -> int:
        return len(self.clients)

    @property
    def disabled_key_count(self) -> int:
        return sum(1 for disabled in self._disabled if disabled)

    def get_usage_summary(self) -> dict[str, Any]:
        return {
            "api_key_count": self.api_key_count,
            "api_key_usage_counts": dict(self.api_key_usage_counts),
            "disabled_key_count": self.disabled_key_count,
            "quota_failover_count": self.quota_failover_count,
        }

    def _key_label(self, index: int) -> str:
        return f"key_{index + 1}"

    def _next_available_index(self) -> int:
        if all(self._disabled):
            raise RuntimeError("All Gemini API keys are unavailable for this run.")

        while True:
            now = self._time()
            next_available_time: float | None = None
            for offset in range(len(self.clients)):
                index = (self._cursor + offset) % len(self.clients)
                if self._disabled[index]:
                    continue
                available_at = self._available_after[index]
                if available_at <= now:
                    self._cursor = (index + 1) % len(self.clients)
                    return index
                if next_available_time is None or available_at < next_available_time:
                    next_available_time = available_at

            if next_available_time is None:
                raise RuntimeError("All Gemini API keys are unavailable for this run.")
            self._sleep(max(0.0, next_available_time - now))

    def _sleep_for_rate_limit(self, index: int) -> None:
        attempt = self._rate_limit_attempts[index]
        if attempt >= self.max_retries:
            self._disabled[index] = True
            return
        sleep_for = min(self.max_retry_sleep_seconds, self.retry_base_seconds * (2**attempt))
        self._rate_limit_attempts[index] += 1
        self._available_after[index] = self._time() + sleep_for

    def embed_document(self, text: str) -> list[float]:
        while True:
            index = self._next_available_index()
            client = self.clients[index]
            label = self._key_label(index)
            try:
                vector = client.embed_document(text)
                self._rate_limit_attempts[index] = 0
                self.api_key_usage_counts[label] += 1
                return vector
            except Exception as exc:
                if self.stop_on_daily_quota and is_daily_quota_error(exc):
                    self._disabled[index] = True
                    self.quota_failover_count += 1
                    print(
                        f"Daily quota exhausted for Gemini API {label}; trying another key.",
                        file=sys.stderr,
                        flush=True,
                    )
                    continue
                if is_rate_limit_error(exc):
                    self.quota_failover_count += 1
                    self._sleep_for_rate_limit(index)
                    print(
                        f"Rate limit for Gemini API {label}; trying another key.",
                        file=sys.stderr,
                        flush=True,
                    )
                    continue
                raise


def make_semantic_embedding_client(strategy: dict[str, Any], *, mock_embedding: bool) -> Any:
    if mock_embedding:
        return MockSemanticEmbeddingClient()
    model_name = str(strategy.get("embedding_model_for_chunking") or "gemini-embedding-2")
    output_dimensionality = int(strategy.get("output_dimensionality") or 768)
    clients = [
        GeminiSemanticEmbeddingClient(api_key, model_name, output_dimensionality)
        for api_key in load_gemini_api_keys()
    ]
    return MultiKeyGeminiSemanticEmbeddingClient(clients)


def make_chunk_hash(
    *,
    chunk_strategy_id: str,
    chunking_version: str,
    config_version: str,
    chunk_type: str,
    doc_id: str,
    section_id: str,
    source_page: int | None,
    char_start: int,
    char_end: int,
    chunk_text: str,
) -> str:
    payload = {
        "char_end": char_end,
        "char_start": char_start,
        "chunk_strategy_id": chunk_strategy_id,
        "chunk_text": chunk_text,
        "chunk_type": chunk_type,
        "chunking_version": chunking_version,
        "config_version": config_version,
        "doc_id": doc_id,
        "section_id": section_id,
        "source_page": source_page,
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def make_chunk_record(
    *,
    unit: SourceUnit,
    atoms: list[Atom],
    chunk_type: str,
    running_no: int,
    parent_id: str | None,
    chunk_strategy_id: str,
    chunking_version: str,
    config_version: str,
    strategy_snapshot: dict[str, Any],
    protected_terms: list[str],
    extra_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    chunk_text = chunk_text_from_atoms(atoms)
    char_start = min(atom.start for atom in atoms)
    char_end = max(atom.end for atom in atoms)
    token_count = count_tokens(chunk_text)
    chunk_id = f"{unit.doc_id}_{chunk_strategy_id}_{chunk_type}_{running_no:06d}"
    provenance = {
        "char_end": char_end,
        "char_start": char_start,
        "input_format": unit.input_format,
        "page_book": unit.page_book,
        "page_pdf_end": unit.page_pdf_end,
        "page_pdf_start": unit.page_pdf_start,
        "section_id": unit.section_id,
        "source_id": unit.doc_id,
        "source_name": unit.source_name,
        "source_page": unit.source_page,
    }

    record = {
        "chunk_id": chunk_id,
        "parent_id": parent_id,
        "chunk_type": chunk_type,
        "chunk_text": chunk_text,
        "text": chunk_text,
        "source_id": unit.doc_id,
        "source_name": unit.source_name,
        "source_page": unit.source_page,
        "domain": unit.domain,
        "chunk_strategy_id": chunk_strategy_id,
        "chunk_hash": "",
        "provenance": provenance,
        "metadata": {
            "char_end": char_end,
            "char_start": char_start,
            "chunk_strategy_id": chunk_strategy_id,
            "chunking_version": chunking_version,
            "input_format": unit.input_format,
            "page_book": unit.page_book,
            "page_pdf_end": unit.page_pdf_end,
            "page_pdf_start": unit.page_pdf_start,
            "parent_id": parent_id,
            "provenance": provenance,
            "section_metadata": unit.metadata,
            "source_id": unit.doc_id,
            "source_page": unit.source_page,
            "strategy_config_snapshot": strategy_snapshot,
            "token_count": token_count,
            "retrieval_unit": chunk_type != "parent",
        },
        "doc_id": unit.doc_id,
        "section_id": unit.section_id,
        "char_start": char_start,
        "char_end": char_end,
        "token_count": token_count,
        "chunking_version": chunking_version,
        "preserved_entities": find_preserved_entities(chunk_text, protected_terms),
    }
    if extra_metadata:
        record["metadata"].update(extra_metadata)
    record["chunk_hash"] = make_chunk_hash(
        chunk_strategy_id=chunk_strategy_id,
        chunking_version=chunking_version,
        config_version=config_version,
        chunk_type=chunk_type,
        doc_id=unit.doc_id,
        section_id=unit.section_id,
        source_page=unit.source_page,
        char_start=char_start,
        char_end=char_end,
        chunk_text=chunk_text,
    )
    return record


def make_flat_chunk_records(
    unit_windows: Iterable[tuple[SourceUnit, list[Atom]]],
    *,
    config: dict[str, Any],
    strategy_id: str,
    strategy: dict[str, Any],
    protected_terms: list[str],
    extra_metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    config_version = str(config.get("version") or "unknown")
    chunking_version = str(strategy.get("chunking_version") or f"{strategy_id}_v1")
    strategy_snapshot = json.loads(json.dumps(strategy, ensure_ascii=False))
    counters: dict[str, int] = defaultdict(int)
    records: list[dict[str, Any]] = []

    for unit, atoms in unit_windows:
        if not atoms:
            continue
        counters[unit.doc_id] += 1
        records.append(
            make_chunk_record(
                unit=unit,
                atoms=atoms,
                chunk_type="chunk",
                running_no=counters[unit.doc_id],
                parent_id=None,
                chunk_strategy_id=strategy_id,
                chunking_version=chunking_version,
                config_version=config_version,
                strategy_snapshot=strategy_snapshot,
                protected_terms=protected_terms,
                extra_metadata=extra_metadata,
            )
        )
    return records


def chunk_parent_child(
    units: list[SourceUnit],
    *,
    config: dict[str, Any],
    strategy_id: str = STRATEGY_PARENT_CHILD,
) -> list[dict[str, Any]]:
    strategy = get_strategy_config(config, strategy_id)
    protected_terms = flatten_protected_terms(config)
    config_version = str(config.get("version") or "unknown")
    chunking_version = str(strategy.get("chunking_version") or f"{strategy_id}_v1")
    parent_spec = strategy["parent"]
    child_spec = strategy["child"]
    max_atom_tokens = max(int(parent_spec["max_tokens"]), int(child_spec["max_tokens"]))

    counters: dict[str, dict[str, int]] = defaultdict(lambda: {"parent": 0, "child": 0})
    records: list[dict[str, Any]] = []
    strategy_snapshot = json.loads(json.dumps(strategy, ensure_ascii=False))

    for unit in units:
        atoms = atomize_text(unit.text, protected_terms, max_atom_tokens)
        if not atoms:
            continue

        parent_windows = build_token_windows(
            atoms,
            min_tokens=int(parent_spec["min_tokens"]),
            max_tokens=int(parent_spec["max_tokens"]),
            overlap_tokens=int(parent_spec["overlap_tokens"]),
        )

        for parent_atoms in parent_windows:
            counters[unit.doc_id]["parent"] += 1
            parent_record = make_chunk_record(
                unit=unit,
                atoms=parent_atoms,
                chunk_type="parent",
                running_no=counters[unit.doc_id]["parent"],
                parent_id=None,
                chunk_strategy_id=strategy_id,
                chunking_version=chunking_version,
                config_version=config_version,
                strategy_snapshot=strategy_snapshot,
                protected_terms=protected_terms,
            )
            records.append(parent_record)

            child_windows = build_token_windows(
                parent_atoms,
                min_tokens=int(child_spec["min_tokens"]),
                max_tokens=int(child_spec["max_tokens"]),
                overlap_tokens=int(child_spec["overlap_tokens"]),
            )
            for child_atoms in child_windows:
                counters[unit.doc_id]["child"] += 1
                records.append(
                    make_chunk_record(
                        unit=unit,
                        atoms=child_atoms,
                        chunk_type="child",
                        running_no=counters[unit.doc_id]["child"],
                        parent_id=parent_record["chunk_id"],
                        chunk_strategy_id=strategy_id,
                        chunking_version=chunking_version,
                        config_version=config_version,
                        strategy_snapshot=strategy_snapshot,
                        protected_terms=protected_terms,
                    )
                )

    return records


def iter_fixed_windows(
    units: list[SourceUnit],
    *,
    strategy: dict[str, Any],
    protected_terms: list[str],
) -> Iterable[tuple[SourceUnit, list[Atom]]]:
    max_tokens = int(strategy["max_tokens"])
    overlap_tokens = max(0, round(max_tokens * float(strategy.get("overlap_ratio", 0))))

    for unit in units:
        atoms = atomize_text(unit.text, protected_terms, max_tokens)
        for window in build_token_windows(
            atoms,
            min_tokens=1,
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
        ):
            yield unit, window


def chunk_fixed_size(
    units: list[SourceUnit],
    *,
    config: dict[str, Any],
    strategy_id: str,
) -> list[dict[str, Any]]:
    strategy = get_strategy_config(config, strategy_id)
    protected_terms = flatten_protected_terms(config)
    return make_flat_chunk_records(
        iter_fixed_windows(units, strategy=strategy, protected_terms=protected_terms),
        config=config,
        strategy_id=strategy_id,
        strategy=strategy,
        protected_terms=protected_terms,
    )


def iter_sentence_merge_windows(
    units: list[SourceUnit],
    *,
    strategy: dict[str, Any],
    protected_terms: list[str],
) -> Iterable[tuple[SourceUnit, list[Atom]]]:
    target_tokens = int(strategy["target_tokens"])
    max_tokens = int(strategy["max_tokens"])

    for unit in units:
        atoms = atomize_text(unit.text, protected_terms, max_tokens)
        current: list[Atom] = []
        current_tokens = 0

        for atom in atoms:
            if current and current_tokens + atom.token_count > max_tokens:
                yield unit, current
                current = []
                current_tokens = 0

            current.append(atom)
            current_tokens += atom.token_count

            if current_tokens >= target_tokens:
                yield unit, current
                current = []
                current_tokens = 0

        if current:
            yield unit, current


def chunk_sentence_merge(
    units: list[SourceUnit],
    *,
    config: dict[str, Any],
    strategy_id: str = STRATEGY_SENTENCE_MERGE,
) -> list[dict[str, Any]]:
    strategy = get_strategy_config(config, strategy_id)
    protected_terms = flatten_protected_terms(config)
    return make_flat_chunk_records(
        iter_sentence_merge_windows(units, strategy=strategy, protected_terms=protected_terms),
        config=config,
        strategy_id=strategy_id,
        strategy=strategy,
        protected_terms=protected_terms,
    )


def iter_semantic_windows(
    units: list[SourceUnit],
    *,
    strategy: dict[str, Any],
    protected_terms: list[str],
) -> Iterable[tuple[SourceUnit, list[Atom]]]:
    min_tokens = int(strategy["min_tokens"])
    target_tokens = int(strategy["target_tokens"])
    max_tokens = int(strategy["max_tokens"])
    similarity_threshold = float(strategy.get("similarity_threshold", 0.12))

    for unit in units:
        atoms = atomize_text(unit.text, protected_terms, max_tokens)
        current: list[Atom] = []
        current_tokens = 0

        for atom in atoms:
            if not current:
                current = [atom]
                current_tokens = atom.token_count
                continue

            current_text = chunk_text_from_atoms(current)
            similarity = lexical_similarity(current_text, atom.text)
            would_exceed_max = current_tokens + atom.token_count > max_tokens
            has_topic_shift = current_tokens >= min_tokens and similarity < similarity_threshold
            target_reached = current_tokens >= target_tokens

            if would_exceed_max or has_topic_shift or (target_reached and similarity == 0.0):
                yield unit, current
                current = [atom]
                current_tokens = atom.token_count
                continue

            current.append(atom)
            current_tokens += atom.token_count

        if current:
            yield unit, current


def chunk_semantic(
    units: list[SourceUnit],
    *,
    config: dict[str, Any],
    strategy_id: str = STRATEGY_SEMANTIC,
) -> list[dict[str, Any]]:
    strategy = get_strategy_config(config, strategy_id)
    protected_terms = flatten_protected_terms(config)
    return make_flat_chunk_records(
        iter_semantic_windows(units, strategy=strategy, protected_terms=protected_terms),
        config=config,
        strategy_id=strategy_id,
        strategy=strategy,
        protected_terms=protected_terms,
        extra_metadata={"semantic_method": str(strategy.get("semantic_method") or "lexical_legacy")},
    )


def iter_semantic_embedding_windows(
    units: list[SourceUnit],
    *,
    strategy: dict[str, Any],
    protected_terms: list[str],
    embedding_client: Any,
    events: list[SemanticSimilarityEvent] | None = None,
) -> list[SemanticWindow]:
    min_tokens = int(strategy["min_tokens"])
    target_tokens = int(strategy["target_tokens"])
    max_tokens = int(strategy["max_tokens"])
    similarity_threshold = float(strategy.get("similarity_threshold", 0.74))
    windows: list[SemanticWindow] = []

    for unit in units:
        atoms = atomize_text(unit.text, protected_terms, max_tokens)
        if not atoms:
            continue

        atom_vectors = [embedding_client.embed_document(atom.text) for atom in atoms]
        current: list[Atom] = []
        current_vectors: list[list[float]] = []
        current_tokens = 0
        last_break_score: float | None = None
        last_break_reason = "document_start"

        for index, (atom, vector) in enumerate(zip(atoms, atom_vectors, strict=True)):
            if not current:
                current = [atom]
                current_vectors = [vector]
                current_tokens = atom.token_count
                continue

            similarity = cosine_similarity(centroid(current_vectors), vector)
            would_exceed_max = current_tokens + atom.token_count > max_tokens
            has_topic_shift = current_tokens >= min_tokens and similarity < similarity_threshold
            target_reached = current_tokens >= target_tokens
            break_reason: str | None = None

            if would_exceed_max:
                break_reason = "max_tokens"
            elif has_topic_shift:
                break_reason = "embedding_similarity_below_threshold"
            elif target_reached and similarity < min(1.0, similarity_threshold + 0.05):
                break_reason = "target_tokens_low_similarity"

            if events is not None:
                events.append(
                    SemanticSimilarityEvent(
                        doc_id=unit.doc_id,
                        section_id=unit.section_id,
                        atom_index=index,
                        similarity=round(similarity, 6),
                        current_tokens=current_tokens,
                        next_atom_tokens=atom.token_count,
                        break_reason=break_reason,
                    )
                )

            if break_reason:
                windows.append(
                    SemanticWindow(
                        unit=unit,
                        atoms=current,
                        break_score=last_break_score,
                        break_reason=last_break_reason,
                    )
                )
                current = [atom]
                current_vectors = [vector]
                current_tokens = atom.token_count
                last_break_score = similarity
                last_break_reason = break_reason
                continue

            current.append(atom)
            current_vectors.append(vector)
            current_tokens += atom.token_count

        if current:
            windows.append(
                SemanticWindow(
                    unit=unit,
                    atoms=current,
                    break_score=last_break_score,
                    break_reason=last_break_reason,
                )
            )
    return windows


def chunk_semantic_embedding(
    units: list[SourceUnit],
    *,
    config: dict[str, Any],
    strategy_id: str = STRATEGY_SEMANTIC_EMBEDDING,
    embedding_client: Any | None = None,
    semantic_events: list[SemanticSimilarityEvent] | None = None,
) -> list[dict[str, Any]]:
    strategy = get_strategy_config(config, strategy_id)
    protected_terms = flatten_protected_terms(config)
    client = embedding_client or MockSemanticEmbeddingClient()
    config_version = str(config.get("version") or "unknown")
    chunking_version = str(strategy.get("chunking_version") or f"{strategy_id}_v1")
    strategy_snapshot = json.loads(json.dumps(strategy, ensure_ascii=False))
    counters: dict[str, int] = defaultdict(int)
    records: list[dict[str, Any]] = []

    windows = iter_semantic_embedding_windows(
        units,
        strategy=strategy,
        protected_terms=protected_terms,
        embedding_client=client,
        events=semantic_events,
    )
    for window in windows:
        counters[window.unit.doc_id] += 1
        records.append(
            make_chunk_record(
                unit=window.unit,
                atoms=window.atoms,
                chunk_type="chunk",
                running_no=counters[window.unit.doc_id],
                parent_id=None,
                chunk_strategy_id=strategy_id,
                chunking_version=chunking_version,
                config_version=config_version,
                strategy_snapshot=strategy_snapshot,
                protected_terms=protected_terms,
                extra_metadata={
                    "centroid_policy": str(strategy.get("centroid_policy") or "running_centroid"),
                    "embedding_model_for_chunking": str(getattr(client, "model_name", strategy.get("embedding_model_for_chunking"))),
                    "max_tokens": int(strategy["max_tokens"]),
                    "min_tokens": int(strategy["min_tokens"]),
                    "semantic_break_reason": window.break_reason,
                    "semantic_break_score": window.break_score,
                    "semantic_method": str(strategy.get("semantic_method") or "embedding_similarity"),
                    "semantic_similarity_threshold": float(strategy.get("similarity_threshold", 0.74)),
                    "target_tokens": int(strategy["target_tokens"]),
                },
            )
        )
    return records


def chunk_units(
    units: list[SourceUnit],
    *,
    config: dict[str, Any],
    strategy_id: str,
    embedding_client: Any | None = None,
    semantic_events: list[SemanticSimilarityEvent] | None = None,
) -> list[dict[str, Any]]:
    get_strategy_config(config, strategy_id)
    if strategy_id == STRATEGY_PARENT_CHILD:
        return chunk_parent_child(units, config=config, strategy_id=strategy_id)
    if strategy_id in FIXED_STRATEGIES:
        return chunk_fixed_size(units, config=config, strategy_id=strategy_id)
    if strategy_id == STRATEGY_SENTENCE_MERGE:
        return chunk_sentence_merge(units, config=config, strategy_id=strategy_id)
    if strategy_id == STRATEGY_SEMANTIC_EMBEDDING:
        return chunk_semantic_embedding(
            units,
            config=config,
            strategy_id=strategy_id,
            embedding_client=embedding_client,
            semantic_events=semantic_events,
        )
    if strategy_id == STRATEGY_SEMANTIC:
        return chunk_semantic(units, config=config, strategy_id=strategy_id)
    raise ValueError(f"Strategy '{strategy_id}' is configured but has no chunker implementation.")


def group_chunks_by_doc(chunks: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for chunk in chunks:
        grouped[str(chunk["doc_id"])].append(chunk)
    return dict(sorted(grouped.items()))


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def output_targets(
    grouped_chunks: dict[str, list[dict[str, Any]]],
    *,
    output: Path | None,
    strategy_id: str,
) -> dict[str, Path]:
    if output is None:
        return {
            doc_id: DEFAULT_CHUNK_DIR / strategy_id / f"{doc_id}_chunks.jsonl"
            for doc_id in grouped_chunks
        }

    if output.suffix.lower() == ".jsonl":
        if len(grouped_chunks) != 1:
            raise ValueError("--output may be a .jsonl file only when one document is chunked.")
        doc_id = next(iter(grouped_chunks))
        return {doc_id: output}

    return {doc_id: output / f"{doc_id}_chunks.jsonl" for doc_id in grouped_chunks}


def build_summary(chunks: list[dict[str, Any]], strategy_id: str, strategy: dict[str, Any]) -> dict[str, Any]:
    grouped = group_chunks_by_doc(chunks)
    documents: dict[str, Any] = {}

    for doc_id, records in grouped.items():
        token_counts = [int(record["token_count"]) for record in records]
        parents = sum(1 for record in records if record["chunk_type"] == "parent")
        children = sum(1 for record in records if record["chunk_type"] == "child")
        flat_chunks = sum(1 for record in records if record["chunk_type"] == "chunk")
        retrieval_units = sum(1 for record in records if record.get("metadata", {}).get("retrieval_unit"))
        documents[doc_id] = {
            "avg_tokens": round(sum(token_counts) / len(token_counts), 2) if token_counts else 0,
            "child_chunks": children,
            "chunk_chunks": flat_chunks,
            "chunk_types": dict(
                sorted(
                    {
                        chunk_type: sum(1 for record in records if record["chunk_type"] == chunk_type)
                        for chunk_type in {record["chunk_type"] for record in records}
                    }.items()
                )
            ),
            "max_tokens": max(token_counts) if token_counts else 0,
            "min_tokens": min(token_counts) if token_counts else 0,
            "parent_chunks": parents,
            "retrieval_unit_chunks": retrieval_units,
            "total_chunks": len(records),
        }

    official_baseline = bool(strategy.get("official_baseline", False))
    return {
        "chunk_strategy_id": strategy_id,
        "documents": documents,
        "legacy_or_auxiliary": not official_baseline,
        "official_baseline": official_baseline,
        "semantic_method": strategy.get("semantic_method"),
        "total_chunks": len(chunks),
    }


def build_semantic_similarity_report(
    events: list[SemanticSimilarityEvent],
    *,
    strategy_id: str,
    strategy: dict[str, Any],
    usage_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    similarities = [event.similarity for event in events]
    break_events = [event for event in events if event.break_reason]
    if similarities:
        sorted_scores = sorted(similarities)
        avg_similarity = round(sum(similarities) / len(similarities), 6)
        min_similarity = sorted_scores[0]
        max_similarity = sorted_scores[-1]
    else:
        avg_similarity = min_similarity = max_similarity = None

    break_reasons = {
        reason: sum(1 for event in break_events if event.break_reason == reason)
        for reason in sorted({str(event.break_reason) for event in break_events})
    }
    report = {
        "avg_similarity": avg_similarity,
        "break_count": len(break_events),
        "break_reasons": break_reasons,
        "chunk_strategy_id": strategy_id,
        "event_count": len(events),
        "max_similarity": max_similarity,
        "min_similarity": min_similarity,
        "sample_events": [
            {
                "atom_index": event.atom_index,
                "break_reason": event.break_reason,
                "current_tokens": event.current_tokens,
                "doc_id": event.doc_id,
                "next_atom_tokens": event.next_atom_tokens,
                "section_id": event.section_id,
                "similarity": event.similarity,
            }
            for event in events[:50]
        ],
        "semantic_method": strategy.get("semantic_method"),
        "semantic_similarity_threshold": float(strategy.get("similarity_threshold", 0.74)),
    }
    if usage_summary:
        report.update(usage_summary)
    return report


def write_outputs(
    chunks: list[dict[str, Any]],
    *,
    output: Path | None,
    summary_output: Path | None,
    semantic_report_output: Path | None,
    strategy_id: str,
    strategy: dict[str, Any],
    semantic_events: list[SemanticSimilarityEvent] | None = None,
    semantic_usage_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    grouped = group_chunks_by_doc(chunks)
    targets = output_targets(grouped, output=output, strategy_id=strategy_id)
    for doc_id, records in grouped.items():
        write_jsonl(targets[doc_id], records)

    summary = build_summary(chunks, strategy_id, strategy)
    summary["outputs"] = {doc_id: str(path) for doc_id, path in targets.items()}

    if summary_output is not None:
        summary_output.parent.mkdir(parents=True, exist_ok=True)
        summary_output.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    if semantic_report_output is not None:
        if strategy_id != STRATEGY_SEMANTIC_EMBEDDING:
            raise ValueError("--semantic-report-output is only valid for chunk_semantic_embedding.")
        report = build_semantic_similarity_report(
            semantic_events or [],
            strategy_id=strategy_id,
            strategy=strategy,
            usage_summary=semantic_usage_summary,
        )
        semantic_report_output.parent.mkdir(parents=True, exist_ok=True)
        semantic_report_output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        summary["semantic_report_output"] = str(semantic_report_output)
    if semantic_usage_summary:
        summary.update(semantic_usage_summary)
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate strategy-aware corpus chunks.")
    parser.add_argument(
        "--input",
        nargs="*",
        type=Path,
        default=None,
        help="Clean JSON/sections JSONL file(s), or a corpus directory. Defaults to benchmark corpus.",
    )
    parser.add_argument(
        "--chunking-strategy",
        default=None,
        help="Strategy ID from configs/chunking_strategies.yaml.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--source-registry", type=Path, default=DEFAULT_SOURCE_REGISTRY)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory, or a .jsonl path when chunking a single document.",
    )
    parser.add_argument("--summary-output", type=Path, default=None)
    parser.add_argument(
        "--semantic-report-output",
        type=Path,
        default=None,
        help="Write semantic similarity diagnostics for chunk_semantic_embedding.",
    )
    parser.add_argument(
        "--mock-embedding",
        action="store_true",
        help="Use deterministic local embeddings for chunk_semantic_embedding.",
    )
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> dict[str, Any]:
    args = parse_args(argv)
    config = load_chunking_config(args.config)
    strategy_id = args.chunking_strategy or str(config["default_strategy"])
    strategy = get_strategy_config(config, strategy_id)

    registry = load_source_registry(args.source_registry)
    input_files = discover_input_files(args.input)
    units: list[SourceUnit] = []
    for input_file in input_files:
        units.extend(load_source_units(input_file, registry))

    if not units:
        raise ValueError("No source text records were loaded from the requested input.")

    semantic_events: list[SemanticSimilarityEvent] = []
    embedding_client = None
    if strategy_id == STRATEGY_SEMANTIC_EMBEDDING:
        embedding_client = make_semantic_embedding_client(strategy, mock_embedding=args.mock_embedding)

    chunks = chunk_units(
        units,
        config=config,
        strategy_id=strategy_id,
        embedding_client=embedding_client,
        semantic_events=semantic_events,
    )
    if not chunks:
        raise ValueError("No chunks were generated from the requested input.")

    return write_outputs(
        chunks,
        output=args.output,
        summary_output=args.summary_output,
        semantic_report_output=args.semantic_report_output,
        strategy_id=strategy_id,
        strategy=strategy,
        semantic_events=semantic_events,
        semantic_usage_summary=(
            embedding_client.get_usage_summary()
            if embedding_client is not None and hasattr(embedding_client, "get_usage_summary")
            else None
        ),
    )


def cli(argv: list[str] | None = None) -> int:
    try:
        summary = run(argv)
    except (FileNotFoundError, NotImplementedError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
