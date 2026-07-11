from typing import Any
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.clients import get_neo4j_driver, get_langfuse_client, get_supabase_client
from app.config import settings
from app.rag.generation import DeterministicGenerationClient
from app.rag.graph import run_rag_dry_run
from app.rag.nodes import default_chart_loader


logger = logging.getLogger(__name__)

try:
    from app.routers import chart
except ModuleNotFoundError as exc:
    chart = None
    logger.warning("Chart router is unavailable: %s", exc)

try:
    from app.routers import lasotuvi_routes
except ModuleNotFoundError as exc:
    lasotuvi_routes = None
    logger.warning("Lasotuvi router is unavailable: %s", exc)

app = FastAPI(title="TuVi GraphRAG - FastAPI Backend")

# Include routers
if chart is not None:
    app.include_router(chart.router)
if lasotuvi_routes is not None:
    app.include_router(lasotuvi_routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

supabase = get_supabase_client()
neo4j_driver = get_neo4j_driver()
langfuse = get_langfuse_client()


def log_chat_retrieval_diagnostics(state: dict[str, Any]) -> None:
    """Log actionable RAG fallback diagnostics without changing the API response.

    The chat endpoint intentionally allows retrieval fallback so the frontend
    receives a graceful answer instead of a 500. When that happens, backend logs
    need to show which node fell back and why; otherwise all failures look like
    the generic no-context answer in the UI.
    """
    trace = state.get("retrieval_trace") or {}
    nodes = trace.get("nodes") or []
    fallback_nodes = [node for node in nodes if node.get("status") == "fallback"]
    generation_metadata = state.get("generation_metadata") or {}
    source_count = len(state.get("sources") or [])
    context_count = len(state.get("context_chunks") or [])

    if fallback_nodes:
        logger.warning(
            "RAG retrieval fallback during chat: chart_id=%s experiment_id=%s nodes=%s",
            state.get("chart_id"),
            state.get("experiment_id"),
            [
                {
                    "node": node.get("node"),
                    "error_type": node.get("error_type"),
                    "fallback_reason": node.get("fallback_reason"),
                }
                for node in fallback_nodes
            ],
        )


def resilient_chart_loader(chart_id: str, user_id: str | None = None) -> dict[str, Any]:
    """Load chart from Supabase, but do not fail the whole chat if unavailable.

    The knowledge-base RAG answer can still be useful without personalized chart
    data. This keeps /chat from returning 500 for missing/stale chart IDs while
    preserving diagnostics in backend logs and chart_data.
    """
    try:
        return default_chart_loader(chart_id, user_id)
    except Exception as exc:
        logger.warning(
            "Chart context unavailable; continuing chat with minimal chart context: chart_id=%s user_id=%s error_type=%s error=%s",
            chart_id,
            user_id,
            type(exc).__name__,
            str(exc),
        )
        return {
            "chart_system": "TUVI",
            "chart_data": {
                "id": chart_id,
                "chart_type": "TUVI",
                "chart_load_fallback": True,
                "chart_load_error_type": type(exc).__name__,
            },
        }

    if generation_metadata.get("fallback_reason") == "no_context" or source_count == 0:
        logger.warning(
            "RAG chat produced no cited context: chart_id=%s experiment_id=%s context_count=%s source_count=%s generation_fallback=%s",
            state.get("chart_id"),
            state.get("experiment_id"),
            context_count,
            source_count,
            generation_metadata.get("fallback_reason"),
        )


@app.get("/health")
async def health():
    return {"status": "ok"}


class ChatRequest(BaseModel):
    chart_id: str
    query: str
    user_id: str | None = None
    experiment_config_path: str | None = None


@app.get("/debug/rag-runtime")
async def rag_runtime_debug():
    """Read-only runtime diagnostics for local debugging.

    This endpoint intentionally avoids returning secrets. It helps verify the
    exact config/env that the running backend process is using, which may differ
    from files on disk when process environment variables override .env values.
    """
    from app.rag.config import load_experiment_config, resolve_config_path

    config_path = resolve_config_path()
    config = load_experiment_config(config_path)
    neo4j_uri = settings.NEO4J_URI
    neo4j_uri_safe = neo4j_uri
    if "://" in neo4j_uri:
        scheme, rest = neo4j_uri.split("://", 1)
        neo4j_uri_safe = f"{scheme}://{rest.split('/', 1)[0]}"

    neo4j_status: dict[str, Any]
    try:
        with neo4j_driver.session(database=settings.NEO4J_DATABASE or None) as session:
            database_name = session.run("CALL db.info() YIELD name RETURN name").single()["name"]
            counts = {
                "chunks": session.run("MATCH (c:Chunk) RETURN count(c) AS count").single()["count"],
                "tuvi_fixed_chunks": session.run(
                    """
                    MATCH (c:Chunk {domain: 'TUVI', chunk_strategy_id: 'chunk_fixed_512'})
                    RETURN count(c) AS count
                    """
                ).single()["count"],
                "tuvi_entities": session.run("MATCH (e:Entity {domain: 'TUVI'}) RETURN count(e) AS count").single()["count"],
            }
            indexes = [
                dict(record)
                for record in session.run(
                    """
                    SHOW INDEXES
                    YIELD name, type, state, labelsOrTypes, properties
                    WHERE name IN ['chunkFulltext', 'chunkVectorBgeM3']
                    RETURN name, type, state, labelsOrTypes, properties
                    ORDER BY name
                    """
                )
            ]
        neo4j_status = {
            "ok": True,
            "database": database_name,
            "counts": counts,
            "indexes": indexes,
        }
    except Exception as exc:
        neo4j_status = {
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }

    return {
        "status": "ok",
        "config_path": str(config_path),
        "experiment_id": config.experiment_id,
        "chunk_strategy_id": config.chunk_strategy_id,
        "query_rewrite_enabled": config.query_rewrite_enabled,
        "graph_retrieval_enabled": config.graph_retrieval_enabled,
        "dense_retrieval_enabled": config.dense_retrieval_enabled,
        "sparse_retrieval_enabled": config.sparse_retrieval_enabled,
        "neo4j": {
            "uri": neo4j_uri_safe,
            "username": settings.NEO4J_USERNAME,
            "database": settings.NEO4J_DATABASE,
            "status": neo4j_status,
        },
    }


@app.post("/debug/rag-smoke")
async def rag_smoke_debug(req: ChatRequest):
    """Run the chat RAG path with deterministic generation for diagnostics.

    It still loads the real chart and real Neo4j retrieval, but it avoids the
    final Gemini generation call so we can isolate retrieval/context problems.
    """
    initial_state: dict[str, Any] = {
        "chart_id": req.chart_id,
        "query": req.query,
    }
    if req.user_id:
        initial_state["user_id"] = req.user_id
    if req.experiment_config_path:
        initial_state["experiment_config_path"] = req.experiment_config_path

    try:
        state = run_rag_dry_run(
            initial_state,
            neo4j_driver=neo4j_driver,
            generation_client=DeterministicGenerationClient(),
            retrieval_fallback_on_error=True,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"error_type": type(exc).__name__, "error": str(exc)},
        ) from exc

    return {
        "status": "ok",
        "answer": state.get("answer") or "",
        "sources": state.get("sources") or [],
        "source_count": len(state.get("sources") or []),
        "context_chunk_count": len(state.get("context_chunks") or []),
        "candidate_counts": {
            "graph": len(state.get("graph_candidates") or []),
            "dense": len(state.get("dense_candidates") or []),
            "sparse": len(state.get("sparse_candidates") or []),
            "fused": len(state.get("fused_candidates") or []),
        },
        "trace": state.get("retrieval_trace") or {},
        "generation_metadata": state.get("generation_metadata") or {},
        "citation_metadata": state.get("citation_metadata") or {},
    }


