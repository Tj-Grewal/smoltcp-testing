#!/usr/bin/env python3
"""Run the IPv4 combinatorial suite and summarize artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
SUITE_ROOT = SCRIPT_DIR.parent
REPO_ROOT = SUITE_ROOT.parents[2]
COMMON_DIR = REPO_ROOT / "security_testing" / "additions" / "common"
if str(COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(COMMON_DIR))

from runner import ensure_dir, run_command, write_json  # noqa: E402


def parse_test_output(output: str) -> dict:
    generated_match = re.search(r"generated_cases=(\d+)", output)
    matched_match = re.search(r"matched_expectation=(\d+)", output)
    return {
        "generated_cases_from_test": int(generated_match.group(1)) if generated_match else None,
        "matched_expectation_from_test": int(matched_match.group(1)) if matched_match else None,
    }


def count_csv_rows(path: Path) -> Optional[int]:
    if not path.exists():
        return None
    rows = 0
    with path.open("r", encoding="utf-8") as f:
        for idx, _ in enumerate(f):
            if idx == 0:
                continue
            rows += 1
    return rows


def run(platform: str) -> None:
    artifacts_dir = SUITE_ROOT / "artifacts"
    logs_dir = SUITE_ROOT / "logs" / platform
    ensure_dir(artifacts_dir)
    ensure_dir(logs_dir)

    cases_csv = SUITE_ROOT / f"ipv4_cases_{platform}.csv"
    log_path = logs_dir / "ipv4_combinatorial.log"
    command = "cargo test -- --nocapture"
    result = run_command(
        command=command,
        cwd=SUITE_ROOT / "ipv4_combinatorial_suite",
        log_path=log_path,
        env={"SEC_TEST_PLATFORM": platform},
    )

    parsed = parse_test_output(result.stdout + "\n" + result.stderr)

    summary = {
        "platform": platform,
        "frame_csv": str(cases_csv.relative_to(REPO_ROOT)),
        "generated_frames_csv_count": count_csv_rows(cases_csv),
        "test_command": command,
        "test_exit_code": result.exit_code,
        "test_log": str(log_path.relative_to(REPO_ROOT)),
        **parsed,
    }

    summary_path = artifacts_dir / f"ipv4_combinatorial_summary_{platform}.json"
    write_json(summary_path, summary)

    print(f"IPv4 combinatorial suite complete for platform={platform}")
    print(f"Summary JSON: {summary_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run IPv4 combinatorial suite.")
    parser.add_argument("--platform", required=True, choices=["windows", "wsl"])
    args = parser.parse_args()
    run(args.platform)
