from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from app.rag.nodes import ChartLoader, DRY_RUN_NODE_ORDER, QueryEntityExtractor, build_node_map
from app.rag.rewrite import QueryRewriter
from app.rag.state import RAGState

try:
    from langgraph.graph import END, StateGraph

    LANGGRAPH_AVAILABLE = True
except Exception:
    END = "__end__"
    StateGraph = None
    LANGGRAPH_AVAILABLE = False


class SequentialDryRunGraph:
    """Small compatibility graph for environments before langgraph is installed."""

    def __init__(self, nodes: list[tuple[str, Callable[[RAGState], RAGState]]]) -> None:
        self.nodes = nodes

    def invoke(self, state: RAGState) -> RAGState:
        current: RAGState = dict(state)
        for _, node in self.nodes:
            current = node(current)
        return current


def build_rag_graph(
    *,
    chart_loader: ChartLoader | None = None,
    config_path: Path | str | None = None,
    query_rewriter: QueryRewriter | None = None,
    query_entity_extractor: QueryEntityExtractor | None = None,
    neo4j_driver: Any | None = None,
    dense_embedding_service: Any | None = None,
) -> Any:
    node_map = build_node_map(
        chart_loader=chart_loader,
        config_path=config_path,
        query_rewriter=query_rewriter,
        query_entity_extractor=query_entity_extractor,
        neo4j_driver=neo4j_driver,
        dense_embedding_service=dense_embedding_service,
    )

    if not LANGGRAPH_AVAILABLE or StateGraph is None:
        return SequentialDryRunGraph([(name, node_map[name]) for name in DRY_RUN_NODE_ORDER])

    workflow = StateGraph(RAGState)
    for name in DRY_RUN_NODE_ORDER:
        workflow.add_node(name, node_map[name])

    workflow.set_entry_point(DRY_RUN_NODE_ORDER[0])
    for left, right in zip(DRY_RUN_NODE_ORDER, DRY_RUN_NODE_ORDER[1:]):
        workflow.add_edge(left, right)
    workflow.add_edge(DRY_RUN_NODE_ORDER[-1], END)
    return workflow.compile()


def run_rag_dry_run(
    initial_state: RAGState,
    *,
    chart_loader: ChartLoader | None = None,
    config_path: Path | str | None = None,
    query_rewriter: QueryRewriter | None = None,
    query_entity_extractor: QueryEntityExtractor | None = None,
    neo4j_driver: Any | None = None,
    dense_embedding_service: Any | None = None,
) -> RAGState:
    graph = build_rag_graph(
        chart_loader=chart_loader,
        config_path=config_path,
        query_rewriter=query_rewriter,
        query_entity_extractor=query_entity_extractor,
        neo4j_driver=neo4j_driver,
        dense_embedding_service=dense_embedding_service,
    )
    return graph.invoke(dict(initial_state))
