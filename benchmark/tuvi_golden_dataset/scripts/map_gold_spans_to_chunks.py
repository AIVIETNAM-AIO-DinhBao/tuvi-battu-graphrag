"""Map gold quotes to stable clean-corpus intervals, never to strategy-specific chunk IDs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.rag.ablation import load_ablation_dataset  # noqa: E402
from app.rag.evaluation_checkpoint import atomic_write_json, sha256_file  # noqa: E402


DEFAULT_DATASET = REPO_ROOT / "benchmark" / "tuvi_golden_dataset" / "release" / "tuviqa_v1_release.jsonl"
DEFAULT_CORPUS = REPO_ROOT / "benchmark" / "tuvi_golden_dataset" / "corpus"
DEFAULT_OUTPUT = (
    REPO_ROOT / "benchmark" / "tuvi_golden_dataset" / "sequential_ablation" / "gold_span_anchors.jsonl"
)
TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def portable_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def canonical_with_offsets(text: str) -> tuple[str, list[int]]:
    """Collapse whitespace while retaining indices into NFC-normalized source text."""

    normalized = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
    output: list[str] = []
    offsets: list[int] = []
    pending_space: int | None = None
    for index, character in enumerate(normalized):
        if character.isspace():
            if output and output[-1] != " " and pending_space is None:
                pending_space = index
            continue
        if pending_space is not None:
            output.append(" ")
            offsets.append(pending_space)
            pending_space = None
        output.append(character)
        offsets.append(index)
    return "".join(output), offsets


def tokens_with_offsets(text: str) -> tuple[list[str], list[tuple[int, int]]]:
    normalized = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
    matches = list(TOKEN_RE.finditer(normalized))
    return [match.group(0).casefold() for match in matches], [(match.start(), match.end()) for match in matches]


def load_clean_corpus(corpus_dir: Path) -> dict[str, list[dict[str, Any]]]:
    corpus: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(corpus_dir.rglob("*_clean.json")):
        records = json.loads(path.read_text(encoding="utf-8"))
        for record in records:
            doc_id = str(record.get("doc_id") or path.stem.split("_")[0])
            text = str(record.get("content") or "")
            canonical, offsets = canonical_with_offsets(text)
            tokens, token_offsets = tokens_with_offsets(text)
            corpus.setdefault(doc_id, []).append(
                {
                    "doc_id": doc_id,
                    "section_id": str(record.get("section_id") or ""),
                    "metadata": dict(record.get("metadata") or {}),
                    "text": unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n"),
                    "canonical": canonical,
                    "offsets": offsets,
                    "tokens": tokens,
                    "token_offsets": token_offsets,
                }
            )
    return corpus


def _page_matches(record: dict[str, Any], span: dict[str, Any]) -> bool:
    record_pages = {
        value
        for key in ("page_pdf", "page_book")
        if (value := record.get("metadata", {}).get(key)) not in (None, "")
    }
    span_pages = {value for key in ("page_pdf", "page_book") if (value := span.get(key)) not in (None, "")}
    return bool(record_pages & span_pages)


def find_matches(records: list[dict[str, Any]], quote: str) -> tuple[list[dict[str, Any]], str]:
    canonical_quote, _ = canonical_with_offsets(quote)
    if not canonical_quote:
        return [], "empty_quote"
    for case_sensitive, method in ((True, "nfc_whitespace_exact"), (False, "nfc_whitespace_casefold")):
        needle = canonical_quote if case_sensitive else canonical_quote.casefold()
        matches: list[dict[str, Any]] = []
        for record in records:
            haystack = record["canonical"] if case_sensitive else record["canonical"].casefold()
            for match in re.finditer(re.escape(needle), haystack):
                offsets = record["offsets"]
                start = offsets[match.start()]
                end = offsets[match.end() - 1] + 1
                matches.append(
                    {
                        "corpus_section_id": record["section_id"],
                        "char_start": start,
                        "char_end": end,
                    }
                )
        if matches:
            return matches, method
    quote_tokens, _ = tokens_with_offsets(quote)
    if quote_tokens:
        token_matches: list[dict[str, Any]] = []
        token_count = len(quote_tokens)
        for record in records:
            tokens = record["tokens"]
            for start_index in range(0, len(tokens) - token_count + 1):
                if tokens[start_index : start_index + token_count] != quote_tokens:
                    continue
                offsets = record["token_offsets"]
                token_matches.append(
                    {
                        "corpus_section_id": record["section_id"],
                        "char_start": offsets[start_index][0],
                        "char_end": offsets[start_index + token_count - 1][1],
                    }
                )
        if token_matches:
            return token_matches, "nfc_exact_token_sequence"
    return [], "not_found"


def build_anchors(
    dataset_path: Path,
    corpus_dir: Path,
    *,
    min_mapping_coverage: float = 0.80,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    items = load_ablation_dataset(dataset_path)
    corpus = load_clean_corpus(corpus_dir)
    anchors: list[dict[str, Any]] = []
    for item in items:
        for index, span in enumerate(item.gold_context_spans, start=1):
            doc_id = str(span.get("doc_id") or "").strip()
            quote = str(span.get("quote") or "")
            records = corpus.get(doc_id, [])
            page_records = [record for record in records if _page_matches(record, span)]
            matches, method = find_matches(page_records, quote) if page_records else ([], "not_found")
            scope = "page"
            if not matches:
                matches, method = find_matches(records, quote)
                scope = "document"
            if len(matches) == 1:
                status = "exact"
                selected = matches[0]
            elif len(matches) > 1:
                status = "ambiguous"
                selected = {"corpus_section_id": None, "char_start": None, "char_end": None}
            else:
                status = "unmapped"
                selected = {"corpus_section_id": None, "char_start": None, "char_end": None}
            anchors.append(
                {
                    "item_id": item.id,
                    "span_id": str(span.get("span_id") or f"{item.id}-SPAN-{index:02d}"),
                    "doc_id": doc_id,
                    "gold_section_id": span.get("section_id"),
                    "corpus_section_id": selected["corpus_section_id"],
                    "char_start": selected["char_start"],
                    "char_end": selected["char_end"],
                    "page_pdf": span.get("page_pdf"),
                    "page_book": span.get("page_book"),
                    "quote": quote,
                    "quote_sha256": hashlib.sha256(unicodedata.normalize("NFC", quote).encode("utf-8")).hexdigest(),
                    "mapping_status": status,
                    "match_method": f"{scope}:{method}",
                    "occurrence_count": len(matches),
                }
            )
    counts = Counter(anchor["mapping_status"] for anchor in anchors)
    gold_items = {anchor["item_id"] for anchor in anchors}
    mapped_items = {anchor["item_id"] for anchor in anchors if anchor["mapping_status"] in {"exact", "manual-approved"}}
    mapped_count = counts.get("exact", 0) + counts.get("manual-approved", 0)
    mapping_coverage = mapped_count / len(anchors) if anchors else 0.0
    summary = {
        "dataset_path": portable_path(dataset_path),
        "dataset_sha256": sha256_file(dataset_path),
        "corpus_dir": portable_path(corpus_dir),
        "item_count": len(items),
        "span_count": len(anchors),
        "mapped_span_count": mapped_count,
        "mapping_coverage": round(mapping_coverage, 6),
        "gold_item_count": len(gold_items),
        "items_with_mapped_span": len(mapped_items),
        "items_without_mapped_span": sorted(gold_items - mapped_items),
        "min_mapping_coverage": min_mapping_coverage,
        "status_counts": dict(sorted(counts.items())),
        "ready_for_official_run": counts.get("ambiguous", 0) == 0 and mapping_coverage >= min_mapping_coverage,
        "scoring_policy": (
            "Only exact/manual-approved anchors enter metric denominators. Unmapped spans are reported as "
            "annotation coverage limitations and are never fuzzy-matched silently."
        ),
    }
    return anchors, summary


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records)
    path.write_text(content, encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create stable gold-span anchors on the clean corpus.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=None)
    parser.add_argument("--min-mapping-coverage", type=float, default=0.80)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 0.0 < args.min_mapping_coverage <= 1.0:
        raise SystemExit("--min-mapping-coverage must be in (0, 1].")
    anchors, summary = build_anchors(
        args.dataset.resolve(),
        args.corpus_dir.resolve(),
        min_mapping_coverage=args.min_mapping_coverage,
    )
    output = args.output.resolve()
    summary_path = (args.summary or output.with_name("gold_span_anchor_summary.json")).resolve()
    write_jsonl(output, anchors)
    summary["output_path"] = portable_path(output)
    summary["output_sha256"] = sha256_file(output)
    atomic_write_json(summary_path, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ready_for_official_run"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
