from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Protocol

import requests

from app.rag.config import ExperimentConfig
from app.rag.gemini_keys import get_primary_runtime_gemini_api_key, load_runtime_gemini_api_keys
from app.rag.prompt_templates import build_prompt_from_template
from app.rag.state import RAGState


NO_CONTEXT_ANSWER = "Chưa đủ dữ liệu trong nguồn hiện có để kết luận. Bạn có thể hỏi cụ thể hơn về sao, cung hoặc tổ hợp trong lá số Tử Vi."
GENERATION_BACKEND_FALLBACK_PREFIX = "Hiện chưa gọi được mô hình luận giải đầy đủ."
ANSWER_FIRST_PROMPT_ID = "tuvi_generation_answer_first_v4"
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_CONNECT_TIMEOUT_SECONDS = 5
GEMINI_READ_TIMEOUT_SECONDS = 20


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
    def __init__(self, api_key: str | None = None, *, session: requests.Session | None = None) -> None:
        self.api_key = api_key
        self.session = session or requests.Session()

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
        last_exc: Exception | None = None
        keys = self._api_keys()
        for index, api_key in enumerate(keys, start=1):
            try:
                response = self.session.post(
                    f"{GEMINI_API_BASE_URL}/models/{config.generation_model}:generateContent",
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": api_key,
                    },
                    json={
                        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.2,
                            "maxOutputTokens": 1024,
                        },
                    },
                    timeout=(GEMINI_CONNECT_TIMEOUT_SECONDS, GEMINI_READ_TIMEOUT_SECONDS),
                )
                if not response.ok:
                    error = GeminiHTTPError.from_response(response)
                    last_exc = error
                    if should_rotate_gemini_key(error) and index < len(keys):
                        continue
                    break
                raw_text = gemini_response_text(response.json())
                return GenerationResult(answer=raw_text or NO_CONTEXT_ANSWER, model=config.generation_model, raw_response=raw_text)
            except requests.RequestException as exc:
                # A transport problem affects every key. Rotating through all
                # keys only multiplies latency and previously let /chat hang for
                # several minutes, so fail fast into the chart-aware fallback.
                last_exc = exc
                break
            except (TypeError, ValueError) as exc:
                last_exc = exc
                break
        if last_exc is not None:
            raise RuntimeError(f"Gemini generation failed: {safe_gemini_error(last_exc)}") from last_exc
        raise RuntimeError("GEMINI_API_KEY or GEMINI_API_KEYS is required for Gemini generation.")


@dataclass(frozen=True)
class GeminiHTTPError(Exception):
    status_code: int
    message: str

    @classmethod
    def from_response(cls, response: requests.Response) -> "GeminiHTTPError":
        message = ""
        try:
            payload = response.json()
            error = payload.get("error") if isinstance(payload, dict) else None
            if isinstance(error, dict):
                message = str(error.get("message") or error.get("status") or "").strip()
        except ValueError:
            pass
        return cls(status_code=int(response.status_code), message=(message or response.reason or "Gemini API error")[:300])

    def __str__(self) -> str:
        return f"HTTP {self.status_code}: {self.message}"


def should_rotate_gemini_key(error: GeminiHTTPError) -> bool:
    if error.status_code in {401, 403, 429}:
        return True
    message = error.message.casefold()
    return error.status_code == 400 and any(term in message for term in ("api key", "api_key_invalid", "quota"))


