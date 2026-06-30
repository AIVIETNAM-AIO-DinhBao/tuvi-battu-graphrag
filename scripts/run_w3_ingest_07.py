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
LOCAL_KAGGLE_STRATEGIES = [
    "chunk_fixed_512",
    "chunk_structure_parent_child",
    "chunk_semantic_embedding_bge_m3",
]
LOCAL_KAGGLE_EMBEDDING_MODEL = "BAAI/bge-m3"
LOCAL_KAGGLE_EMBEDDING_DIM = 1024
LOCAL_KAGGLE_LLM_MODEL = "Qwen/Qwen2.5-7B-Instruct"
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


def resolve_profile_args(args: argparse.Namespace) -> argparse.Namespace:
    profile = getattr(args, "profile", "gemini")
    if args.strategies is None:
        args.strategies = list(LOCAL_KAGGLE_STRATEGIES if profile == "local-kaggle" else DEFAULT_STRATEGIES)
    if args.chunks_dir is None:
        args.chunks_dir = (
            args.dataset_dir / "local_kaggle" / "chunks"
            if profile == "local-kaggle"
            else args.dataset_dir / "chunks"
        )
    if args.entities_dir is None:
        args.entities_dir = (
            args.dataset_dir / "local_kaggle" / "entities"
            if profile == "local-kaggle"
            else args.dataset_dir / "entities"
        )
    if args.reports_dir is None:
        args.reports_dir = (
            args.dataset_dir / "reports" / "w3_ingest_07_local_kaggle"
            if profile == "local-kaggle"
            else args.dataset_dir / "reports" / "w3_ingest_07"
        )
    return args


def command_record(
    *,
    command_id: str,
    phase: str,
    argv: list[Any],
    mode: str,
    profile: str,
    source_id: str | None,
    strategy_id: str,
    gemini_api_key_count: int,
    requires_gemini: bool,
    backend: str | None = None,
    model: str | None = None,
    expected_dim: int | None = None,
    summary_output: Path | None = None,
    skip_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "backend": backend,
        "command_id": command_id,
        "expected_dim": expected_dim,
        "gemini_api_key_count": gemini_api_key_count,
        "mode": mode,
        "model": model,
        "phase": phase,
        "profile": profile,
        "requires_gemini": requires_gemini,
        "skip_reason": skip_reason,
        "source_id": source_id,
        "strategy_id": strategy_id,
        "summary_output": str(summary_output) if summary_output else None,
        "argv": as_command(argv),
    }


