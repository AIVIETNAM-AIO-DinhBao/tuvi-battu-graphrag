from __future__ import annotations

import json
import re
from collections.abc import Iterable
from typing import Any, TypedDict

from app.rag.config import ExperimentConfig
from app.rag.state import RAGState


FULLTEXT_STOPWORDS = {"có", "của", "gì", "là", "tại", "thì", "trong", "và", "với"}
SAFE_NEO4J_INDEX_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
TEXT_PREVIEW_CHARS = 240


class RetrievalCandidate(TypedDict, total=False):
    retrieval_path: str
    rank: int
    score: float
    chunk_id: str | None
    chunk_hash: str | None
    chunk_type: str | None
    parent_id: str | None
    chunk_strategy_id: str | None
    domain: str | None
    source_id: str | None
    source_name: str | None
    source_page: int | str | None
    text: str
    text_preview: str
    title: str | None
    matched_entities: list[str]
    relation_types: list[str]
    provenance: dict[str, Any]


def safe_index_name(value: str) -> str:
    if not SAFE_NEO4J_INDEX_RE.match(value):
        raise ValueError(f"Unsafe Neo4j index name: {value!r}")
    return value


def sanitize_fulltext_query(query: str) -> str:
    # Neo4j fulltext uses Lucene syntax; keep Vietnamese text but neutralize operators.
    cleaned = re.sub(r'([+\-!(){}\[\]^"~*?:\\/]|&&|\|\|)', " ", query)
    return " ".join(cleaned.split())


def build_fulltext_query(query: str) -> str:
    terms = [
        term
        for term in sanitize_fulltext_query(query).split()
        if len(term) > 1 and term.casefold() not in FULLTEXT_STOPWORDS
    ]
    if not terms:
        return sanitize_fulltext_query(query)
    return " OR ".join(terms)


def retrieval_query_text(state: RAGState) -> str:
    return (
        state.get("rewritten_query")
        or state.get("normalized_query")
        or state.get("query")
        or ""
    ).strip()


def query_entity_rows(state: RAGState) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for entity in state.get("query_entities") or []:
        canonical_name = str(entity.get("canonical_name") or "").strip()
        entity_type = str(entity.get("entity_type") or "").strip()
        if not canonical_name or not entity_type:
            continue
        key = (canonical_name, entity_type)
        if key in seen:
            continue
        seen.add(key)
        rows.append({"canonical_name": canonical_name, "entity_type": entity_type})
    return rows


def normalize_candidate(record: Any, *, retrieval_path: str, rank: int) -> RetrievalCandidate:
    node = record_get(record, "node") or {}
    score = record_get(record, "score")
    matched_entities = to_string_list(record_get(record, "matched_entities"))
    relation_types = to_string_list(record_get(record, "relation_types"))
    text = str(node_get(node, "text") or node_get(node, "chunk_text") or "")
    title = optional_string(node_get(node, "title"))
    chunk_id = optional_string(node_get(node, "chunk_id") or node_get(node, "id"))
    provenance = coerce_provenance(node_get(node, "provenance_json") or node_get(node, "provenance"))
    provenance_fields = {
        "chunk_hash": optional_string(node_get(node, "chunk_hash")),
        "chunk_id": chunk_id,
        "chunk_strategy_id": optional_string(node_get(node, "chunk_strategy_id")),
        "parent_id": optional_string(node_get(node, "parent_id")),
        "source_id": optional_string(node_get(node, "source_id")),
        "source_name": optional_string(node_get(node, "source_name")),
        "source_page": node_get(node, "source_page"),
    }
    for key, value in provenance_fields.items():
        if value is not None and key not in provenance:
            provenance[key] = value

    return {
        "retrieval_path": retrieval_path,
        "rank": rank,
        "score": float(score if score is not None else 0.0),
        "chunk_id": chunk_id,
        "chunk_hash": provenance_fields["chunk_hash"],
        "chunk_type": optional_string(node_get(node, "chunk_type")),
        "parent_id": provenance_fields["parent_id"],
        "chunk_strategy_id": provenance_fields["chunk_strategy_id"],
        "domain": optional_string(node_get(node, "domain")),
        "source_id": provenance_fields["source_id"],
        "source_name": provenance_fields["source_name"],
        "source_page": provenance_fields["source_page"],
        "text": text,
        "text_preview": text[:TEXT_PREVIEW_CHARS],
        "title": title,
        "matched_entities": matched_entities,
        "relation_types": relation_types,
        "provenance": provenance,
    }


