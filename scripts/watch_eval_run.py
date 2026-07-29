"""Watch a background W8 evaluation run and write lightweight status snapshots.

This helper intentionally only reads run artifacts. It does not mutate the
evaluation checkpoint used by ``scripts/run_eval.py``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import time
from pathlib import Path
from typing import Any


def _is_pid_running(pid: str) -> bool:
    if not pid:
        return False
    try:
        tasklist = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        ).stdout
    except OSError:
        return False
    return pid in tasklist


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot(output_dir: Path, pid_file: Path) -> dict[str, Any]:
    pid = pid_file.read_text(encoding="ascii").strip() if pid_file.exists() else ""
    checkpoint_dir = output_dir / "checkpoints"
    summary = _load_json(checkpoint_dir / "checkpoint_summary.json")
    stdout = output_dir / "phase2_full_stdout.log"
    stderr = output_dir / "phase2_full_stderr.log"
    return {
        "checked_at_local": dt.datetime.now().isoformat(),
        "pid": pid,
        "running": _is_pid_running(pid),
        "summary": summary,
        "stdout_bytes": stdout.stat().st_size if stdout.exists() else 0,
        "stderr_bytes": stderr.stat().st_size if stderr.exists() else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--pid-file", type=Path)
    parser.add_argument("--interval-seconds", type=int, default=300)
    args = parser.parse_args()

    output_dir = args.output_dir
    pid_file = args.pid_file or output_dir / "phase2_full.pid"
    status_path = output_dir / "phase2_full_status_latest.json"
    history_path = output_dir / "phase2_full_status_history.jsonl"

    while True:
        record = snapshot(output_dir, pid_file)
        status_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        summary = record.get("summary") or {}
        if not record.get("running") or summary.get("remaining_pair_count") == 0:
            break
        time.sleep(max(args.interval_seconds, 1))

    return 0


if __name__ == "__main__":  # pragma: no cover - operational helper
    raise SystemExit(main())