def build_commands(args: argparse.Namespace, gemini_api_key_count: int) -> list[dict[str, Any]]:
    args = resolve_profile_args(args)
    chunks_dir = args.chunks_dir
    entities_dir = args.entities_dir
    reports_dir = args.reports_dir
    state_dir = reports_dir / args.mode
    corpus_inputs = [args.dataset_dir / "corpus" / source for source in args.sources]
    commands: list[dict[str, Any]] = []
    local_profile = args.profile == "local-kaggle"

    for strategy in args.strategies:
        strategy_chunks_dir = chunks_dir / strategy
        chunk_summary = reports_dir / f"{strategy}_chunk_summary.json"
        semantic_strategy = strategy in {"chunk_semantic_embedding", "chunk_semantic_embedding_bge_m3"}
        chunk_argv: list[Any] = [
            sys.executable,
            "-B",
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
        chunk_backend: str | None = None
        chunk_model: str | None = None
        chunk_expected_dim: int | None = None
        if semantic_strategy:
            chunk_argv.extend(["--semantic-report-output", reports_dir / f"{strategy}_semantic_similarity_report.json"])
            if args.mode == "dry-run" or args.mock_embedding:
                chunk_argv.append("--mock-embedding")
                chunk_backend = "mock"
            elif local_profile:
                chunk_backend = "local"
                chunk_model = args.local_embedding_model
                chunk_expected_dim = args.local_embedding_dim
                chunk_argv.extend(
                    [
                        "--embedding-backend",
                        "local",
                        "--local-embedding-model",
                        args.local_embedding_model,
                        "--local-embedding-batch-size",
                        str(args.local_embedding_batch_size),
                        "--local-embedding-implementation",
                        args.local_embedding_implementation,
                    ]
                )
                if args.local_embedding_device:
                    chunk_argv.extend(["--local-embedding-device", args.local_embedding_device])
                if not args.local_embedding_normalize:
                    chunk_argv.append("--no-local-embedding-normalize")
            else:
                chunk_backend = "gemini"
                chunk_model = "gemini-embedding-2"
                chunk_expected_dim = 768
        commands.append(
            command_record(
                command_id=f"{strategy}:chunking",
                phase="chunking",
                argv=chunk_argv,
                mode=args.mode,
                profile=args.profile,
                source_id=None,
                strategy_id=strategy,
                gemini_api_key_count=gemini_api_key_count,
                requires_gemini=semantic_strategy and chunk_backend == "gemini",
                backend=chunk_backend,
                model=chunk_model,
                expected_dim=chunk_expected_dim,
                summary_output=chunk_summary,
            )
        )

        strategy_entities_dir = entities_dir / strategy
        entity_output = strategy_entities_dir / f"{strategy}_entities.jsonl"
        entity_argv: list[Any] = [
            sys.executable,
            "-B",
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
        if args.mode == "dry-run" or args.mock_llm:
            entity_argv.append("--mock-llm")
            entity_backend = "mock"
            entity_model = "mock-llm-augmentation"
        elif local_profile:
            entity_backend = "local"
            entity_model = args.local_llm_model
            entity_argv.extend(
                [
                    "--llm-backend",
                    "local",
                    "--model",
                    args.local_llm_model,
                    "--local-llm-model",
                    args.local_llm_model,
                    "--local-llm-quantization",
                    args.local_llm_quantization,
                    "--local-llm-max-new-tokens",
                    str(args.local_llm_max_new_tokens),
                    "--local-llm-temperature",
                    str(args.local_llm_temperature),
                    "--local-llm-top-p",
                    str(args.local_llm_top_p),
                    "--local-llm-max-json-retries",
                    str(args.local_llm_max_json_retries),
                ]
            )
            if args.local_llm_device:
                entity_argv.extend(["--local-llm-device", args.local_llm_device])
        else:
            entity_backend = "gemini"
            entity_model = None
        commands.append(
            command_record(
                command_id=f"{strategy}:entity",
                phase="entity_extraction",
                argv=entity_argv,
                mode=args.mode,
                profile=args.profile,
                source_id=None,
                strategy_id=strategy,
                gemini_api_key_count=gemini_api_key_count,
                requires_gemini=entity_backend == "gemini",
                backend=entity_backend,
                model=entity_model,
                summary_output=reports_dir / f"{strategy}_entity_summary.json",
            )
        )

        graph_argv: list[Any] = [
            sys.executable,
            "-B",
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
        if args.mode != "production" or local_profile:
            graph_argv.append("--dry-run")
        if args.mode == "dry-run" or args.mock_llm:
            graph_argv.append("--mock-llm")
            graph_backend = "mock"
            graph_model = "mock-relation-llm"
        elif local_profile:
            graph_backend = "local"
            graph_model = args.local_llm_model
            graph_argv.extend(
                [
                    "--llm-backend",
                    "local",
                    "--model",
                    args.local_llm_model,
                    "--local-llm-model",
                    args.local_llm_model,
                    "--local-llm-quantization",
                    args.local_llm_quantization,
                    "--local-llm-max-new-tokens",
                    str(args.local_llm_max_new_tokens),
                    "--local-llm-temperature",
                    str(args.local_llm_temperature),
                    "--local-llm-top-p",
                    str(args.local_llm_top_p),
                    "--local-llm-max-json-retries",
                    str(args.local_llm_max_json_retries),
                ]
            )
            if args.local_llm_device:
                graph_argv.extend(["--local-llm-device", args.local_llm_device])
        else:
            graph_backend = "gemini"
            graph_model = "gemini-2.0-flash-lite"
        commands.append(
            command_record(
                command_id=f"{strategy}:graph",
                phase="graph_relation",
                argv=graph_argv,
                mode=args.mode,
                profile=args.profile,
                source_id=None,
                strategy_id=strategy,
                gemini_api_key_count=gemini_api_key_count,
                requires_gemini=graph_backend == "gemini",
                backend=graph_backend,
                model=graph_model,
                summary_output=reports_dir / f"{strategy}_graph_write_summary.json",
            )
        )

        for source in args.sources:
            if local_profile:
                embeddings_dir = args.dataset_dir / "local_kaggle" / "embeddings" / strategy
                embed_argv = [
                    sys.executable,
                    "-B",
                    script_path("embed_chunks.py"),
                    "--chunks-input",
                    strategy_chunks_dir,
                    "--source-id",
                    source,
                    "--chunking-strategy",
                    strategy,
                    "--output",
                    embeddings_dir / f"{source}_{strategy}_embeddings.jsonl",
                    "--summary-output",
                    reports_dir / f"embed_{source}_{strategy}.json",
                    "--retrieval-smoke-output",
                    reports_dir / f"retrieval_{source}_{strategy}.json",
                    "--state-output",
                    state_dir / f"{source}_{strategy}_embedding_state.json",
                    "--resume",
                    "--smoke-query",
                    args.smoke_query,
                    "--embedding-backend",
                    "local",
                    "--model",
                    args.local_embedding_model,
                    "--expected-dim",
                    str(args.local_embedding_dim),
                    "--local-embedding-model",
                    args.local_embedding_model,
                    "--local-embedding-batch-size",
                    str(args.local_embedding_batch_size),
                    "--local-embedding-implementation",
                    args.local_embedding_implementation,
                    "--vector-index-name",
                    args.local_vector_index_name,
                ]
                if args.local_embedding_device:
                    embed_argv.extend(["--local-embedding-device", args.local_embedding_device])
                if not args.local_embedding_normalize:
                    embed_argv.append("--no-local-embedding-normalize")
                embed_backend = "local"
                embed_model = args.local_embedding_model
                embed_dim = args.local_embedding_dim
                embed_skip_reason = "skipped_local_embedding_dry_run" if args.mode == "dry-run" else None
            else:
                embed_argv = [
                    sys.executable,
                    "-B",
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
                    embed_backend = "mock"
                    embed_model = "mock-embedding"
                else:
                    embed_backend = "gemini"
                    embed_model = "gemini-embedding-2"
                embed_dim = 768
                embed_skip_reason = "skipped_requires_db" if args.mode == "dry-run" else None
            commands.append(
                command_record(
                    command_id=f"{source}:{strategy}:embed_retrieval",
                    phase="embed_retrieval",
                    argv=embed_argv,
                    mode=args.mode,
                    profile=args.profile,
                    source_id=source,
                    strategy_id=strategy,
                    gemini_api_key_count=gemini_api_key_count,
                    requires_gemini=embed_backend == "gemini",
                    backend=embed_backend,
                    model=embed_model,
                    expected_dim=embed_dim,
                    summary_output=reports_dir / f"embed_{source}_{strategy}.json",
                    skip_reason=embed_skip_reason,
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
            and command_state.get("profile", args.profile) == args.profile
            and command_summary_completed(command)
        ):
            skipped += 1
            continue
        if command.get("skip_reason"):
            state["commands"][command["command_id"]] = {
                "completed_at": utc_now(),
                "mode": args.mode,
                "phase": command["phase"],
                "profile": args.profile,
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
            "profile": args.profile,
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
    parser.add_argument("--profile", choices=["gemini", "local-kaggle"], default="gemini")
    parser.add_argument("--sources", nargs="+", default=DEFAULT_SOURCES)
    parser.add_argument("--strategies", nargs="+", default=None)
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    parser.add_argument("--chunks-dir", type=Path, default=None)
    parser.add_argument("--entities-dir", type=Path, default=None)
    parser.add_argument("--reports-dir", type=Path, default=None)
    parser.add_argument("--manifest-output", type=Path, default=None)
    parser.add_argument("--summary-output", type=Path, default=None)
    parser.add_argument("--state-output", type=Path, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--force-embedding", action="store_true")
    parser.add_argument("--mock-llm", action="store_true")
    parser.add_argument("--mock-embedding", action="store_true")
    parser.add_argument("--local-embedding-model", default=LOCAL_KAGGLE_EMBEDDING_MODEL)
    parser.add_argument("--local-embedding-dim", type=int, default=LOCAL_KAGGLE_EMBEDDING_DIM)
    parser.add_argument("--local-embedding-device", default=None)
    parser.add_argument("--local-embedding-batch-size", type=int, default=16)
    parser.add_argument(
        "--local-embedding-implementation",
        choices=["auto", "flagembedding", "sentence-transformers"],
        default="auto",
    )
    parser.add_argument("--local-embedding-normalize", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--local-vector-index-name", default="chunkVectorBgeM3")
    parser.add_argument("--local-llm-model", default=LOCAL_KAGGLE_LLM_MODEL)
    parser.add_argument("--local-llm-device", default=None)
    parser.add_argument("--local-llm-quantization", choices=["4bit", "8bit", "none"], default="4bit")
    parser.add_argument("--local-llm-max-new-tokens", type=int, default=1024)
    parser.add_argument("--local-llm-temperature", type=float, default=0.0)
    parser.add_argument("--local-llm-top-p", type=float, default=0.9)
    parser.add_argument("--local-llm-max-json-retries", type=int, default=1)
    parser.add_argument("--smoke-query", default=DEFAULT_SMOKE_QUERY)
    return resolve_profile_args(parser.parse_args(argv))


def run(argv: list[str] | None = None) -> dict[str, Any]:
    load_dotenv(ROOT_DIR / ".env")
    args = resolve_profile_args(parse_args(argv))
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
        "profile": args.profile,
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
                    "profile": args.profile,
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
        "profile": args.profile,
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
