import json
import sys
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

import gemini_keys  # noqa: E402
import run_w3_ingest_07 as runner  # noqa: E402


def smoke_dir(name: str) -> Path:
    path = ROOT_DIR / "pytest-cache-files-w3-ingest-07" / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_shared_gemini_key_loader_sorts_numbered_keys_and_dedupes() -> None:
    keys = gemini_keys.load_gemini_api_keys(
        {
            "GEMINI_API_KEYS": "key-c, key-a, key-c",
            "GEMINI_API_KEY": "key-a",
            "GEMINI_API_KEY_10": "key-j",
            "GEMINI_API_KEY_2": "key-b",
            "GEMINI_API_KEY_3": "key-c",
            "GEMINI_API_KEY_EXTRA": "ignored",
        }
    )

    assert keys == ["key-c", "key-a", "key-b", "key-j"]


def test_plan_mode_writes_manifest_without_running_subprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner, "load_gemini_api_keys", lambda: ["key-1", "key-2", "key-3", "key-4"])
    monkeypatch.setattr(
        runner,
        "run_subprocess",
        lambda command: pytest.fail(f"plan mode executed {command['command_id']}"),
    )
    work_dir = smoke_dir("plan-mode")
    reports_dir = work_dir / "reports"

    summary = runner.run(
        [
            "--mode",
            "plan",
            "--dataset-dir",
            str(work_dir / "dataset"),
            "--chunks-dir",
            str(work_dir / "chunks"),
            "--entities-dir",
            str(work_dir / "entities"),
            "--reports-dir",
            str(reports_dir),
        ]
    )

    manifest = json.loads((reports_dir / "w3_ingest_07_command_manifest.json").read_text(encoding="utf-8"))
    assert summary["completed"] is True
    assert manifest["gemini_api_key_count"] == 4
    assert manifest["command_count"] == 21
    assert sum(1 for command in manifest["commands"] if command["phase"] == "embed_retrieval") == 12
    semantic_chunk = next(
        command for command in manifest["commands"] if command["command_id"] == "chunk_semantic_embedding:chunking"
    )
    assert "--semantic-report-output" in semantic_chunk["argv"]
    assert semantic_chunk["gemini_api_key_count"] == 4


def test_local_kaggle_plan_uses_local_backends_without_gemini(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner, "load_gemini_api_keys", lambda: [])
    monkeypatch.setattr(
        runner,
        "run_subprocess",
        lambda command: pytest.fail(f"plan mode executed {command['command_id']}"),
    )
    work_dir = smoke_dir("local-kaggle-plan")

    summary = runner.run(
        [
            "--mode",
            "plan",
            "--profile",
            "local-kaggle",
            "--dataset-dir",
            str(work_dir / "dataset"),
        ]
    )

    reports_dir = work_dir / "dataset" / "reports" / "w3_ingest_07_local_kaggle"
    manifest = json.loads((reports_dir / "w3_ingest_07_command_manifest.json").read_text(encoding="utf-8"))
    commands = manifest["commands"]
    semantic = next(command for command in commands if command["command_id"] == "chunk_semantic_embedding_bge_m3:chunking")
    entity = next(command for command in commands if command["command_id"] == "chunk_fixed_512:entity")
    graph = next(command for command in commands if command["command_id"] == "chunk_fixed_512:graph")
    embed = next(command for command in commands if command["phase"] == "embed_retrieval")

    assert summary["completed"] is True
    assert summary["profile"] == "local-kaggle"
    assert manifest["gemini_api_key_count"] == 0
    assert manifest["command_count"] == 21
    assert all(command["requires_gemini"] is False for command in commands)
    assert semantic["backend"] == "local"
    assert semantic["model"] == "BAAI/bge-m3"
    assert semantic["expected_dim"] == 1024
    assert entity["backend"] == "local"
    assert graph["backend"] == "local"
    assert "--dry-run" in graph["argv"]
    assert "--payload-output-dir" in graph["argv"]
    assert embed["backend"] == "local"
    assert embed["embedding_slot"] == "bge_m3"
    assert "--chunks-input" in embed["argv"]
    assert "--embedding-slot" in embed["argv"]
    assert "--expected-dim" in embed["argv"]


