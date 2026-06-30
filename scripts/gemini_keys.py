"""Shared Gemini API key discovery and safe quota helpers."""

from __future__ import annotations

import os
import re
from typing import Mapping


def load_gemini_api_keys(env: Mapping[str, str | None] | None = None) -> list[str]:
    """Load Gemini keys without logging or exposing raw values.

    Precedence is stable for resume/debug reports:
    1. GEMINI_API_KEYS comma-separated values.
    2. GEMINI_API_KEY.
    3. GEMINI_API_KEY_<number>, sorted by the numeric suffix.
    """
    source = env if env is not None else os.environ
    raw_keys: list[str] = []
    raw_keys.extend(str(source.get("GEMINI_API_KEYS") or "").split(","))
    raw_keys.append(str(source.get("GEMINI_API_KEY") or ""))

    numbered: list[tuple[int, str]] = []
    for key, value in source.items():
        match = re.fullmatch(r"GEMINI_API_KEY_(\d+)", str(key))
        if match:
            numbered.append((int(match.group(1)), str(value or "")))
    raw_keys.extend(value for _, value in sorted(numbered))

    keys: list[str] = []
    seen: set[str] = set()
    for raw_key in raw_keys:
        key = raw_key.strip()
        if not key or key in seen:
            continue
        keys.append(key)
        seen.add(key)
    return keys


def key_usage_labels(api_key_count: int) -> dict[str, int]:
    return {f"key_{index + 1}": 0 for index in range(max(0, api_key_count))}


def is_rate_limit_error(exc: Exception) -> bool:
    message = f"{type(exc).__name__}: {exc}".casefold()
    return any(
        token in message
        for token in (
            "429",
            "quota",
            "rate limit",
            "rate_limit",
            "resourceexhausted",
            "resource exhausted",
            "requests per minute",
            "tokens per minute",
            "rpm",
            "tpm",
        )
    )


def is_daily_quota_error(exc: Exception) -> bool:
    message = f"{type(exc).__name__}: {exc}".casefold()
    return any(
        token in message
        for token in (
            "daily",
            "per day",
            "perday",
            "requests per day",
            "requests_per_day",
            "generatedrequestsperday",
            "generaterequestsperday",
            "free_tier_requests",
            "rpd",
        )
    )
