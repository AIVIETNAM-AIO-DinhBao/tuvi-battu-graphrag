"""Generate a copy/paste run ticket for human runner A or B."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.rag.ablation import load_ablation_manifest  # noqa: E402
from app.rag.evaluation_checkpoint import sha256_file  # noqa: E402


ANCHORS = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "sequential_ablation" / "gold_span_anchors.jsonl"


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT_DIR).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def git_sha() -> str:
    command = ["git", "-c", f"safe.directory={ROOT_DIR.as_posix()}", "rev-parse", "HEAD"]
    try:
        return subprocess.run(command, cwd=ROOT_DIR, check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "UNAVAILABLE"


def command_for(
    manifest_path: Path,
    output_dir: str,
    phase: str,
    *,
    resume: bool,
    bundle: str | None = None,
) -> str:
    wrapper = {
        "p3": "run_p3_frozen_prompt_phase.ps1",
        "p5": "run_p5_replay_phase.ps1",
    }.get(phase, "run_retrieval_phase.ps1")
    suffix = " `\n  -Resume" if resume else ""
    manifest = repo_relative(manifest_path).replace("/", "\\")
    output = output_dir.replace("/", "\\")
    command = (
        f"powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\sequential_ablation\\{wrapper} `\n"
        f"  -Manifest '{manifest}' `\n"
    )
    normalized_bundle = str(bundle or "").replace("/", "\\")
    if phase == "p3":
        command += f"  -FrozenBundle '{normalized_bundle}' `\n"
    elif phase == "p5":
        command += f"  -Bundle '{normalized_bundle}' `\n"
    command += f"  -OutputDir '{output}'"
    if phase != "p5":
        command += f" `\n  -CheckpointDir '{output}\\checkpoints'{suffix}"
    return command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an immutable human run ticket from a shard manifest.")
    parser.add_argument("--phase", choices=["p1", "p2", "p3", "p4", "p5"], required=True)
    parser.add_argument("--member", choices=["A", "B"], required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", default="TBD (Asia/Bangkok)")
    parser.add_argument("--neo4j-snapshot", default="TBD — A must fill before release")
    parser.add_argument("--bundle", default=None, help="Required shared bundle path for P3/P5 tickets.")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = resolve(args.manifest).resolve()
    output_path = resolve(args.output).resolve()
    if output_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite {output_path}; use --force only before ticket release.")
    manifest = load_ablation_manifest(manifest_path)
    if args.phase in {"p3", "p5"} and not args.bundle:
        raise SystemExit(f"--bundle is required for {args.phase.upper()} tickets.")
    config_count = len(manifest.configs)
    backend = "gemini blind-v2" if args.phase == "p3" else "rule-based-gold-evidence-v1"
    bundle_path = resolve(Path(args.bundle)).resolve() if args.bundle else None
    bundle_manifest = bundle_path / "bundle_manifest.json" if bundle_path else None
    if bundle_manifest is not None and not bundle_manifest.exists():
        raise SystemExit(f"Bundle manifest does not exist: {bundle_manifest}")
    bundle_note = (
        f"{repo_relative(bundle_path)}; manifest_sha256={sha256_file(bundle_manifest)}"
        if bundle_path is not None and bundle_manifest is not None
        else "N/A"
    )
    output_dir = repo_relative(manifest.output_dir)
    official = command_for(manifest_path, output_dir, args.phase, resume=False, bundle=args.bundle)
    resume = command_for(manifest_path, output_dir, args.phase, resume=True, bundle=args.bundle)
    text = f"""# Run ticket {args.phase.upper()}-{args.member}

- Assignee: `{args.member}`
- Phase: `{args.phase.upper()}`
- Git SHA: `{git_sha()}`
- Dataset SHA-256: `{sha256_file(manifest.dataset_path)}`
- Anchor SHA-256: `{sha256_file(ANCHORS)}`
- Shared bundle: `{bundle_note}`
- Neo4j snapshot/counts: `{args.neo4j_snapshot}`
- Manifest: `{repo_relative(manifest_path)}`
- Manifest SHA-256: `{sha256_file(manifest_path)}`
- Output: `{output_dir}`
- Expected: `{config_count} configs × 100 items = {config_count * 100} pairs`
- Backend: `{backend}`
- Deadline: `{args.deadline}`

## Lệnh official duy nhất

```powershell
{official}
```

Không thêm `--limit` và không sửa manifest.

## Resume khi bị ngắt

```powershell
{resume}
```

## Bàn giao nguyên thư mục output

- [ ] `evaluation_report.json`
- [ ] `evaluation_report.md`
- [ ] `checkpoints/evaluation_checkpoint.json`
- [ ] `checkpoints/checkpoint_summary.json`
- [ ] `artifact_manifest_sha256.json`
- [ ] console log nếu có lỗi
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8", newline="\n")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
