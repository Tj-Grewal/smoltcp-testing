#!/usr/bin/env python3
"""Run fuzzing with sanitizer support and record distinct crash signatures."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SUITE_ROOT = SCRIPT_DIR.parent
REPO_ROOT = SUITE_ROOT.parents[2]
COMMON_DIR = REPO_ROOT / "security_testing" / "additions" / "common"
if str(COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(COMMON_DIR))

from runner import ensure_dir, run_command, write_json  # noqa: E402

FUZZ_TARGETS = [
    "packet_parser",
    "tcp_headers",
    "dhcp_header",
    "ieee802154_header",
    "sixlowpan_packet",
]

PANIC_RE = re.compile(r"panicked at '?(.*?)'?\s*,\s*(.*):(\d+):(\d+)")
ASAN_RE = re.compile(r"ERROR: AddressSanitizer: (.*)")
UBSAN_RE = re.compile(r"runtime error:\s*(.*)")


def error_signature(text: str) -> str:
    panic = PANIC_RE.search(text)
    if panic:
        msg, file_path, line, col = panic.groups()
        return f"panic|{msg}|{file_path}:{line}:{col}"

    asan = ASAN_RE.search(text)
    if asan:
        return f"asan|{asan.group(1).strip()}"

    ubsan = UBSAN_RE.search(text)
    if ubsan:
        return f"ubsan|{ubsan.group(1).strip()}"

    digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]
    return f"unknown|{digest}"


def list_artifacts(target: str) -> list[Path]:
    directory = REPO_ROOT / "fuzz" / "artifacts" / target
    if not directory.exists():
        return []
    return sorted([p for p in directory.iterdir() if p.is_file()])


def ensure_cargo_fuzz(log_path: Path) -> None:
    probe = run_command("cargo fuzz --help", REPO_ROOT, log_path)
    if probe.exit_code == 0:
        return

    install_log = log_path.parent / "cargo_fuzz_install.log"
    install = run_command("cargo install cargo-fuzz", REPO_ROOT, install_log)
    if install.exit_code != 0:
        raise RuntimeError(
            "cargo-fuzz is not available and installation failed. "
            f"See log: {install_log}"
        )


def ensure_nightly_toolchain(log_path: Path) -> None:
    install = run_command("rustup toolchain install nightly", REPO_ROOT, log_path)
    if install.exit_code != 0:
        raise RuntimeError(
            "Rust nightly toolchain installation failed. "
            f"See log: {log_path}"
        )


def run(platform: str, seconds_per_target: int) -> None:
    artifacts_dir = SUITE_ROOT / "artifacts"
    logs_dir = SUITE_ROOT / "logs" / platform
    ensure_dir(artifacts_dir)
    ensure_dir(logs_dir)

    ensure_cargo_fuzz(logs_dir / "cargo_fuzz_probe.log")
    ensure_nightly_toolchain(logs_dir / "rustup_nightly_install.log")

    target_runs = []
    discovered_errors = []

    for target in FUZZ_TARGETS:
        fuzz_log = logs_dir / f"fuzz_{target}.log"
        command = (
            f"cargo +nightly fuzz run {target} -- "
            f"-max_total_time={seconds_per_target} -timeout=10 -rss_limit_mb=4096"
        )
        result = run_command(command, REPO_ROOT / "fuzz", fuzz_log)

        artifacts = list_artifacts(target)
        reproduced = []
        for idx, artifact in enumerate(artifacts, start=1):
            repro_log = logs_dir / f"repro_{target}_{idx:02d}.log"
            repro_cmd = f"cargo +nightly fuzz run {target} {artifact} -- -runs=1"
            repro = run_command(
                repro_cmd,
                REPO_ROOT / "fuzz",
                repro_log,
                env={"RUST_BACKTRACE": "1"},
            )
            stderr_blob = (repro.stdout or "") + "\n" + (repro.stderr or "")
            signature = error_signature(stderr_blob)
            reproduced.append(
                {
                    "artifact": str(artifact.relative_to(REPO_ROOT)),
                    "repro_command": repro_cmd,
                    "repro_exit_code": repro.exit_code,
                    "repro_log": str(repro_log.relative_to(REPO_ROOT)),
                    "signature": signature,
                }
            )
            discovered_errors.append(
                {
                    "target": target,
                    "artifact": str(artifact.relative_to(REPO_ROOT)),
                    "signature": signature,
                    "repro_log": str(repro_log.relative_to(REPO_ROOT)),
                }
            )

        target_runs.append(
            {
                "target": target,
                "command": command,
                "exit_code": result.exit_code,
                "fuzz_log": str(fuzz_log.relative_to(REPO_ROOT)),
                "artifact_count": len(artifacts),
                "artifacts": [str(a.relative_to(REPO_ROOT)) for a in artifacts],
                "reproductions": reproduced,
            }
        )

    unique_signatures = sorted({e["signature"] for e in discovered_errors})

    summary = {
        "platform": platform,
        "seconds_per_target": seconds_per_target,
        "targets": target_runs,
        "discovered_error_instances": discovered_errors,
        "distinct_error_signatures": unique_signatures,
        "distinct_error_count": len(unique_signatures),
    }

    summary_path = artifacts_dir / f"fuzzing_summary_{platform}.json"
    write_json(summary_path, summary)

    print(f"Fuzzing suite complete for platform={platform}")
    print(f"Distinct error signatures: {len(unique_signatures)}")
    print(f"Summary JSON: {summary_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run fuzzing and sanitizer crash discovery.")
    parser.add_argument("--platform", required=True, choices=["windows", "wsl"])
    parser.add_argument("--seconds-per-target", type=int, default=180)
    args = parser.parse_args()
    run(args.platform, args.seconds_per_target)
