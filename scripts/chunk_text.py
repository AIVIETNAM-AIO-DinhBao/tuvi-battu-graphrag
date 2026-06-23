"""Strategy-aware chunk generation for W3-INGEST-02.

The script reads canonical cleaned corpus files and emits deterministic JSONL
chunks with strategy metadata. W3-INGEST-02 implements only Strategy A:
structure-first parent-child chunking.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = ROOT_DIR / "configs" / "chunking_strategies.yaml"
DEFAULT_CORPUS_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "corpus"
DEFAULT_SOURCE_REGISTRY = (
    ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "guideline" / "source_registry.json"
)
DEFAULT_CHUNK_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "chunks"
STRATEGY_PARENT_CHILD = "chunk_structure_parent_child"

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
) -> dict[str, Any]:
    chunk_text = chunk_text_from_atoms(atoms)
    char_start = min(atom.start for atom in atoms)
    char_end = max(atom.end for atom in atoms)
    token_count = count_tokens(chunk_text)
    chunk_id = f"{unit.doc_id}_{chunk_strategy_id}_{chunk_type}_{running_no:06d}"

    record = {
        "chunk_id": chunk_id,
        "parent_id": parent_id,
        "chunk_type": chunk_type,
        "chunk_text": chunk_text,
        "source_name": unit.source_name,
        "source_page": unit.source_page,
        "domain": unit.domain,
        "chunk_strategy_id": chunk_strategy_id,
        "chunk_hash": "",
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
            "section_metadata": unit.metadata,
            "source_page": unit.source_page,
            "strategy_config_snapshot": strategy_snapshot,
            "token_count": token_count,
        },
        "doc_id": unit.doc_id,
        "section_id": unit.section_id,
        "char_start": char_start,
        "char_end": char_end,
        "token_count": token_count,
        "chunking_version": chunking_version,
        "preserved_entities": find_preserved_entities(chunk_text, protected_terms),
    }
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


def chunk_units(
    units: list[SourceUnit],
    *,
    config: dict[str, Any],
    strategy_id: str,
) -> list[dict[str, Any]]:
    if strategy_id != STRATEGY_PARENT_CHILD:
        get_strategy_config(config, strategy_id)
    return chunk_parent_child(units, config=config, strategy_id=strategy_id)


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


def build_summary(chunks: list[dict[str, Any]], strategy_id: str) -> dict[str, Any]:
    grouped = group_chunks_by_doc(chunks)
    documents: dict[str, Any] = {}

    for doc_id, records in grouped.items():
        token_counts = [int(record["token_count"]) for record in records]
        parents = sum(1 for record in records if record["chunk_type"] == "parent")
        children = sum(1 for record in records if record["chunk_type"] == "child")
        documents[doc_id] = {
            "avg_tokens": round(sum(token_counts) / len(token_counts), 2) if token_counts else 0,
            "child_chunks": children,
            "max_tokens": max(token_counts) if token_counts else 0,
            "min_tokens": min(token_counts) if token_counts else 0,
            "parent_chunks": parents,
            "total_chunks": len(records),
        }

    return {
        "chunk_strategy_id": strategy_id,
        "documents": documents,
        "total_chunks": len(chunks),
    }


def write_outputs(
    chunks: list[dict[str, Any]],
    *,
    output: Path | None,
    summary_output: Path | None,
    strategy_id: str,
) -> dict[str, Any]:
    grouped = group_chunks_by_doc(chunks)
    targets = output_targets(grouped, output=output, strategy_id=strategy_id)
    for doc_id, records in grouped.items():
        write_jsonl(targets[doc_id], records)

    summary = build_summary(chunks, strategy_id)
    summary["outputs"] = {doc_id: str(path) for doc_id, path in targets.items()}

    if summary_output is not None:
        summary_output.parent.mkdir(parents=True, exist_ok=True)
        summary_output.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
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
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> dict[str, Any]:
    args = parse_args(argv)
    config = load_chunking_config(args.config)
    strategy_id = args.chunking_strategy or str(config["default_strategy"])
    get_strategy_config(config, strategy_id)

    registry = load_source_registry(args.source_registry)
    input_files = discover_input_files(args.input)
    units: list[SourceUnit] = []
    for input_file in input_files:
        units.extend(load_source_units(input_file, registry))

    if not units:
        raise ValueError("No source text records were loaded from the requested input.")

    chunks = chunk_units(units, config=config, strategy_id=strategy_id)
    if not chunks:
        raise ValueError("No chunks were generated from the requested input.")

    return write_outputs(
        chunks,
        output=args.output,
        summary_output=args.summary_output,
        strategy_id=strategy_id,
    )


def cli(argv: list[str] | None = None) -> int:
    try:
        summary = run(argv)
    except (FileNotFoundError, NotImplementedError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