def test_gemini_plan_emits_gemini_embedding_slot() -> None:
    work_dir = smoke_dir("gemini-slot-plan")
    args = runner.parse_args(
        [
            "--mode",
            "plan",
            "--sources",
            "TVGM",
            "--strategies",
            "chunk_fixed_512",
            "--dataset-dir",
            str(work_dir / "dataset"),
        ]
    )

    commands = runner.build_commands(args, gemini_api_key_count=1)
    embed = next(command for command in commands if command["phase"] == "embed_retrieval")
    graph = next(command for command in commands if command["phase"] == "graph_relation")
    entity = next(command for command in commands if command["phase"] == "entity_extraction")

    assert embed["embedding_slot"] == "gemini"
    assert "--embedding-slot" in embed["argv"]
    assert "gemini" in embed["argv"]
    assert "--payload-output-dir" in graph["argv"]
    assert entity["backend"] == "gemini"
    assert "--llm-batch-size" in entity["argv"]
    assert "4" in entity["argv"]
    assert "--requests-per-minute" in entity["argv"]
    assert "15.0" in entity["argv"]
    assert graph["backend"] == "gemini"
    assert "--relation-mode" in graph["argv"]
    assert "llm" in graph["argv"]
    assert "--llm-batch-size" in graph["argv"]


def test_rule_only_plan_uses_rule_entity_and_relation_modes() -> None:
    work_dir = smoke_dir("rule-only-plan")
    args = runner.parse_args(
        [
            "--mode",
            "plan",
            "--profile",
            "rule-only",
            "--sources",
            "TVGM",
            "--strategies",
            "chunk_fixed_512",
            "--dataset-dir",
            str(work_dir / "dataset"),
        ]
    )

    commands = runner.build_commands(args, gemini_api_key_count=0)
    entity = next(command for command in commands if command["phase"] == "entity_extraction")
    graph = next(command for command in commands if command["phase"] == "graph_relation")

    assert args.profile == "rule-only"
    assert entity["backend"] == "rule"
    assert entity["requires_gemini"] is False
    assert "--llm-augmentation" in entity["argv"]
    assert "off" in entity["argv"]
    assert "--llm-backend" not in entity["argv"]
    assert graph["backend"] == "rule"
    assert graph["requires_gemini"] is False
    assert "--relation-mode" in graph["argv"]
    assert "rule" in graph["argv"]
    assert "--mock-llm" not in graph["argv"]


def test_phase_filter_can_plan_entity_without_graph() -> None:
    work_dir = smoke_dir("phase-filter")
    args = runner.parse_args(
        [
            "--mode",
            "plan",
            "--sources",
            "TVGM",
            "--strategies",
            "chunk_fixed_512",
            "--dataset-dir",
            str(work_dir / "dataset"),
            "--phases",
            "entity_extraction",
        ]
    )

    commands = runner.build_commands(args, gemini_api_key_count=1)

    assert {command["phase"] for command in commands} == {"entity_extraction"}
    assert len(commands) == 1


def test_graph_dry_run_keeps_production_gemini_relation_calls() -> None:
    work_dir = smoke_dir("graph-dry-run")
    args = runner.parse_args(
        [
            "--mode",
            "production",
            "--profile",
            "gemini-call",
            "--sources",
            "TVGM",
            "--strategies",
            "chunk_fixed_512",
            "--dataset-dir",
            str(work_dir / "dataset"),
            "--phases",
            "graph_relation",
            "--graph-dry-run",
        ]
    )

    commands = runner.build_commands(args, gemini_api_key_count=1)
    graph = commands[0]

    assert graph["phase"] == "graph_relation"
    assert graph["backend"] == "gemini"
    assert graph["requires_gemini"] is True
    assert "--dry-run" in graph["argv"]
    assert "--mock-llm" not in graph["argv"]


def test_gemini_model_overrides_are_forwarded_to_entity_and_relation() -> None:
    work_dir = smoke_dir("gemini-model-overrides")
    args = runner.parse_args(
        [
            "--mode",
            "plan",
            "--profile",
            "gemini-call",
            "--sources",
            "TVGM",
            "--strategies",
            "chunk_fixed_512",
            "--dataset-dir",
            str(work_dir / "dataset"),
            "--gemini-entity-model",
            "gemini-3.1-flash-lite-preview",
            "--gemini-relation-model",
            "gemini-3.1-flash-lite-preview",
        ]
    )

    commands = runner.build_commands(args, gemini_api_key_count=1)
    entity = next(command for command in commands if command["phase"] == "entity_extraction")
    graph = next(command for command in commands if command["phase"] == "graph_relation")

    assert entity["model"] == "gemini-3.1-flash-lite-preview"
    assert graph["model"] == "gemini-3.1-flash-lite-preview"
    assert "--model" in entity["argv"]
    assert "--model" in graph["argv"]
    assert "gemini-3.1-flash-lite-preview" in entity["argv"]
    assert "gemini-3.1-flash-lite-preview" in graph["argv"]


