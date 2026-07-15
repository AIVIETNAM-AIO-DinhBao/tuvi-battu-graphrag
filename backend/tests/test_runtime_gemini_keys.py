from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.rag.gemini_keys import (
    get_primary_runtime_gemini_api_key,
    load_runtime_gemini_api_keys,
    runtime_gemini_key_diagnostics,
)


@dataclass
class FakeSettings:
    GEMINI_API_KEYS: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_API_KEY_2: str = ""
    GEMINI_API_KEY_3: str = ""
    GEMINI_API_KEY_4: str = ""
    GEMINI_API_KEY_5: str = ""
    GEMINI_API_KEY_6: str = ""
    GEMINI_API_KEY_7: str = ""
    GEMINI_API_KEY_8: str = ""


def test_runtime_gemini_keys_prefer_comma_separated_os_env() -> None:
    keys = load_runtime_gemini_api_keys(
        env={"GEMINI_API_KEYS": " env-1, env-2, env-1 ", "GEMINI_API_KEY": "env-single"},
        settings_obj=FakeSettings(GEMINI_API_KEY="settings-single"),
    )

    assert keys[:3] == ["env-1", "env-2", "env-single"]
    assert keys[-1] == "settings-single"


def test_runtime_gemini_keys_fallback_to_settings_when_os_env_missing() -> None:
    settings = FakeSettings(GEMINI_API_KEY="settings-main", GEMINI_API_KEY_2="settings-two")

    assert load_runtime_gemini_api_keys(env={}, settings_obj=settings) == ["settings-main", "settings-two"]
    assert get_primary_runtime_gemini_api_key("unit test", env={}, settings_obj=settings) == "settings-main"


def test_runtime_gemini_keys_support_numbered_env_and_filter_placeholders() -> None:
    keys = load_runtime_gemini_api_keys(
        env={"GEMINI_API_KEY": "test-key", "GEMINI_API_KEY_3": "third", "GEMINI_API_KEY_2": "second"},
        settings_obj=FakeSettings(GEMINI_API_KEY="test-key"),
    )

    assert keys == ["second", "third"]


def test_runtime_gemini_keys_raise_clear_error_when_absent() -> None:
    with pytest.raises(RuntimeError, match="required for Gemini generation"):
        get_primary_runtime_gemini_api_key("Gemini generation", env={}, settings_obj=FakeSettings())


def test_runtime_gemini_key_diagnostics_do_not_expose_secret_values() -> None:
    diagnostics = runtime_gemini_key_diagnostics(
        env={"GEMINI_API_KEY": "secret-main", "GEMINI_API_KEY_2": "secret-two"},
        settings_obj=FakeSettings(GEMINI_API_KEY="settings-secret"),
    )

    assert diagnostics["os_has_gemini_api_key"] is True
    assert diagnostics["os_numbered_key_count"] == 1
    assert diagnostics["settings_has_gemini_api_key"] is True
    assert diagnostics["runtime_key_count"] == 3
    assert "secret-main" not in str(diagnostics)
    assert "settings-secret" not in str(diagnostics)