from typing import Any
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.clients import get_neo4j_driver, get_langfuse_client, get_supabase_client
from app.config import settings
from app.rag.graph import run_rag_dry_run


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


@app.get("/health")
async def health():
    return {"status": "ok"}


class ChatRequest(BaseModel):
    chart_id: str
    query: str
    user_id: str | None = None
    experiment_config_path: str | None = None


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

        state = run_rag_dry_run(initial_state, retrieval_fallback_on_error=True)
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
