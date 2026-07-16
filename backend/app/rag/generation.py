from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from app.rag.config import ExperimentConfig
from app.rag.gemini_keys import get_primary_runtime_gemini_api_key, load_runtime_gemini_api_keys
from app.rag.state import RAGState


NO_CONTEXT_ANSWER = "Chưa đủ dữ liệu trong nguồn hiện có để kết luận. Bạn có thể hỏi cụ thể hơn về sao, cung hoặc tổ hợp trong lá số Tử Vi."
GENERATION_BACKEND_FALLBACK_PREFIX = "Hiện chưa gọi được mô hình luận giải đầy đủ."


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
        return get_primary_runtime_gemini_api_key("Gemini generation", explicit_api_key=self.api_key)

    def _api_keys(self) -> list[str]:
        if self.api_key:
            return [self.api_key]
        keys = load_runtime_gemini_api_keys()
        if not keys:
            self._api_key()
        return keys

    def generate(self, prompt: str, *, config: ExperimentConfig, state: RAGState) -> GenerationResult:
        try:
            import google.generativeai as genai
        except Exception as exc:
            raise RuntimeError("google-generativeai is required for Gemini generation.") from exc

        last_exc: Exception | None = None
        keys = self._api_keys()
        for index, api_key in enumerate(keys, start=1):
            try:
                genai.configure(api_key=api_key)
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
            except Exception as exc:
                last_exc = exc
                if self.api_key or index >= len(keys):
                    break
                continue
        if last_exc is not None:
            raise RuntimeError(f"Gemini generation failed after {len(keys)} runtime key(s): {last_exc}") from last_exc
        raise RuntimeError("GEMINI_API_KEY or GEMINI_API_KEYS is required for Gemini generation.")


class DeterministicGenerationClient:
    """Test-safe generator that creates a concise cited Vietnamese answer.

    This client is used for tests/debug endpoints and as a last-resort fallback
    when the real generation backend is unavailable. It must therefore be honest:
    do not pretend to have produced a full interpretation. Prefer chart facts when
    present so factual chart questions remain useful even during Gemini outages.
    """

    def generate(self, prompt: str, *, config: ExperimentConfig, state: RAGState) -> GenerationResult:
        context_chunks = state.get("context_chunks") or []
        if not context_chunks and not str(state.get("final_context") or "").strip():
            return GenerationResult(answer=NO_CONTEXT_ANSWER, model="deterministic-test", fallback_reason="no_context")
        answer = build_chart_aware_fallback_answer(state, backend_unavailable=False)
        return GenerationResult(answer=answer, model="deterministic-test")


def build_chart_aware_fallback_answer(state: RAGState, *, backend_unavailable: bool) -> str:
    """Build an honest fallback answer from chart facts and retrieved sources.

    The old deterministic fallback produced a generic answer that looked like a
    normal assistant response while not actually interpreting the chart. For live
    chat this is misleading, especially for factual chart questions. This fallback
    explicitly states the limitation, surfaces extracted chart facts first, and
    only then points to retrieved sources.
    """
    context_chunks = state.get("context_chunks") or []
    final_context = str(state.get("final_context") or "").strip()
    chart_lines = chart_fact_answer_lines(state.get("chart_facts") or {})
    source_markers = citation_markers(context_chunks, limit=3)

    lines: list[str] = []
    if backend_unavailable:
        lines.append(GENERATION_BACKEND_FALLBACK_PREFIX)
    else:
        lines.append("Dưới đây là phần tóm tắt an toàn từ dữ kiện lá số và nguồn đã truy xuất.")

    if chart_lines:
        lines.append("")
        lines.append("Dữ kiện lá số đã trích xuất:")
        lines.extend(chart_lines)
    elif "[CHART_FACTS]" in final_context or "[CHART]" in final_context:
        lines.append("")
        lines.append("Hệ thống có khối dữ kiện lá số trong context, nhưng chưa chuẩn hóa đủ để tóm tắt tự động.")

    if source_markers:
        lines.append("")
        lines.append(f"Nguồn Tử Vi liên quan đã truy xuất: {', '.join(source_markers)}.")
        if backend_unavailable:
            lines.append("Các nguồn này chỉ nên xem là tài liệu đối chiếu; phần luận giải tổng hợp cần chạy lại khi mô hình sinh câu trả lời hoạt động.")
    elif final_context:
        lines.append("")
        lines.append("Có context nội bộ cho câu hỏi này, nhưng chưa có nguồn citation dạng [S1], [S2] để hiển thị.")

    if not chart_lines and not source_markers and not final_context:
        return NO_CONTEXT_ANSWER
    return "\n".join(lines).strip()