def test_dry_run_commands_use_mock_flags_and_skip_db_embed() -> None:
    work_dir = smoke_dir("dry-run-commands")
    args = runner.parse_args(
        [
            "--mode",
            "dry-run",
            "--dataset-dir",
            str(work_dir / "dataset"),
            "--chunks-dir",
            str(work_dir / "chunks"),
            "--entities-dir",
            str(work_dir / "entities"),
            "--reports-dir",
            str(work_dir / "reports"),
        ]
    )

    commands = runner.build_commands(args, gemini_api_key_count=2)

    assert any(command["skip_reason"] == "skipped_requires_db" for command in commands)
    assert all(
        "--mock-embedding" in command["argv"]
        for command in commands
        if command["phase"] == "embed_retrieval"
    )
    assert all(
        "--mock-llm" in command["argv"]
        for command in commands
        if command["phase"] in {"entity_extraction", "graph_relation"}
    )
    assert all(
        "--state-output" in command["argv"] and "--resume" in command["argv"]
        for command in commands
        if command["phase"] == "graph_relation"
    )
    assert all(
        "--include-parent-chunks" not in command["argv"]
        for command in commands
        if command["phase"] == "embed_retrieval"
    )


def test_production_mode_fails_early_without_required_gemini_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work_dir = smoke_dir("production-no-key")
    monkeypatch.setattr(runner, "load_gemini_api_keys", lambda: [])
    monkeypatch.setattr(
        runner,
        "run_subprocess",
        lambda command: pytest.fail(f"production should fail before {command['command_id']}"),
    )

    with pytest.raises(ValueError, match="At least one Gemini API key"):
        runner.run(
            [
                "--mode",
                "production",
                "--dataset-dir",
                str(work_dir / "dataset"),
                "--chunks-dir",
                str(work_dir / "chunks"),
                "--entities-dir",
                str(work_dir / "entities"),
                "--reports-dir",
                str(work_dir / "reports"),
            ]
        )


def test_resume_skips_completed_command_state(monkeypatch: pytest.MonkeyPatch) -> None:
    work_dir = smoke_dir("resume-state")
    reports_dir = work_dir / "reports"
    state_path = work_dir / "state.json"
    runner.write_json(
        state_path,
        {"commands": {"chunk_fixed_512:chunking": {"mode": "dry-run", "status": "completed"}}},
    )
    runner.write_json(reports_dir / "chunk_fixed_512_chunk_summary.json", {"total_chunks": 1})
    executed: list[str] = []

    def fake_run_subprocess(command: dict) -> None:
        executed.append(command["command_id"])
        if command.get("summary_output"):
            runner.write_json(Path(command["summary_output"]), {"completed": True})

    monkeypatch.setattr(runner, "run_subprocess", fake_run_subprocess)
    args = runner.parse_args(
        [
            "--mode",
            "dry-run",
            "--sources",
            "TVGM",
            "--strategies",
            "chunk_fixed_512",
            "--resume",
            "--state-output",
            str(state_path),
            "--reports-dir",
            str(reports_dir),
            "--chunks-dir",
            str(work_dir / "chunks"),
            "--entities-dir",
            str(work_dir / "entities"),
        ]
    )
    commands = runner.build_commands(args, gemini_api_key_count=1)

    result = runner.execute_commands(commands, args=args, state_path=state_path)

    assert "chunk_fixed_512:chunking" not in executed
    assert result["skipped_command_count"] == 2
    assert "chunk_fixed_512:entity" in executed
    assert "chunk_fixed_512:graph" in executed


