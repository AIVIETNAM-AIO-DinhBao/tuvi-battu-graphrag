from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

from app.config import settings


NUMBERED_GEMINI_KEY_PREFIX = "GEMINI_API_KEY_"
DEFAULT_NUMBERED_KEY_LIMIT = 8
PLACEHOLDER_KEYS = {"", "test-key", "your_gemini_api_key", "your-gemini-api-key"}


def load_runtime_gemini_api_keys(
    env: Mapping[str, str | None] | None = None,
    settings_obj: Any = settings,
    *,
    include_placeholders: bool = False,
) -> list[str]:
    """Load Gemini API keys for backend runtime without exposing secrets.

    Runtime clients used to read only ``os.environ``. In local FastAPI runs,
    pydantic-settings can load ``.env`` into ``settings`` without exporting the
    same values back to ``os.environ``; that caused chat generation to fallback
    even when ``.env`` contained valid keys. This helper reads both sources and
    supports the numbered key convention used by ingestion scripts.
    """

    source = env if env is not None else os.environ
    raw_keys: list[str] = []

    raw_keys.extend(_split_keys(source.get("GEMINI_API_KEYS")))
    raw_keys.append(str(source.get("GEMINI_API_KEY") or ""))
    raw_keys.extend(_numbered_env_keys(source))

    raw_keys.extend(_split_keys(getattr(settings_obj, "GEMINI_API_KEYS", "")))
    raw_keys.append(str(getattr(settings_obj, "GEMINI_API_KEY", "") or ""))
    raw_keys.extend(_numbered_settings_keys(settings_obj))

    keys: list[str] = []
    for raw_key in raw_keys:
        key = str(raw_key or "").strip().strip('"').strip("'")
        if not key:
            continue
        if not include_placeholders and key.lower() in PLACEHOLDER_KEYS:
            continue
        if key not in keys:
            keys.append(key)
    return keys


def get_primary_runtime_gemini_api_key(
    purpose: str,
    *,
    explicit_api_key: str | None = None,
    env: Mapping[str, str | None] | None = None,
    settings_obj: Any = settings,
) -> str:
    if explicit_api_key:
        return explicit_api_key.strip()
    keys = load_runtime_gemini_api_keys(env=env, settings_obj=settings_obj)
    if keys:
        return keys[0]
    raise RuntimeError(f"GEMINI_API_KEY or GEMINI_API_KEYS is required for {purpose}.")


def runtime_gemini_key_diagnostics(
    env: Mapping[str, str | None] | None = None,
    settings_obj: Any = settings,
) -> dict[str, Any]:
    source = env if env is not None else os.environ
    return {
        "os_has_gemini_api_keys": bool(str(source.get("GEMINI_API_KEYS") or "").strip()),
        "os_has_gemini_api_key": bool(str(source.get("GEMINI_API_KEY") or "").strip()),
        "os_numbered_key_count": _usable_key_count(_numbered_env_keys(source)),
        "settings_has_gemini_api_keys": bool(str(getattr(settings_obj, "GEMINI_API_KEYS", "") or "").strip()),
        "settings_has_gemini_api_key": bool(str(getattr(settings_obj, "GEMINI_API_KEY", "") or "").strip()),
        "settings_numbered_key_count": _usable_key_count(_numbered_settings_keys(settings_obj)),
        "runtime_key_count": len(load_runtime_gemini_api_keys(env=source, settings_obj=settings_obj)),
    }


def _split_keys(value: str | None) -> list[str]:
    return [key.strip() for key in str(value or "").split(",") if key.strip()]


def _numbered_env_keys(source: Mapping[str, str | None]) -> list[str]:
    numbered: list[tuple[int, str]] = []
    for name, value in source.items():
        if not name.startswith(NUMBERED_GEMINI_KEY_PREFIX):
            continue
        suffix = name.removeprefix(NUMBERED_GEMINI_KEY_PREFIX)
        if not suffix.isdigit():
            continue
        numbered.append((int(suffix), str(value or "")))
    return [value for _index, value in sorted(numbered)]


def _numbered_settings_keys(settings_obj: Any) -> list[str]:
    keys: list[str] = []
    for index in range(2, DEFAULT_NUMBERED_KEY_LIMIT + 1):
        keys.append(str(getattr(settings_obj, f"GEMINI_API_KEY_{index}", "") or ""))
    return keys


def _usable_key_count(values: list[str]) -> int:
    return sum(
        1
        for value in values
        if (key := str(value or "").strip().strip('"').strip("'")) and key.lower() not in PLACEHOLDER_KEYS
    )