def chart_fact_answer_lines(chart_facts: dict[str, Any]) -> list[str]:
    if not isinstance(chart_facts, dict) or not chart_facts.get("chart_available"):
        return []
    lines: list[str] = []
    summary = chart_facts.get("summary") if isinstance(chart_facts.get("summary"), dict) else {}
    summary_labels = {
        "menh_position": "Mệnh",
        "than_position": "Thân",
        "ban_menh": "Bản Mệnh",
        "ngu_hanh_ban_menh": "Ngũ hành Bản Mệnh",
        "cuc": "Cục",
    }
    for key, label in summary_labels.items():
        value = summary.get(key)
        if value not in (None, "", []):
            lines.append(f"- {label}: {value}")

    for house in chart_facts.get("house_facts") or []:
        if not isinstance(house, dict):
            continue
        house_label = str(house.get("house_name") or "Cung liên quan").strip()
        branch = str(house.get("earthly_branch") or "").strip()
        prefix = f"- Cung {house_label}"
        if branch:
            prefix += f" tại {branch}"
        details: list[str] = []
        major = star_names(house.get("major_stars") or [])
        aux = star_names(house.get("aux_stars") or [])
        if major:
            details.append(f"chính tinh: {', '.join(major)}")
        if aux:
            details.append(f"phụ tinh: {', '.join(aux[:8])}")
        special_states = []
        if house.get("tuan_khong"):
            special_states.append("Tuần")
        if house.get("triet_khong"):
            special_states.append("Triệt")
        if special_states:
            details.append("có " + "/".join(special_states))
        if house.get("is_than_resident"):
            details.append("Thân cư tại cung này")
        lines.append(prefix + ("; " + "; ".join(details) if details else ""))
    for relation in chart_facts.get("relations") or []:
        if not isinstance(relation, dict):
            continue
        if relation.get("type") == "tam_hop" and relation.get("houses"):
            name = relation.get("name") or "-".join(str(value) for value in relation.get("houses") or [])
            houses = ", ".join(str(value) for value in relation.get("houses") or [])
            status = "đã nhận diện trong lá số" if relation.get("available") else "chưa đủ quy tắc để xác nhận đầy đủ"
            lines.append(f"- Tam hợp {name}: {houses}; {status}")
    return lines


def star_names(stars: list[Any]) -> list[str]:
    names: list[str] = []
    for star in stars:
        if isinstance(star, dict):
            value = star.get("name") or star.get("canonical_name")
        else:
            value = star
        text = str(value or "").strip()
        if text and text not in names:
            names.append(text)
    return names


def citation_markers(context_chunks: list[Any], *, limit: int) -> list[str]:
    markers: list[str] = []
    for chunk in context_chunks:
        if not isinstance(chunk, dict):
            continue
        marker = str(chunk.get("citation_marker") or "").strip()
        if not marker:
            continue
        formatted = f"[{marker}]" if not marker.startswith("[") else marker
        if formatted not in markers:
            markers.append(formatted)
        if len(markers) >= limit:
            break
    return markers


def build_generation_prompt(state: RAGState, config: ExperimentConfig) -> str:
    query = state.get("rewritten_query") or state.get("normalized_query") or state.get("query") or ""
    final_context = state.get("final_context") or ""
    return (
        "Bạn là trợ lý luận giải Tử Vi. Chỉ trả lời trong domain TUVI.\n"
        "Dựa vào CONTEXT và lá số được cung cấp; không bịa nguồn, không suy diễn ngoài dữ liệu.\n"
        "Nếu CONTEXT không đủ, hãy nói rõ chưa đủ dữ liệu trong nguồn hiện có.\n"
        "Khi dùng thông tin từ nguồn sách, ghi citation dạng [S1], [S2]. "
        "Khi dùng dữ kiện lá số trong khối [CHART], ghi citation [CHART]. "
        "Không viết marker [CHART_FACTS]; chỉ dùng [CHART] cho dữ kiện lá số. "
        "Không tự tạo marker [S1] nếu CONTEXT không có block [S1].\n\n"
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
    final_context = str(state.get("final_context") or "").strip()
    if not context_chunks and (not final_context or state.get("retrieval_backend_unavailable")):
        return NO_CONTEXT_ANSWER, {
            "fallback_reason": "no_context",
            "generation_model": config.generation_model,
            "prompt_template_id": config.prompt_template_id,
        }

    prompt = build_generation_prompt(state, config)
    client = generation_client or GeminiGenerationClient()
    try:
        result = client.generate(prompt, config=config, state=state)
    except Exception as exc:
        fallback_answer = build_chart_aware_fallback_answer(state, backend_unavailable=True)
        return fallback_answer, {
            "error_type": type(exc).__name__,
            "error_message": safe_error_message(exc),
            "fallback_reason": "generation_backend_error",
            "generation_model": config.generation_model,
            "prompt_chars": len(prompt),
            "prompt_template_id": config.prompt_template_id,
            "raw_response_present": False,
        }
    metadata = {
        "fallback_reason": result.fallback_reason,
        "generation_model": result.model,
        "prompt_chars": len(prompt),
        "prompt_template_id": config.prompt_template_id,
        "raw_response_present": bool(result.raw_response),
    }
    return result.answer or NO_CONTEXT_ANSWER, metadata


def safe_error_message(exc: Exception, *, max_chars: int = 300) -> str:
    message = str(exc).strip()
    if not message:
        message = repr(exc)
    return message[:max_chars]