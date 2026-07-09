from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Protocol

from app.rag.config import ExperimentConfig
from app.rag.query_entities import normalize_lookup


@dataclass(frozen=True)
class RewriteResult:
    rewritten_query: str
    changed: bool
    reason: str = ""
    domain: str = "TUVI"
    raw_response: str | None = None
    fallback_reason: str | None = None


class QueryRewriter(Protocol):
    def rewrite(self, query: str, *, chart_data: dict[str, Any], config: ExperimentConfig) -> RewriteResult:
        ...


class PassthroughQueryRewriter:
    def rewrite(self, query: str, *, chart_data: dict[str, Any], config: ExperimentConfig) -> RewriteResult:
        return RewriteResult(rewritten_query=query, changed=False, reason="passthrough")


class GeminiQueryRewriter:
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
        raise RuntimeError("GEMINI_API_KEY or GEMINI_API_KEYS is required for Gemini query rewrite.")

    def rewrite(self, query: str, *, chart_data: dict[str, Any], config: ExperimentConfig) -> RewriteResult:
        try:
            import google.generativeai as genai
        except Exception as exc:
            raise RuntimeError("google-generativeai is required for Gemini query rewrite.") from exc

        rewrite_config = config.query_rewrite
        genai.configure(api_key=self._api_key())
        model = genai.GenerativeModel(rewrite_config.model)
        prompt = build_rewrite_prompt(query, chart_data)
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": rewrite_config.temperature,
                "max_output_tokens": rewrite_config.max_output_tokens,
                "response_mime_type": "application/json",
            },
        )
        raw_text = str(getattr(response, "text", "") or "")
        payload = parse_rewrite_payload(raw_text)
        rewritten_query = str(payload.get("rewritten_query") or "").strip()
        return RewriteResult(
            rewritten_query=rewritten_query,
            changed=bool(payload.get("changed", rewritten_query != query)),
            reason=str(payload.get("reason") or ""),
            domain=str(payload.get("domain") or "TUVI"),
            raw_response=raw_text,
        )


def build_rewrite_prompt(query: str, chart_data: dict[str, Any]) -> str:
    chart_hint = chart_data.get("chart_type") or chart_data.get("chart_system") or "TUVI"
    return (
        "Bạn là query rewriter cho hệ thống hỏi đáp Tử Vi. "
        "Chỉ làm rõ câu hỏi trong domain TUVI; không thêm luận đoán mới. "
        "Giữ nguyên tên sao, tên cung, tổ hợp, Tứ Hóa và thuật ngữ Tử Vi.\n"
        f"chart_type: {chart_hint}\n"
        f"query: {query}\n"
        "Output JSON strict dạng "
        "{\"rewritten_query\":\"...\",\"changed\":false,\"reason\":\"...\",\"domain\":\"TUVI\"}."
    )


def parse_rewrite_payload(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    payload = json.loads(cleaned)
    if not isinstance(payload, dict):
        raise ValueError("Rewrite response must be a JSON object.")
    return payload


def contains_term(text: str, term: str) -> bool:
    return normalize_lookup(term) in normalize_lookup(text)


def guard_rewrite_result(
    original_query: str,
    result: RewriteResult,
    *,
    terms_to_preserve: list[str],
) -> RewriteResult:
    rewritten_query = " ".join(result.rewritten_query.split())
    if not rewritten_query:
        return RewriteResult(
            rewritten_query=original_query,
            changed=False,
            reason=result.reason,
            domain=result.domain,
            raw_response=result.raw_response,
            fallback_reason="empty_rewrite",
        )
    if result.domain != "TUVI":
        return RewriteResult(
            rewritten_query=original_query,
            changed=False,
            reason=result.reason,
            domain=result.domain,
            raw_response=result.raw_response,
            fallback_reason="out_of_domain",
        )
    missing_terms = [term for term in terms_to_preserve if not contains_term(rewritten_query, term)]
    if missing_terms:
        return RewriteResult(
            rewritten_query=original_query,
            changed=False,
            reason=result.reason,
            domain=result.domain,
            raw_response=result.raw_response,
            fallback_reason="missing_terms:" + ",".join(missing_terms),
        )
    return RewriteResult(
        rewritten_query=rewritten_query,
        changed=rewritten_query != original_query,
        reason=result.reason,
        domain=result.domain,
        raw_response=result.raw_response,
    )


def make_default_query_rewriter(config: ExperimentConfig) -> QueryRewriter:
    if config.query_rewrite.backend == "gemini":
        return GeminiQueryRewriter()
    return PassthroughQueryRewriter()