def retrieve_graph_candidates(
    state: RAGState,
    *,
    session: Any,
    config: ExperimentConfig,
) -> list[RetrievalCandidate]:
    entities = query_entity_rows(state)
    if not entities:
        return []

    graph_config = config.graph_retrieval
    records = execute_read(
        session,
        graph_retrieval_tx,
        entities=entities,
        top_k=graph_config.top_k,
        per_entity_limit=graph_config.per_entity_limit,
        relation_types=graph_config.allowed_relation_types,
        domain=config.domain,
        source_ids=config.source_ids,
        chunk_strategy_id=config.chunk_strategy_id,
        child_only=graph_config.child_only,
    )
    return normalize_and_rank(records, retrieval_path="graph")


def retrieve_dense_candidates(
    state: RAGState,
    *,
    session: Any,
    embedding_service: Any,
    config: ExperimentConfig,
) -> list[RetrievalCandidate]:
    dense_config = config.dense_retrieval
    query = retrieval_query_text(state)
    embedding = list(embedding_service.embed_query(query))
    if len(embedding) != config.embedding.dimension:
        raise ValueError(
            f"Dense query embedding dimension must be {config.embedding.dimension}; got {len(embedding)}."
        )

    records = execute_read(
        session,
        dense_retrieval_tx,
        embedding=embedding,
        candidate_k=dense_config.candidate_k,
        top_k=dense_config.top_k,
        domain=config.domain,
        source_ids=config.source_ids,
        chunk_strategy_id=config.chunk_strategy_id,
        vector_index_name=dense_config.vector_index,
        child_only=dense_config.child_only,
    )
    return normalize_and_rank(records, retrieval_path="dense")


def retrieve_sparse_candidates(
    state: RAGState,
    *,
    session: Any,
    config: ExperimentConfig,
) -> list[RetrievalCandidate]:
    sparse_config = config.sparse_retrieval
    fulltext_records = execute_read(
        session,
        sparse_retrieval_tx,
        query=retrieval_query_text(state),
        top_k=sparse_config.top_k,
        domain=config.domain,
        source_ids=config.source_ids,
        chunk_strategy_id=config.chunk_strategy_id,
        fulltext_index_name=sparse_config.fulltext_index,
        child_only=sparse_config.child_only,
    )
    exact_entities = query_entity_rows(state)
    exact_records = []
    if exact_entities:
        exact_records = execute_read(
            session,
            exact_entity_text_retrieval_tx,
            entities=exact_entities,
            top_k=sparse_config.top_k,
            domain=config.domain,
            source_ids=config.source_ids,
            chunk_strategy_id=config.chunk_strategy_id,
            child_only=sparse_config.child_only,
        )
    return normalize_and_rank([*exact_records, *fulltext_records], retrieval_path="sparse")


def graph_retrieval_tx(
    tx: Any,
    *,
    entities: list[dict[str, str]],
    top_k: int,
    per_entity_limit: int,
    relation_types: list[str],
    domain: str,
    source_ids: list[str],
    chunk_strategy_id: str,
    child_only: bool,
) -> list[Any]:
    direct = list(
        tx.run(
            """
            UNWIND $entities AS qe
            MATCH (seed:Entity {
                canonical_name: qe.canonical_name,
                entity_type: qe.entity_type,
                domain: $domain
            })
            CALL {
                WITH seed
                MATCH (node:Chunk)-[:MENTIONS]->(seed)
                WHERE node.domain = $domain
                  AND node.source_id IN $source_ids
                  AND node.chunk_strategy_id = $chunk_strategy_id
                  AND (
                    $child_only = false
                    OR $chunk_strategy_id <> 'chunk_structure_parent_child'
                    OR node.chunk_type = 'child'
                  )
                RETURN node
                LIMIT $per_entity_limit
            }
            WITH node, collect(DISTINCT seed.canonical_name) AS matched_entities
            RETURN node,
                   1.0 AS score,
                   matched_entities,
                   ['MENTIONS'] AS relation_types
            ORDER BY score DESC
            LIMIT $top_k
            """,
            entities=entities,
            top_k=top_k,
            per_entity_limit=per_entity_limit,
            domain=domain,
            source_ids=source_ids,
            chunk_strategy_id=chunk_strategy_id,
            child_only=child_only,
        )
    )
    related = list(
        tx.run(
            """
            UNWIND $entities AS qe
            MATCH (seed:Entity {
                canonical_name: qe.canonical_name,
                entity_type: qe.entity_type,
                domain: $domain
            })-[rel]-(related:Entity)
            WHERE type(rel) IN $relation_types
            CALL {
                WITH related
                MATCH (node:Chunk)-[:MENTIONS]->(related)
                WHERE node.domain = $domain
                  AND node.source_id IN $source_ids
                  AND node.chunk_strategy_id = $chunk_strategy_id
                  AND (
                    $child_only = false
                    OR $chunk_strategy_id <> 'chunk_structure_parent_child'
                    OR node.chunk_type = 'child'
                  )
                RETURN node
                LIMIT $per_entity_limit
            }
            WITH node,
                 max(coalesce(rel.confidence, 0.5)) AS score,
                 collect(DISTINCT seed.canonical_name) AS matched_entities,
                 collect(DISTINCT type(rel)) AS relation_types
            RETURN node, score, matched_entities, relation_types
            ORDER BY score DESC
            LIMIT $top_k
            """,
            entities=entities,
            top_k=top_k,
            per_entity_limit=per_entity_limit,
            domain=domain,
            source_ids=source_ids,
            chunk_strategy_id=chunk_strategy_id,
            relation_types=[relation for relation in relation_types if relation != "MENTIONS"],
            child_only=child_only,
        )
    )
    return direct + related


