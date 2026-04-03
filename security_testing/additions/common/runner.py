#!/usr/bin/env python3
"""Shared command runner and logging helpers for security testing additions."""

from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


@dataclass
class CommandResult:
    command: str
    cwd: str
    exit_code: int
    duration_seconds: float
    started_utc: str
    finished_utc: str
    stdout: str
    stderr: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, obj: object) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False), encoding="utf-8")


def run_command(
    command: str,
    cwd: Path,
    log_path: Path,
    env: Optional[Dict[str, str]] = None,
) -> CommandResult:
    """Run a shell command and write a deterministic log file."""
    ensure_dir(log_path.parent)
    started = utc_now_iso()
    t0 = time.perf_counter()

    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    cargo_bin = Path.home() / ".cargo" / "bin"
    if cargo_bin.exists():
        current_path = merged_env.get("PATH", "")
        parts = current_path.split(os.pathsep) if current_path else []
        cargo_bin_str = str(cargo_bin)
        if cargo_bin_str not in parts:
            merged_env["PATH"] = (
                f"{cargo_bin_str}{os.pathsep}{current_path}"
                if current_path
                else cargo_bin_str
            )

    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=merged_env,
    )

    while True:
        try:
            stdout, stderr = process.communicate(timeout=5)
            break
        except subprocess.TimeoutExpired:
            print(f"[runner] still running: {command}", flush=True)

    t1 = time.perf_counter()
    finished = utc_now_iso()

    result = CommandResult(
        command=command,
        cwd=str(cwd),
        exit_code=process.returncode,
        duration_seconds=t1 - t0,
        started_utc=started,
        finished_utc=finished,
        stdout=stdout,
        stderr=stderr,
    )

    with log_path.open("w", encoding="utf-8") as f:
        f.write(f"COMMAND: {result.command}\n")
        f.write(f"CWD: {result.cwd}\n")
        f.write(f"STARTED_UTC: {result.started_utc}\n")
        f.write(f"FINISHED_UTC: {result.finished_utc}\n")
        f.write(f"DURATION_SECONDS: {result.duration_seconds:.6f}\n")
        f.write(f"EXIT_CODE: {result.exit_code}\n")
        f.write("\n=== STDOUT ===\n")
        f.write(result.stdout)
        f.write("\n=== STDERR ===\n")
        f.write(result.stderr)

    return result


def result_to_jsonable(result: CommandResult) -> Dict[str, object]:
    return asdict(result)