def test_execute_commands_logs_runner_progress(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    work_dir = smoke_dir("runner-progress")
    reports_dir = work_dir / "reports"
    state_path = work_dir / "state.json"
    executed: list[str] = []

    def fake_run_subprocess(command: dict) -> None:
        executed.append(command["command_id"])
        if command.get("summary_output"):
            runner.write_json(Path(command["summary_output"]), {"completed": True})

    monkeypatch.setattr(runner, "run_subprocess", fake_run_subprocess)
    args = runner.parse_args(
        [
            "--mode",
            "dry-run",
            "--sources",
            "TVGM",
            "--strategies",
            "chunk_fixed_512",
            "--phases",
            "entity_extraction",
            "--state-output",
            str(state_path),
            "--reports-dir",
            str(reports_dir),
            "--chunks-dir",
            str(work_dir / "chunks"),
            "--entities-dir",
            str(work_dir / "entities"),
        ]
    )
    commands = runner.build_commands(args, gemini_api_key_count=1)

    runner.execute_commands(commands, args=args, state_path=state_path)

    captured = capsys.readouterr()
    assert executed == ["chunk_fixed_512:entity"]
    assert "[runner-progress]" in captured.err
    assert "start 1/1 command_id=chunk_fixed_512:entity" in captured.err
    assert "done 1/1 command_id=chunk_fixed_512:entity" in captured.err


def test_resume_does_not_skip_command_completed_in_different_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    work_dir = smoke_dir("resume-state-mode-mismatch")
    reports_dir = work_dir / "reports"
    state_path = work_dir / "state.json"
    runner.write_json(
        state_path,
        {"commands": {"chunk_fixed_512:chunking": {"mode": "dry-run", "status": "completed"}}},
    )
    executed: list[str] = []

    def fake_run_subprocess(command: dict) -> None:
        executed.append(command["command_id"])
        if command.get("summary_output"):
            runner.write_json(Path(command["summary_output"]), {"completed": True})

    monkeypatch.setattr(runner, "run_subprocess", fake_run_subprocess)
    args = runner.parse_args(
        [
            "--mode",
            "production",
            "--sources",
            "TVGM",
            "--strategies",
            "chunk_fixed_512",
            "--resume",
            "--state-output",
            str(state_path),
            "--reports-dir",
            str(reports_dir),
            "--chunks-dir",
            str(work_dir / "chunks"),
            "--entities-dir",
            str(work_dir / "entities"),
        ]
    )
    commands = runner.build_commands(args, gemini_api_key_count=1)

    result = runner.execute_commands(commands, args=args, state_path=state_path)

    assert "chunk_fixed_512:chunking" in executed
    assert result["skipped_command_count"] == 0


def test_resume_does_not_skip_completed_state_when_summary_is_incomplete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work_dir = smoke_dir("resume-incomplete-summary")
    reports_dir = work_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    state_path = work_dir / "state.json"
    entity_summary_path = reports_dir / "chunk_fixed_512_entity_summary.json"
    runner.write_json(
        state_path,
        {
            "commands": {
                "chunk_fixed_512:chunking": {"mode": "production", "status": "completed"},
                "chunk_fixed_512:entity": {"mode": "production", "status": "completed"},
            }
        },
    )
    runner.write_json(reports_dir / "chunk_fixed_512_chunk_summary.json", {"total_chunks": 1})
    runner.write_json(entity_summary_path, {"completed": False, "disabled_key_count": 4, "error_count": 1})
    executed: list[str] = []

    def fake_run_subprocess(command: dict) -> None:
        executed.append(command["command_id"])
        if command["command_id"] == "chunk_fixed_512:entity":
            runner.write_json(entity_summary_path, {"completed": False, "disabled_key_count": 4, "error_count": 1})

    monkeypatch.setattr(runner, "run_subprocess", fake_run_subprocess)
    args = runner.parse_args(
        [
            "--mode",
            "production",
            "--sources",
            "TVGM",
            "--strategies",
            "chunk_fixed_512",
            "--resume",
            "--state-output",
            str(state_path),
            "--reports-dir",
            str(reports_dir),
            "--chunks-dir",
            str(work_dir / "chunks"),
            "--entities-dir",
            str(work_dir / "entities"),
        ]
    )
    commands = runner.build_commands(args, gemini_api_key_count=1)

    with pytest.raises(RuntimeError, match="incomplete summary"):
        runner.execute_commands(commands, args=args, state_path=state_path)

    assert "chunk_fixed_512:chunking" not in executed
    assert "chunk_fixed_512:entity" in executed
    assert "chunk_fixed_512:graph" not in executed
