#!/usr/bin/env python3
"""Run enhanced coverage and optional static checks for additions."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SUITE_ROOT = SCRIPT_DIR.parent
REPO_ROOT = SUITE_ROOT.parents[2]
COMMON_DIR = REPO_ROOT / "security_testing-v1" / "additions" / "common"
if str(COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(COMMON_DIR))

from runner import ensure_dir, run_command, write_json  # noqa: E402

COVERAGE_RE = re.compile(r"TOTAL\s+([0-9]+)\s+([0-9]+)\s+([0-9]+\.?[0-9]*)%")

SUITES = [
    {
        "name": "ipv4_combinatorial",
        "manifest": REPO_ROOT
        / "security_testing-v1"
        / "additions"
        / "ipv4_combinatorial"
        / "ipv4_combinatorial_suite"
        / "Cargo.toml",
    },
    {
        "name": "microbench",
        "manifest": REPO_ROOT
        / "security_testing-v1"
        / "additions"
        / "perf_microbench"
        / "microbench_suite"
        / "Cargo.toml",
    },
]


def quote(path: Path) -> str:
    return f'"{path}"'


def ensure_tool(command_probe: str, install_command: str, cwd: Path, probe_log: Path, install_log: Path) -> bool:
    probe = run_command(command_probe, cwd, probe_log)
    if probe.exit_code == 0:
        return True

    install = run_command(install_command, cwd, install_log)
    return install.exit_code == 0


def parse_coverage(text: str) -> dict:
    match = COVERAGE_RE.search(text)
    if match:
        return {
            "regions": int(match.group(1)),
            "missed": int(match.group(2)),
            "coverage_percent": float(match.group(3)),
        }
    return {
        "regions": None,
        "missed": None,
        "coverage_percent": None,
    }


def run_cov_for_suite(platform: str, suite: dict, artifacts_dir: Path, logs_dir: Path) -> dict:
    name = suite["name"]
    manifest = suite["manifest"]

    summary_log = logs_dir / f"{name}_coverage_summary.log"
    summary_cmd = (
        f"cargo llvm-cov --manifest-path {quote(manifest)} "
        "--tests --summary-only --include-deps"
    )
    summary_result = run_command(summary_cmd, REPO_ROOT, summary_log)

    lcov_path = artifacts_dir / f"coverage_{name}_{platform}.lcov"
    lcov_log = logs_dir / f"{name}_coverage_lcov.log"
    lcov_cmd = (
        f"cargo llvm-cov --manifest-path {quote(manifest)} "
        f"--tests --include-deps --lcov --output-path {quote(lcov_path)}"
    )
    lcov_result = run_command(lcov_cmd, REPO_ROOT, lcov_log)

    output_blob = (summary_result.stdout or "") + "\n" + (summary_result.stderr or "")
    coverage = parse_coverage(output_blob)
    coverage["summary_log"] = str(summary_log.relative_to(REPO_ROOT))
    coverage["lcov_log"] = str(lcov_log.relative_to(REPO_ROOT))
    coverage["lcov_exit_code"] = lcov_result.exit_code
    coverage["lcov_file"] = str(lcov_path.relative_to(REPO_ROOT))

    return {
        "summary_exit_code": summary_result.exit_code,
        "coverage": coverage,
    }


def run(platform: str, include_static: bool) -> None:
    artifacts_dir = SUITE_ROOT / "artifacts"
    logs_dir = SUITE_ROOT / "logs" / platform
    ensure_dir(artifacts_dir)
    ensure_dir(logs_dir)

    llvm_tools_log = logs_dir / "rustup_llvm_tools.log"
    llvm_tools_result = run_command("rustup component add llvm-tools-preview", REPO_ROOT, llvm_tools_log)

    cov_tool_ok = ensure_tool(
        command_probe="cargo llvm-cov --version",
        install_command="cargo install cargo-llvm-cov",
        cwd=REPO_ROOT,
        probe_log=logs_dir / "probe_llvm_cov.log",
        install_log=logs_dir / "install_llvm_cov.log",
    )

    suite_results = {}
    if cov_tool_ok:
        for suite in SUITES:
            suite_results[suite["name"]] = run_cov_for_suite(platform, suite, artifacts_dir, logs_dir)

    static_checks = None
    if include_static:
        clippy_log = logs_dir / "clippy.log"
        clippy_result = run_command("cargo clippy --lib --tests", REPO_ROOT, clippy_log)

        audit_probe_log = logs_dir / "probe_audit.log"
        audit_probe = run_command("cargo audit --version", REPO_ROOT, audit_probe_log)
        audit_result_data = {
            "available": audit_probe.exit_code == 0,
            "probe_log": str(audit_probe_log.relative_to(REPO_ROOT)),
        }
        if audit_probe.exit_code == 0:
            audit_log = logs_dir / "cargo_audit.log"
            audit_result = run_command("cargo audit", REPO_ROOT, audit_log)
            audit_result_data["exit_code"] = audit_result.exit_code
            audit_result_data["log_file"] = str(audit_log.relative_to(REPO_ROOT))

        static_checks = {
            "clippy": {
                "exit_code": clippy_result.exit_code,
                "log_file": str(clippy_log.relative_to(REPO_ROOT)),
            },
            "cargo_audit": audit_result_data,
        }

    summary = {
        "platform": platform,
        "llvm_tools_exit_code": llvm_tools_result.exit_code,
        "llvm_cov_available": cov_tool_ok,
        "suites": suite_results,
        "static_checks": static_checks,
    }

    summary_path = artifacts_dir / f"whitebox_safety_summary_{platform}.json"
    write_json(summary_path, summary)

    print(f"White-box additions complete for platform={platform}")
    print(f"Summary JSON: {summary_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run enhanced white-box coverage suite.")
    parser.add_argument("--platform", required=True, choices=["windows", "wsl"])
    parser.add_argument("--include-static", action="store_true")
    args = parser.parse_args()
    run(args.platform, args.include_static)
