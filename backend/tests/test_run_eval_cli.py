from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT_DIR / "scripts" / "run_eval.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location("run_eval_script", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "argv",
    [
        ["run_eval.py", "--resume"],
        ["run_eval.py", "--retry-failed"],
        ["run_eval.py", "--max-item-attempts", "0"],
        ["run_eval.py", "--retry-base-seconds", "-1"],
    ],
)
def test_parse_args_rejects_invalid_checkpoint_and_retry_options(monkeypatch, argv: list[str]) -> None:
    module = load_script_module()
    monkeypatch.setattr(module.sys, "argv", argv)

    with pytest.raises(SystemExit) as exc_info:
        module.parse_args()

    assert exc_info.value.code == 2


def test_checkpoint_store_rejects_existing_path_without_resume(tmp_path: Path) -> None:
    module = load_script_module()
    checkpoint_dir = tmp_path / "checkpoint"
    checkpoint_dir.mkdir()
    (checkpoint_dir / "evaluation_checkpoint.json").write_text("{}", encoding="utf-8")
    args = module.argparse.Namespace(
        checkpoint_dir=checkpoint_dir,
        resume=False,
        limit=1,
        offline_smoke=True,
        judge_backend="static",
        judge_model="static-smoke",
    )
    manifest = module.build_single_config_manifest(
        dataset_path=ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "release" / "tuviqa_v1_release.jsonl",
        config_path=ROOT_DIR / "configs" / "default_production.yaml",
        output_dir=tmp_path,
    )

    with pytest.raises(module.CheckpointError, match="already exists"):
        module.build_checkpoint_store(args, manifest)