def dense_retrieval_tx(
    tx: Any,
    *,
    embedding: list[float],
    candidate_k: int,
    top_k: int,
    domain: str,
    source_ids: list[str],
    chunk_strategy_id: str,
    vector_index_name: str,
    child_only: bool,
) -> list[Any]:
    index_name = safe_index_name(vector_index_name)
    return list(
        tx.run(
            f"""
            CALL db.index.vector.queryNodes('{index_name}', $candidate_k, $embedding)
            YIELD node, score
            WHERE node.domain = $domain
              AND node.source_id IN $source_ids
              AND node.chunk_strategy_id = $chunk_strategy_id
              AND (
                $child_only = false
                OR $chunk_strategy_id <> 'chunk_structure_parent_child'
                OR node.chunk_type = 'child'
              )
            RETURN node,
                   score,
                   [] AS matched_entities,
                   [] AS relation_types
            ORDER BY score DESC
            LIMIT $top_k
            """,
            candidate_k=max(candidate_k, top_k),
            embedding=embedding,
            top_k=top_k,
            domain=domain,
            source_ids=source_ids,
            chunk_strategy_id=chunk_strategy_id,
            child_only=child_only,
        )
    )


def sparse_retrieval_tx(
    tx: Any,
    *,
    query: str,
    top_k: int,
    domain: str,
    source_ids: list[str],
    chunk_strategy_id: str,
    fulltext_index_name: str,
    child_only: bool,
) -> list[Any]:
    index_name = safe_index_name(fulltext_index_name)
    return list(
        tx.run(
            f"""
            CALL db.index.fulltext.queryNodes('{index_name}', $fulltext_query)
            YIELD node, score
            WHERE node.domain = $domain
              AND node.source_id IN $source_ids
              AND node.chunk_strategy_id = $chunk_strategy_id
              AND (
                $child_only = false
                OR $chunk_strategy_id <> 'chunk_structure_parent_child'
                OR node.chunk_type = 'child'
              )
            RETURN node,
                   score,
                   [] AS matched_entities,
                   [] AS relation_types
            ORDER BY score DESC
            LIMIT $top_k
            """,
            fulltext_query=build_fulltext_query(query),
            top_k=top_k,
            domain=domain,
            source_ids=source_ids,
            chunk_strategy_id=chunk_strategy_id,
            child_only=child_only,
        )
    )


