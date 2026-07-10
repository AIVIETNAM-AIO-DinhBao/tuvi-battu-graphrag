"""RAG foundation package for W4."""

from app.rag.config import ExperimentConfig, config_hash, load_experiment_config
from app.rag.generation import GenerationClient
from app.rag.graph import build_rag_graph, run_rag_dry_run
from app.rag.ranking import CandidateReranker
from app.rag.rewrite import RewriteResult
from app.rag.state import RAGState

__all__ = [
    "ExperimentConfig",
    "CandidateReranker",
    "GenerationClient",
    "RAGState",
    "RewriteResult",
    "build_rag_graph",
    "config_hash",
    "load_experiment_config",
    "run_rag_dry_run",
]