@app.get("/debug/rag-smoke-no-chart")
async def rag_smoke_no_chart_debug(query: str = "Thiên Mã tại Quan Lộc thế nào?"):
    """Read-only retrieval smoke test that does not require a Supabase chart."""

    def fake_chart_loader(chart_id: str, user_id: str | None = None) -> dict[str, Any]:
        return {"chart_system": "TUVI", "chart_data": {"id": chart_id, "chart_type": "TUVI"}}

    state = run_rag_dry_run(
        {"chart_id": "debug-chart", "query": query},
        chart_loader=fake_chart_loader,
        neo4j_driver=neo4j_driver,
        generation_client=DeterministicGenerationClient(),
        retrieval_fallback_on_error=True,
    )

    return {
        "status": "ok",
        "answer": state.get("answer") or "",
        "source_count": len(state.get("sources") or []),
        "context_chunk_count": len(state.get("context_chunks") or []),
        "candidate_counts": {
            "graph": len(state.get("graph_candidates") or []),
            "dense": len(state.get("dense_candidates") or []),
            "sparse": len(state.get("sparse_candidates") or []),
            "fused": len(state.get("fused_candidates") or []),
        },
        "sources": state.get("sources") or [],
        "trace": state.get("retrieval_trace") or {},
    }

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        langfuse.log_event("chat_request", {
            "chart_id": req.chart_id,
            "user_id": req.user_id,
            "query": req.query,
        })
    except Exception:
        pass

    try:
        initial_state: dict[str, Any] = {
            "chart_id": req.chart_id,
            "query": req.query,
        }
        if req.user_id:
            initial_state["user_id"] = req.user_id
        if req.experiment_config_path:
            initial_state["experiment_config_path"] = req.experiment_config_path

        state = run_rag_dry_run(
            initial_state,
            chart_loader=resilient_chart_loader,
            neo4j_driver=neo4j_driver,
            retrieval_fallback_on_error=True,
        )
        log_chat_retrieval_diagnostics(state)
        config = state.get("experiment_config")
        chunk_strategy_id = getattr(config, "chunk_strategy_id", None)
        response = {
            "status": "ok",
            "answer": state.get("answer") or "",
            "sources": state.get("sources") or [],
            "trace": state.get("retrieval_trace") or {},
            "experiment_id": state.get("experiment_id"),
            "config_hash": state.get("config_hash"),
            "chunk_strategy_id": chunk_strategy_id,
            "generation_metadata": state.get("generation_metadata") or {},
            "citation_metadata": state.get("citation_metadata") or {},
        }
        try:
            langfuse.log_event("chat_response", {
                "chart_id": req.chart_id,
                "user_id": req.user_id,
                "experiment_id": response["experiment_id"],
                "config_hash": response["config_hash"],
                "chunk_strategy_id": response["chunk_strategy_id"],
                "source_count": len(response["sources"]),
            })
        except Exception:
            pass
        return response
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Unhandled chat error: chart_id=%s user_id=%s error_type=%s",
            req.chart_id,
            req.user_id,
            type(exc).__name__,
        )
        try:
            langfuse.log_event("chat_error", {
                "chart_id": req.chart_id,
                "user_id": req.user_id,
                "error_type": type(exc).__name__,
            })
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Không thể xử lý câu hỏi lúc này.") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info")
