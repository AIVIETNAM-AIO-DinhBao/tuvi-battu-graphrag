from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.rag.gemini_keys import load_runtime_gemini_api_keys


RUN_DIR = Path(__file__).resolve().parent / "full100"
CHECKPOINT_DIR = RUN_DIR / "checkpoint"
SUMMARY_PATH = CHECKPOINT_DIR / "checkpoint_summary.json"
PROCESS_PATH = RUN_DIR / "process.json"
MONITOR_PATH = RUN_DIR / "monitor_status.json"
EXIT_PATH = RUN_DIR / "exit_code.txt"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def read_summary() -> dict | None:
    try:
        return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def main() -> int:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    EXIT_PATH.unlink(missing_ok=True)
    command = [
        str(ROOT / ".venv" / "Scripts" / "python.exe"),
        "scripts/run_eval.py",
        "--manifest", "configs/w8_abl_01_priority_wave.yaml",
        "--judge-backend", "gemini",
        "--judge-model", "gemini-3.1-flash-lite-preview",
        "--skip-persistence",
        "--checkpoint-dir", "benchmark/tuvi_golden_dataset/reports/w8_abl_01_priority_wave/full100/checkpoint",
        "--output-dir", "benchmark/tuvi_golden_dataset/reports/w8_abl_01_priority_wave/full100",
        "--max-item-attempts", "2",
        "--retry-base-seconds", "2",
    ]
    environment = dict(os.environ)
    environment["PYTHONPATH"] = "backend"
    runtime_keys = load_runtime_gemini_api_keys()
    if len(runtime_keys) < 2:
        raise RuntimeError("At least two runtime Gemini keys are required for the rotated priority wave.")
    # The prelaunch probe recorded that original key_1 exhausted its daily
    # request quota while keys 2-4 remained healthy. Rotate only in the child
    # process environment; never persist secret values.
    rotated_keys = runtime_keys[1:] + runtime_keys[:1]
    environment["GEMINI_API_KEYS"] = ",".join(rotated_keys)
    with (RUN_DIR / "stdout.log").open("w", encoding="utf-8") as stdout, (RUN_DIR / "stderr.log").open("w", encoding="utf-8") as stderr:
        process = subprocess.Popen(command, cwd=ROOT, env=environment, stdout=stdout, stderr=stderr)
        atomic_json(PROCESS_PATH, {
            "pid": os.getpid(),
            "evaluator_pid": process.pid,
            "started_at": utc_now(),
            "status": "running",
            "runtime_key_count": len(rotated_keys),
            "active_primary_label": "original_key_2",
            "exhausted_key_label_moved_to_end": "original_key_1",
            "command": "scripts/run_eval.py --manifest configs/w8_abl_01_priority_wave.yaml [sanitized live full-100 args]",
        })
        while process.poll() is None:
            atomic_json(MONITOR_PATH, {
                "status": "running",
                "supervisor_pid": os.getpid(),
                "evaluator_pid": process.pid,
                "heartbeat_at": utc_now(),
                "checkpoint": read_summary(),
            })
            time.sleep(15)
        exit_code = int(process.returncode or 0)

    EXIT_PATH.write_text(f"{exit_code}\n", encoding="ascii")
    final_status = "completed" if exit_code == 0 else "failed"
    atomic_json(MONITOR_PATH, {
        "status": final_status,
        "supervisor_pid": os.getpid(),
        "evaluator_pid": process.pid,
        "heartbeat_at": utc_now(),
        "exit_code": exit_code,
        "checkpoint": read_summary(),
    })
    process_payload = json.loads(PROCESS_PATH.read_text(encoding="utf-8"))
    process_payload["status"] = final_status
    process_payload["exit_code"] = exit_code
    atomic_json(PROCESS_PATH, process_payload)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())