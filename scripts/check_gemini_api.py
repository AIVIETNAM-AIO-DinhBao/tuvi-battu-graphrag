"""Preflight Gemini API keys and model access without running ingest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from gemini_keys import load_gemini_api_keys


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PROMPT = (
    "Tra loi ngan gon bang JSON: "
    "{\"ok\":true,\"entities\":[\"Thai Duong\",\"Thien Luong\"]}"
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def summarize_exception(exc: Exception, *, max_length: int = 1000) -> str:
    message = f"{type(exc).__name__}: {exc}".replace("\n", " ").strip()
    if len(message) > max_length:
        return message[: max_length - 3].rstrip() + "..."
    return message


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Gemini API keys and model access.")
    parser.add_argument("--model", default="gemini-2.0-flash-lite")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--list-models", action="store_true")
    parser.add_argument("--max-models", type=int, default=20)
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> dict[str, Any]:
    load_dotenv(ROOT_DIR / ".env")
    args = parse_args(argv)
    try:
        import google.generativeai as genai  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("google-generativeai is not installed.") from exc

    keys = load_gemini_api_keys()
    if not keys:
        raise ValueError("No Gemini API keys found in GEMINI_API_KEYS/GEMINI_API_KEY_N.")

    checks: list[dict[str, Any]] = []
    for index, api_key in enumerate(keys, start=1):
        label = f"key_{index}"
        result: dict[str, Any] = {"key_label": label, "model": args.model, "ok": False}
        try:
            genai.configure(api_key=api_key)
            if args.list_models:
                models = [model.name for model in genai.list_models()]
                result["models_sample"] = models[: max(0, args.max_models)]
                result["model_available_in_list"] = any(
                    name.endswith(f"/{args.model}") or name == args.model for name in models
                )
            model = genai.GenerativeModel(args.model)
            response = model.generate_content(args.prompt)
            result["ok"] = True
            result["response_excerpt"] = str(getattr(response, "text", ""))[:500]
        except Exception as exc:  # noqa: BLE001 - preflight must report provider errors.
            result["error"] = summarize_exception(exc)
        checks.append(result)

    return {
        "checked_key_count": len(keys),
        "checks": checks,
        "model": args.model,
        "ok_key_count": sum(1 for item in checks if item.get("ok")),
    }


def cli(argv: list[str] | None = None) -> int:
    try:
        summary = run(argv)
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["ok_key_count"] > 0 else 2


if __name__ == "__main__":
    raise SystemExit(cli())
