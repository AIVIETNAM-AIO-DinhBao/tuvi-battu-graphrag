"""Orchestrate W3-INGEST-07 full-corpus baseline ingest.

Default mode is safe: build a command manifest without calling Gemini or DBs.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from gemini_keys import load_gemini_api_keys


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATASET_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset"
DEFAULT_SOURCES = ["TVKL", "TVNL", "TVHS", "TVGM"]
DEFAULT_STRATEGIES = ["chunk_fixed_512", "chunk_structure_parent_child", "chunk_semantic_embedding"]
DEFAULT_SMOKE_QUERY = "Thiên Mã tại Quan Lộc"


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def script_path(name: str) -> Path:
    return ROOT_DIR / "scripts" / name


def read_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def as_command(argv: list[Any]) -> list[str]:
    return [str(item) for item in argv]


def command_record(
    *,
    command_id: str,
    phase: str,
    argv: list[Any],
    mode: str,
    source_id: str | None,
    strategy_id: str,
    gemini_api_key_count: int,
    requires_gemini: bool,
    summary_output: Path | None = None,
    skip_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "command_id": command_id,
        "gemini_api_key_count": gemini_api_key_count,
        "mode": mode,
        "phase": phase,
        "requires_gemini": requires_gemini,
        "skip_reason": skip_reason,
        "source_id": source_id,
        "strategy_id": strategy_id,
        "summary_output": str(summary_output) if summary_output else None,
        "argv": as_command(argv),
    }


def build_commands(args: argparse.Namespace, gemini_api_key_count: int) -> list[dict[str, Any]]:
    chunks_dir = args.chunks_dir
    entities_dir = args.entities_dir
    reports_dir = args.reports_dir
    state_dir = reports_dir / args.mode
    corpus_inputs = [args.dataset_dir / "corpus" / source for source in args.sources]
    commands: list[dict[str, Any]] = []

    for strategy in args.strategies:
        strategy_chunks_dir = chunks_dir / strategy
        chunk_summary = reports_dir / f"{strategy}_chunk_summary.json"
        chunk_argv: list[Any] = [
            sys.executable,
            script_path("chunk_text.py"),
            "--input",
            *corpus_inputs,
            "--chunking-strategy",
            strategy,
            "--output",
            strategy_chunks_dir,
            "--summary-output",
            chunk_summary,
        ]
        if strategy == "chunk_semantic_embedding":
            chunk_argv.extend(["--semantic-report-output", reports_dir / f"{strategy}_semantic_similarity_report.json"])
            if args.mode != "production" or args.mock_embedding:
                chunk_argv.append("--mock-embedding")
        commands.append(
            command_record(
                command_id=f"{strategy}:chunking",
                phase="chunking",
                argv=chunk_argv,
                mode=args.mode,
                source_id=None,
                strategy_id=strategy,
                gemini_api_key_count=gemini_api_key_count,
                requires_gemini=strategy == "chunk_semantic_embedding" and "--mock-embedding" not in chunk_argv,
                summary_output=chunk_summary,
            )
        )

        strategy_entities_dir = entities_dir / strategy
        entity_output = strategy_entities_dir / f"{strategy}_entities.jsonl"
        entity_argv: list[Any] = [
            sys.executable,
            script_path("extract_entities.py"),
            "--input",
            strategy_chunks_dir,
            "--output",
            entity_output,
            "--chunking-strategy",
            strategy,
            "--review-output",
            reports_dir / f"{strategy}_entity_review.json",
            "--partial-summary-output",
            reports_dir / f"{strategy}_entity_summary.json",
            "--state-output",
            state_dir / f"{strategy}_entity_state.json",
            "--resume",
        ]
        if args.mode != "production" or args.mock_llm:
            entity_argv.append("--mock-llm")
        commands.append(
            command_record(
                command_id=f"{strategy}:entity",
                phase="entity_extraction",
                argv=entity_argv,
                mode=args.mode,
                source_id=None,
                strategy_id=strategy,
                gemini_api_key_count=gemini_api_key_count,
                requires_gemini="--mock-llm" not in entity_argv,
                summary_output=reports_dir / f"{strategy}_entity_summary.json",
            )
        )

        graph_argv: list[Any] = [
            sys.executable,
            script_path("write_graph_provenance.py"),
            "--chunks-input",
            strategy_chunks_dir,
            "--entities-input",
            entity_output,
            "--chunking-strategy",
            strategy,
            "--summary-output",
            reports_dir / f"{strategy}_graph_write_summary.json",
            "--relation-review-output",
            reports_dir / f"{strategy}_relation_review.json",
            "--review-sample-size",
            "20",
            "--state-output",
            state_dir / f"{strategy}_graph_relation_state.json",
            "--resume",
        ]
        if args.mode != "production":
            graph_argv.append("--dry-run")
        if args.mode != "production" or args.mock_llm:
            graph_argv.append("--mock-llm")
        commands.append(
            command_record(
                command_id=f"{strategy}:graph",
                phase="graph_relation",
                argv=graph_argv,
                mode=args.mode,
                source_id=None,
                strategy_id=strategy,
                gemini_api_key_count=gemini_api_key_count,
                requires_gemini="--mock-llm" not in graph_argv,
                summary_output=reports_dir / f"{strategy}_graph_write_summary.json",
            )
        )

        for source in args.sources:
            embed_argv: list[Any] = [
                sys.executable,
                script_path("embed_chunks.py"),
                "--source-id",
                source,
                "--chunking-strategy",
                strategy,
                "--summary-output",
                reports_dir / f"embed_{source}_{strategy}.json",
                "--retrieval-smoke-output",
                reports_dir / f"retrieval_{source}_{strategy}.json",
                "--smoke-query",
                args.smoke_query,
            ]
            if args.force_embedding:
                embed_argv.append("--force")
            if args.mode != "production" or args.mock_embedding:
                embed_argv.append("--mock-embedding")
            commands.append(
                command_record(
                    command_id=f"{source}:{strategy}:embed_retrieval",
                    phase="embed_retrieval",
                    argv=embed_argv,
                    mode=args.mode,
                    source_id=source,
                    strategy_id=strategy,
                    gemini_api_key_count=gemini_api_key_count,
                    requires_gemini="--mock-embedding" not in embed_argv,
                    summary_output=reports_dir / f"embed_{source}_{strategy}.json",
                    skip_reason="skipped_requires_db" if args.mode == "dry-run" else None,
                )
            )
    return commands


def command_summary_completed(command: dict[str, Any]) -> bool:
    summary_output = command.get("summary_output")
    if not summary_output:
        return True
    path = Path(str(summary_output))
    if not path.exists():
        return False
    summary = read_json(path)
    return summary.get("completed") is not False


def assert_command_summary_completed(command: dict[str, Any]) -> None:
    summary_output = command.get("summary_output")
    if not summary_output:
        return
    path = Path(str(summary_output))
    if not path.exists():
        raise RuntimeError(f"Command {command['command_id']} did not write expected summary {path}.")
    summary = read_json(path)
    if summary.get("completed") is False:
        error_count = summary.get("error_count")
        disabled_key_count = summary.get("disabled_key_count")
        quota_failover_count = summary.get("quota_failover_count")
        details = {
            "disabled_key_count": disabled_key_count,
            "error_count": error_count,
            "quota_failover_count": quota_failover_count,
            "summary_output": str(path),
        }
        raise RuntimeError(f"Command {command['command_id']} wrote incomplete summary: {details}")


def run_subprocess(command: dict[str, Any]) -> dict[str, Any]:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    result = subprocess.run(
        command["argv"],
        cwd=ROOT_DIR,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        raise RuntimeError(
            f"Command {command['command_id']} failed with exit code {result.returncode}: "
            f"{stderr or stdout}"
        )
    return {"returncode": result.returncode}


def execute_commands(
    commands: list[dict[str, Any]],
    *,
    args: argparse.Namespace,
    state_path: Path,
) -> dict[str, Any]:
    state = read_json(state_path, {"commands": {}})
    state.setdefault("commands", {})
    executed = 0
    skipped = 0
    for command in commands:
        command_state = state["commands"].get(command["command_id"], {})
        if (
            args.resume
            and not args.force
            and command_state.get("status") == "completed"
            and command_state.get("mode") == args.mode
            and command_summary_completed(command)
        ):
            skipped += 1
            continue
        if command.get("skip_reason"):
            state["commands"][command["command_id"]] = {
                "completed_at": utc_now(),
                "mode": args.mode,
                "phase": command["phase"],
                "status": "skipped",
                "skip_reason": command["skip_reason"],
            }
            skipped += 1
            write_json(state_path, state)
            continue

        state["commands"][command["command_id"]] = {
            "gemini_api_key_count": command["gemini_api_key_count"],
            "mode": args.mode,
            "phase": command["phase"],
            "started_at": utc_now(),
            "status": "running",
        }
        write_json(state_path, state)
        try:
            run_subprocess(command)
            assert_command_summary_completed(command)
        except Exception as exc:
            state["commands"][command["command_id"]].update(
                {
                    "error": f"{type(exc).__name__}: {exc}",
                    "failed_at": utc_now(),
                    "status": "partial",
                }
            )
            state["last_completed_unit"] = command["command_id"]
            write_json(state_path, state)
            raise
        state["commands"][command["command_id"]].update({"completed_at": utc_now(), "status": "completed"})
        state["last_completed_unit"] = command["command_id"]
        executed += 1
        write_json(state_path, state)
    return {"executed_command_count": executed, "skipped_command_count": skipped}


def validate_production_key_availability(commands: list[dict[str, Any]], gemini_api_key_count: int) -> None:
    if gemini_api_key_count > 0:
        return
    if any(command["requires_gemini"] for command in commands):
        raise ValueError("At least one Gemini API key is required for production mode.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run or plan W3-INGEST-07 full-corpus ingest.")
    parser.add_argument("--mode", choices=["plan", "dry-run", "production"], default="plan")
    parser.add_argument("--sources", nargs="+", default=DEFAULT_SOURCES)
    parser.add_argument("--strategies", nargs="+", default=DEFAULT_STRATEGIES)
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    parser.add_argument("--chunks-dir", type=Path, default=DEFAULT_DATASET_DIR / "chunks")
    parser.add_argument("--entities-dir", type=Path, default=DEFAULT_DATASET_DIR / "entities")
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_DATASET_DIR / "reports" / "w3_ingest_07")
    parser.add_argument("--manifest-output", type=Path, default=None)
    parser.add_argument("--summary-output", type=Path, default=None)
    parser.add_argument("--state-output", type=Path, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--force-embedding", action="store_true")
    parser.add_argument("--mock-llm", action="store_true")
    parser.add_argument("--mock-embedding", action="store_true")
    parser.add_argument("--smoke-query", default=DEFAULT_SMOKE_QUERY)
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> dict[str, Any]:
    load_dotenv(ROOT_DIR / ".env")
    args = parse_args(argv)
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    manifest_output = args.manifest_output or args.reports_dir / "w3_ingest_07_command_manifest.json"
    summary_output = args.summary_output or args.reports_dir / "w3_ingest_07_run_summary.json"
    state_output = args.state_output or args.reports_dir / "w3_ingest_07_state.json"

    gemini_api_key_count = len(load_gemini_api_keys())
    commands = build_commands(args, gemini_api_key_count)
    manifest = {
        "command_count": len(commands),
        "commands": commands,
        "generated_at": utc_now(),
        "gemini_api_key_count": gemini_api_key_count,
        "mode": args.mode,
    }
    write_json(manifest_output, manifest)

    if args.mode == "production":
        validate_production_key_availability(commands, gemini_api_key_count)

    execution = {"executed_command_count": 0, "skipped_command_count": 0}
    completed = True
    error: str | None = None
    if args.mode != "plan":
        try:
            execution = execute_commands(commands, args=args, state_path=state_output)
        except Exception as exc:
            completed = False
            error = f"{type(exc).__name__}: {exc}"
            if args.mode == "production":
                summary = {
                    **execution,
                    "command_count": len(commands),
                    "completed": completed,
                    "error": error,
                    "generated_at": utc_now(),
                    "gemini_api_key_count": gemini_api_key_count,
                    "manifest_output": str(manifest_output),
                    "mode": args.mode,
                    "state_output": str(state_output),
                }
                write_json(summary_output, summary)
                raise

    summary = {
        **execution,
        "command_count": len(commands),
        "completed": completed,
        "error": error,
        "generated_at": utc_now(),
        "gemini_api_key_count": gemini_api_key_count,
        "manifest_output": str(manifest_output),
        "mode": args.mode,
        "state_output": str(state_output),
    }
    write_json(summary_output, summary)
    return summary


def cli(argv: list[str] | None = None) -> int:
    try:
        summary = run(argv)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
