#!/usr/bin/env python3
"""Execute microbench runs and aggregate performance metrics."""

from __future__ import annotations

import argparse
import csv
import re
import statistics
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SUITE_ROOT = SCRIPT_DIR.parent
REPO_ROOT = SUITE_ROOT.parents[2]
COMMON_DIR = REPO_ROOT / "security_testing-v1" / "additions" / "common"
if str(COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(COMMON_DIR))

from runner import ensure_dir, run_command, write_json  # noqa: E402

METRIC_RE = re.compile(r"^METRIC,([^,]+),(\d+),(\d+),([0-9.]+)$", re.M)


def parse_metrics(output: str) -> dict:
    metrics = {}
    for name, iters, total_ns, ns_per_iter in METRIC_RE.findall(output):
        metrics[name] = {
            "iterations": int(iters),
            "total_ns": int(total_ns),
            "ns_per_iter": float(ns_per_iter),
        }
    return metrics


def run(platform: str, repetitions: int, iters: int) -> None:
    artifacts_dir = SUITE_ROOT / "artifacts"
    logs_dir = SUITE_ROOT / "logs" / platform
    ensure_dir(artifacts_dir)
    ensure_dir(logs_dir)

    warmup_log = logs_dir / "microbench_warmup.log"
    run_command(
        command="cargo test --release -- --nocapture",
        cwd=SUITE_ROOT / "microbench_suite",
        log_path=warmup_log,
        env={"MICROBENCH_ITERS": str(iters)},
    )

    run_summaries = []
    for i in range(1, repetitions + 1):
        log_path = logs_dir / f"microbench_run_{i:02d}.log"
        result = run_command(
            command="cargo test --release -- --nocapture",
            cwd=SUITE_ROOT / "microbench_suite",
            log_path=log_path,
            env={"MICROBENCH_ITERS": str(iters)},
        )
        metrics = parse_metrics(result.stdout + "\n" + result.stderr)
        run_summaries.append(
            {
                "run_index": i,
                "exit_code": result.exit_code,
                "log_file": str(log_path.relative_to(REPO_ROOT)),
                "metrics": metrics,
            }
        )

    metrics_csv = artifacts_dir / f"microbench_metrics_{platform}.csv"
    with metrics_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["run", "metric", "iterations", "total_ns", "ns_per_iter"])
        for row in run_summaries:
            for metric_name, metric_data in row["metrics"].items():
                writer.writerow(
                    [
                        row["run_index"],
                        metric_name,
                        metric_data["iterations"],
                        metric_data["total_ns"],
                        f"{metric_data['ns_per_iter']:.4f}",
                    ]
                )

    aggregate = {}
    metric_names = set()
    for row in run_summaries:
        metric_names.update(row["metrics"].keys())

    for metric_name in sorted(metric_names):
        samples = [
            row["metrics"][metric_name]["ns_per_iter"]
            for row in run_summaries
            if metric_name in row["metrics"]
        ]
        if samples:
            aggregate[metric_name] = {
                "sample_count": len(samples),
                "mean_ns_per_iter": statistics.mean(samples),
                "stdev_ns_per_iter": statistics.pstdev(samples) if len(samples) > 1 else 0.0,
                "min_ns_per_iter": min(samples),
                "max_ns_per_iter": max(samples),
            }

    summary = {
        "platform": platform,
        "repetitions": repetitions,
        "iters": iters,
        "warmup_log": str(warmup_log.relative_to(REPO_ROOT)),
        "runs": run_summaries,
        "aggregate_ns_per_iter": aggregate,
        "metrics_csv": str(metrics_csv.relative_to(REPO_ROOT)),
    }

    summary_path = artifacts_dir / f"microbench_summary_{platform}.json"
    write_json(summary_path, summary)

    print(f"Microbench suite complete for platform={platform}")
    print(f"Summary JSON: {summary_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run microbench suite.")
    parser.add_argument("--platform", required=True, choices=["windows", "wsl"])
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--iters", type=int, default=10000)
    args = parser.parse_args()
    run(args.platform, args.repetitions, args.iters)