def gemini_response_text(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return ""
    candidate = candidates[0] if isinstance(candidates[0], dict) else {}
    content = candidate.get("content") if isinstance(candidate.get("content"), dict) else {}
    parts = content.get("parts") if isinstance(content.get("parts"), list) else []
    return "".join(str(part.get("text") or "") for part in parts if isinstance(part, dict)).strip()


def safe_gemini_error(exc: Exception) -> str:
    if isinstance(exc, GeminiHTTPError):
        return str(exc)
    if isinstance(exc, requests.Timeout):
        return "request timed out"
    if isinstance(exc, requests.ConnectionError):
        return "connection failed"
    return type(exc).__name__


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
        source_id = str(chunk.get("source_id") or "").strip()
        if not marker or marker.strip("[]").upper() == "CHART" or source_id.upper() == "CHART":
            continue
        formatted = f"[{marker}]" if not marker.startswith("[") else marker
        if formatted not in markers:
            markers.append(formatted)
        if len(markers) >= limit:
            break
    return markers


def build_generation_prompt(state: RAGState, config: ExperimentConfig) -> str:
    return build_prompt_from_template(state, config)


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

    retrieval_depth = str((state.get("retrieval_plan") or {}).get("retrieval_depth") or "")
    if retrieval_depth in {"medium", "deep"} and not has_corpus_context(context_chunks):
        return build_missing_corpus_answer(state), {
            "fallback_reason": "no_corpus_context",
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
    quality_issues = answer_quality_issues(result.answer, state) if config.prompt_template_id == ANSWER_FIRST_PROMPT_ID else []
    quality_retry_reasons = list(quality_issues)
    quality_retry_attempted = bool(quality_retry_reasons)
    quality_retry_succeeded = False
    quality_retry_error: str | None = None
    if quality_issues:
        try:
            repaired_result = client.generate(
                build_answer_repair_prompt(prompt, result.answer, quality_issues, state),
                config=config,
                state=state,
            )
            repaired_issues = answer_quality_issues(repaired_result.answer, state)
            if not repaired_issues:
                result = repaired_result
                quality_retry_succeeded = True
                quality_issues = []
            else:
                quality_issues = repaired_issues
        except Exception as exc:
            quality_retry_error = safe_error_message(exc)
    metadata = {
        "fallback_reason": result.fallback_reason,
        "generation_model": result.model,
        "prompt_chars": len(prompt),
        "prompt_template_id": config.prompt_template_id,
        "raw_response_present": bool(result.raw_response),
        "quality_retry_attempted": quality_retry_attempted,
        "quality_retry_succeeded": quality_retry_succeeded,
        "quality_retry_reasons": quality_retry_reasons,
        "quality_issues": quality_issues,
    }
    if quality_retry_error:
        metadata["quality_retry_error"] = quality_retry_error
    return result.answer or NO_CONTEXT_ANSWER, metadata


def has_corpus_context(context_chunks: list[Any]) -> bool:
    for chunk in context_chunks:
        if not isinstance(chunk, dict):
            continue
        marker = str(chunk.get("citation_marker") or "").strip("[]").upper()
        source_id = str(chunk.get("source_id") or "").strip().upper()
        if marker and marker != "CHART" and source_id != "CHART":
            return True
    return False


def build_missing_corpus_answer(state: RAGState) -> str:
    lines = [
        "KẾT LUẬN: Chưa đủ căn cứ từ tài liệu Tử Vi đã truy xuất để luận giải đáng tin cậy cho câu hỏi này.",
    ]
    chart_lines = chart_fact_answer_lines(state.get("chart_facts") or {})
    if chart_lines:
        lines.extend(["", "DỮ KIỆN XÁC NHẬN TỪ LÁ SỐ:"])
        lines.extend(f"{line} [CHART]" for line in chart_lines)
    lines.extend(
        [
            "",
            "LƯU Ý: Hệ thống chỉ ghi nhận các dữ kiện trên, không tự suy diễn tính cách hoặc vận hạn khi chưa truy xuất được nguồn sách phù hợp.",
        ]
    )
    return "\n".join(lines)


def answer_quality_issues(answer: str, state: RAGState) -> list[str]:
    """Detect narrow, high-confidence contradictions against complete chart input.

    This guard intentionally does not judge Tử Vi content and does not alter
    retrieval.  It only catches the recurrent failure where the draft says a
    palace (or its stars) was not supplied although the generation context
    contains the complete twelve-palace chart.
    """
    chart_facts = state.get("chart_facts") or {}
    all_houses = chart_facts.get("all_house_facts") or []
    if len(all_houses) < 12:
        return []

    normalized = " ".join(str(answer or "").casefold().split())
    if not normalized:
        return ["empty_answer"]

    missing_chart_patterns = (
        r"(?:lá số|\[chart\]).{0,120}(?:chưa|không).{0,40}(?:cung cấp|liệt kê|có dữ kiện|có thông tin).{0,100}(?:cung|sao)",
        r"(?:cung|sao).{0,120}(?:chưa|không).{0,40}(?:được cung cấp|được liệt kê|có trong).{0,80}(?:lá số|\[chart\])",
        r"(?:dữ kiện|thông tin).{0,80}(?:cung|sao).{0,120}(?:chưa|không).{0,40}(?:cung cấp|liệt kê).{0,40}(?:lá số|\[chart\])",
    )
    if any(re.search(pattern, normalized) for pattern in missing_chart_patterns):
        return ["false_missing_chart_data"]
    return []


def build_answer_repair_prompt(prompt: str, draft: str, issues: list[str], state: RAGState) -> str:
    chart_facts = state.get("chart_facts") or {}
    all_houses = chart_facts.get("all_house_facts") or []
    house_names = [
        str(house.get("house_name") or "").strip()
        for house in all_houses
        if isinstance(house, dict) and str(house.get("house_name") or "").strip()
    ]
    return (
        f"{prompt}\n\n"
        "YÊU CẦU SỬA BẢN NHÁP:\n"
        f"Bản nháp vi phạm: {', '.join(issues)}.\n"
        f"[CHART] đã cung cấp đủ {len(house_names)} cung ({', '.join(house_names)}). "
        "Không được nói một cung hoặc các sao của cung đó bị thiếu nếu chúng đã xuất hiện trong [CHART]. "
        "Nếu thiếu căn cứ từ sách, chỉ được nói tài liệu luận giải chưa đủ cho nhận định đó.\n"
        "Hãy viết lại từ đầu: kết luận trực tiếp trong 1--2 câu đầu, sau đó chỉ giữ 2--4 căn cứ liên quan nhất, "
        "không dùng Markdown và không nhắc đến việc đang sửa bản nháp.\n\n"
        f"BẢN NHÁP KHÔNG ĐẠT:\n{draft}"
    )


def safe_error_message(exc: Exception, *, max_chars: int = 300) -> str:
    message = str(exc).strip()
    if not message:
        message = repr(exc)
    return message[:max_chars]
