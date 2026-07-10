from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol

from app.rag.config import ExperimentConfig
from app.rag.state import RAGState


NO_CONTEXT_ANSWER = "Chưa đủ dữ liệu trong nguồn hiện có để kết luận. Bạn có thể hỏi cụ thể hơn về sao, cung hoặc tổ hợp trong lá số Tử Vi."


@dataclass(frozen=True)
class GenerationResult:
    answer: str
    model: str
    raw_response: str | None = None
    fallback_reason: str | None = None


class GenerationClient(Protocol):
    def generate(self, prompt: str, *, config: ExperimentConfig, state: RAGState) -> GenerationResult:
        ...


class GeminiGenerationClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    def _api_key(self) -> str:
        if self.api_key:
            return self.api_key
        combined = os.getenv("GEMINI_API_KEYS") or ""
        keys = [key.strip() for key in combined.split(",") if key.strip()]
        if keys:
            return keys[0]
        key = os.getenv("GEMINI_API_KEY")
        if key:
            return key
        raise RuntimeError("GEMINI_API_KEY or GEMINI_API_KEYS is required for Gemini generation.")

    def generate(self, prompt: str, *, config: ExperimentConfig, state: RAGState) -> GenerationResult:
        try:
            import google.generativeai as genai
        except Exception as exc:
            raise RuntimeError("google-generativeai is required for Gemini generation.") from exc

        genai.configure(api_key=self._api_key())
        model = genai.GenerativeModel(config.generation_model)
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 1024,
            },
        )
        raw_text = str(getattr(response, "text", "") or "").strip()
        return GenerationResult(answer=raw_text or NO_CONTEXT_ANSWER, model=config.generation_model, raw_response=raw_text)


class DeterministicGenerationClient:
    """Test-safe generator that creates a concise cited Vietnamese answer."""

    def generate(self, prompt: str, *, config: ExperimentConfig, state: RAGState) -> GenerationResult:
        context_chunks = state.get("context_chunks") or []
        if not context_chunks:
            return GenerationResult(answer=NO_CONTEXT_ANSWER, model="deterministic-test", fallback_reason="no_context")
        markers = ", ".join(f"[{chunk.get('citation_marker')}]" for chunk in context_chunks[:2])
        query = state.get("rewritten_query") or state.get("normalized_query") or state.get("query") or "câu hỏi"
        answer = (
            f"Dựa trên nguồn Tử Vi đã truy xuất, câu hỏi '{query}' cần được luận trong phạm vi các đoạn liên quan. "
            f"Các nguồn chính gồm {markers}. Khi áp dụng vào lá số, nên đối chiếu thêm cung, sao và tổ hợp liên quan trước khi kết luận."
        )
        return GenerationResult(answer=answer, model="deterministic-test")


def build_generation_prompt(state: RAGState, config: ExperimentConfig) -> str:
    query = state.get("rewritten_query") or state.get("normalized_query") or state.get("query") or ""
    final_context = state.get("final_context") or ""
    return (
        "Bạn là trợ lý luận giải Tử Vi. Chỉ trả lời trong domain TUVI.\n"
        "Dựa vào CONTEXT và lá số được cung cấp; không bịa nguồn, không suy diễn ngoài dữ liệu.\n"
        "Nếu CONTEXT không đủ, hãy nói rõ chưa đủ dữ liệu trong nguồn hiện có.\n"
        "Khi dùng thông tin từ nguồn, ghi citation dạng [S1], [S2].\n\n"
        f"prompt_template_id: {config.prompt_template_id}\n"
        f"chunk_strategy_id: {config.chunk_strategy_id}\n"
        f"QUESTION: {query}\n\n"
        f"CONTEXT:\n{final_context}\n\n"
        "Trả lời tiếng Việt, ngắn gọn, có citation nếu có nguồn."
    )


def generate_answer(
    state: RAGState,
    config: ExperimentConfig,
    *,
    generation_client: GenerationClient | None = None,
) -> tuple[str, dict[str, Any]]:
    context_chunks = state.get("context_chunks") or []
    if not context_chunks:
        return NO_CONTEXT_ANSWER, {
            "fallback_reason": "no_context",
            "generation_model": config.generation_model,
            "prompt_template_id": config.prompt_template_id,
        }

    prompt = build_generation_prompt(state, config)
    client = generation_client or GeminiGenerationClient()
    result = client.generate(prompt, config=config, state=state)
    metadata = {
        "fallback_reason": result.fallback_reason,
        "generation_model": result.model,
        "prompt_chars": len(prompt),
        "prompt_template_id": config.prompt_template_id,
        "raw_response_present": bool(result.raw_response),
    }
    return result.answer or NO_CONTEXT_ANSWER, metadata