def exact_entity_text_retrieval_tx(
    tx: Any,
    *,
    entities: list[dict[str, str]],
    top_k: int,
    domain: str,
    source_ids: list[str],
    chunk_strategy_id: str,
    child_only: bool,
) -> list[Any]:
    return list(
        tx.run(
            """
            UNWIND $entities AS qe
            MATCH (node:Chunk)
            WHERE node.domain = $domain
              AND node.source_id IN $source_ids
              AND node.chunk_strategy_id = $chunk_strategy_id
              AND (
                $child_only = false
                OR $chunk_strategy_id <> 'chunk_structure_parent_child'
                OR node.chunk_type = 'child'
              )
              AND (
                toLower(coalesce(node.text, '')) CONTAINS toLower(qe.canonical_name)
                OR toLower(coalesce(node.title, '')) CONTAINS toLower(qe.canonical_name)
              )
            WITH node,
                 collect(DISTINCT qe.canonical_name) AS matched_entities,
                 toLower(coalesce(node.text, '')) AS text_lc
            WITH node,
                 matched_entities,
                 text_lc,
                 reduce(def_boost = 0.0, entity IN matched_entities |
                     def_boost
                     + CASE WHEN text_lc CONTAINS toLower(entity + ':') THEN 220.0 ELSE 0.0 END
                     + CASE WHEN text_lc CONTAINS toLower(entity + ' -') THEN 120.0 ELSE 0.0 END
                 ) AS entity_definition_boost
            WITH node,
                 matched_entities,
                 100.0
                 + size(matched_entities)
                 + entity_definition_boost
                 + CASE WHEN entity_definition_boost > 0.0 AND (text_lc CONTAINS 'tánh chất' OR text_lc CONTAINS 'tính chất') THEN 50.0 ELSE 0.0 END
                 + CASE WHEN entity_definition_boost > 0.0 AND (text_lc CONTAINS 'tánh tình' OR text_lc CONTAINS 'tính tình') THEN 35.0 ELSE 0.0 END
                 + CASE WHEN text_lc CONTAINS 'thuộc ' AND text_lc CONTAINS 'hành ' THEN 10.0 ELSE 0.0 END
                 - CASE WHEN text_lc CONTAINS 'thông tin lá số' THEN 80.0 ELSE 0.0 END
                 - CASE WHEN text_lc CONTAINS 'tại cung tý nếu tử vi' THEN 90.0 ELSE 0.0 END
                 - CASE WHEN text_lc CONTAINS 'bảng tra' THEN 50.0 ELSE 0.0 END
                 - CASE WHEN text_lc CONTAINS 'hóa kỵ' THEN 10.0 ELSE 0.0 END
                 AS exact_score
            RETURN node,
                   exact_score AS score,
                   matched_entities,
                   ['EXACT_ENTITY_TEXT'] AS relation_types
            ORDER BY score DESC, coalesce(node.source_page, 999999) ASC
            LIMIT $top_k
            """,
            entities=entities,
            top_k=top_k,
            domain=domain,
            source_ids=source_ids,
            chunk_strategy_id=chunk_strategy_id,
            child_only=child_only,
        )
    )


def execute_read(session: Any, tx_func: Any, **kwargs: Any) -> list[Any]:
    if hasattr(session, "execute_read"):
        return list(session.execute_read(tx_func, **kwargs))
    return list(tx_func(session, **kwargs))


def normalize_and_rank(records: Iterable[Any], *, retrieval_path: str) -> list[RetrievalCandidate]:
    candidates = [
        normalize_candidate(record, retrieval_path=retrieval_path, rank=index)
        for index, record in enumerate(records, start=1)
    ]
    deduped = dedupe_candidates(candidates)
    for index, candidate in enumerate(deduped, start=1):
        candidate["rank"] = index
    return deduped


def dedupe_candidates(candidates: list[RetrievalCandidate]) -> list[RetrievalCandidate]:
    best_by_key: dict[str, RetrievalCandidate] = {}
    passthrough: list[RetrievalCandidate] = []
    for candidate in candidates:
        key = candidate.get("chunk_hash") or candidate.get("chunk_id")
        if not key:
            passthrough.append(candidate)
            continue
        previous = best_by_key.get(key)
        if previous is None or float(candidate["score"]) > float(previous["score"]):
            best_by_key[key] = candidate
    return sorted(
        [*best_by_key.values(), *passthrough],
        key=lambda item: (float(item.get("score") or 0.0), -int(item.get("rank") or 0)),
        reverse=True,
    )


def record_get(record: Any, key: str) -> Any:
    if hasattr(record, "get"):
        return record.get(key)
    try:
        return record[key]
    except (KeyError, TypeError, IndexError):
        return None


def node_get(node: Any, key: str) -> Any:
    if hasattr(node, "get"):
        return node.get(key)
    try:
        return node[key]
    except (KeyError, TypeError, IndexError):
        return None


def optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def to_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Iterable):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def coerce_provenance(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {"raw": value}
        return parsed if isinstance(parsed, dict) else {"value": parsed}
    return {}
