# Chunking & Canonical Corpus Specification

**Doc ID:** CC-SPEC-001
**Version:** 1.0
**Applies to:** Dataset team, RAG team, QA/eval team
**Status:** Normative specification

## 1. Purpose

This document defines the required shared corpus, normalization, sectioning, chunking, schema, and mapping rules for both benchmark dataset work and the RAG system.

## 2. Normative rules

### 2.1 Shared source of truth

All teams must use the same 4 source books and the same canonical corpus derived from them.

### 2.2 Normalize first

All processing must run on canonical cleaned text, not raw PDF text.
Required normalization:
- Unicode NFC.
- Remove repeated headers and footers.
- Remove page numbers only when they are layout noise.
- Normalize whitespace and line breaks.
- Do not rewrite source wording.

### 2.3 Section before chunk

The shared logic is:
1. Extract page text.
2. Normalize pages.
3. Build sections.
4. Define spans inside sections.
5. Chunk from canonical sections.
6. Map spans to chunks.

### 2.4 Do not split key entities

Do not split a sentence if it contains important star / palace names.
Do not cut in a way that breaks canonical entity phrases.

### 2.5 Deterministic versioning

Every pipeline must declare:
- `normalize_version`
- `section_version`
- `chunking_version`
- `entity_dict_version`
- `mapping_version`

If any of these changes, downstream files must be regenerated.

## 3. Shared files

The following files are shared from the start by both teams:

| File | Shared use | Why shared |
|---|---|---|
| `source_registry.json` | Yes | One canonical identity for the 4 books. |
| `raw_pages_*.json` | Yes | One extraction base for audit and normalization. |
| `clean_pages_*.json` | Yes | Canonical cleaned text used by annotation and chunking. |
| `page_map_*.json` | Yes | Shared page reference for audit and citations. |
| `sections_*.jsonl` / `source_sections_index.json` | Yes | Shared structural layer before chunking. |
| Canonical star/palace dictionary | Yes | Shared entity names and aliases. |
| `schema_release.json` | Yes for dataset governance | Freezes benchmark fields. |
| `gold_sections.jsonl` | Yes for evaluation | Ground truth spans for retrieval eval. |
| `gold_with_chunk_map.jsonl` | Yes | Final bridge between spans and chunks. |

## 4. Required schemas

### 4.1 source_registry.json
Each source must include:
- `doc_id`
- `title`
- `file_name`
- `domain`
- `citation_short`
- `id_convention`
- `notes`

### 4.2 clean page record
Each cleaned page should include:
- `doc_id`
- `page_pdf`
- `page_book` (nullable)
- `raw_text`
- `clean_text`
- `normalize_version`
- `quality_flag`

### 4.3 section record
Each section should include:
- `section_id`
- `doc_id`
- `title`
- `page_start_pdf`
- `page_end_pdf`
- `char_start`
- `char_end`
- `text`
- `section_level`
- `parent_section_id` (nullable)
- `section_version`

### 4.4 chunk record
Each chunk should include:
- `chunk_id`
- `doc_id`
- `source_name`
- `source_page`
- `section_id`
- `parent_id`
- `chunk_type` (`parent` or `child`)
- `chunk_text`
- `chunk_hash`
- `domain`
- `chunking_version`
- `char_start`
- `char_end`
- `token_count`
- `preserved_entities` (optional)

## 5. Chunking rules

### 5.1 Default chunk sizes
- Parent chunk: 400–512 tokens.
- Parent overlap: 60–100 tokens.
- Child chunk: 120–180 tokens.
- Child overlap: small and consistent.

### 5.2 Boundary rules
- Prefer section-aware boundaries.
- Do not split inside a sentence when a star/palace name appears.
- Preserve heading context when possible.
- Keep chunks deterministic across reruns.

### 5.3 IDs
Suggested formats:
- `section_id`: `{doc_id}-SEC-{number}`
- `span_id`: `{section_id}-SPAN-{number}`
- `chunk_id`: `{doc_id}-{chunk_type}-{number}`

## 6. Mapping rules

### 6.1 Span to chunk mapping
Map gold spans to chunks using:
1. `doc_id`
2. `section_id`
3. page reference
4. character offsets
5. text overlap as fallback

### 6.2 Mapping success
A mapping is valid if the span is fully covered or safely aligned with one or more chunks and the overlap is unambiguous.

### 6.3 Mapping failure
If mapping is uncertain, flag it and recheck normalization or chunking version. Do not guess.

## 7. Operational freeze order

Freeze in this order:
1. `source_registry.json`
2. canonical cleaned pages
3. page map
4. section index
5. entity dictionary
6. chunking version
7. ingest chunks and provenance
8. span-to-chunk mapping
9. dataset release

## 8. Ownership

- Dataset team owns benchmark labeling and release files.
- RAG team owns ingestion, chunking implementation, embeddings, retrieval, and provenance.
- Shared corpora, sectioning rules, entity dictionary, and mapping rules are common assets.

## 9. Completion criteria

This spec is considered adopted when:
- the 4 source books are frozen,
- canonical cleaned pages are shared,
- sectioning and chunking versions are fixed,
- chunk metadata matches this spec,
- span-to-chunk mapping works on a dry run.
