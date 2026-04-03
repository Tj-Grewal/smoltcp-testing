#!/usr/bin/env python3
"""Generate first-order mutants and log kill results with JSON summaries."""

from __future__ import annotations

import argparse
import csv
import difflib
import random
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
SUITE_ROOT = SCRIPT_DIR.parent
REPO_ROOT = SUITE_ROOT.parents[2]
COMMON_DIR = REPO_ROOT / "security_testing" / "additions" / "common"
if str(COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(COMMON_DIR))

from runner import ensure_dir, result_to_jsonable, run_command, write_json  # noqa: E402


TARGETS = [
    {
        "file": "src/storage/assembler.rs",
        "filter": "storage::assembler",
        "count": 110,
    },
    {
        "file": "src/wire/ipv4.rs",
        "filter": "wire::ipv4",
        "count": 100,
    },
    {
        "file": "src/wire/udp.rs",
        "filter": "wire::udp",
        "count": 100,
    },
    {
        "file": "src/wire/tcp.rs",
        "filter": "wire::tcp",
        "count": 120,
    },
]

OP_PATTERNS: List[Tuple[str, str, str]] = [
    ("rel_eq_ne", r"[ \t]*==[ \t]*", " != "),
    ("rel_ne_eq", r"[ \t]*!=[ \t]*", " == "),
    ("rel_le_lt", r"[ \t]*<=[ \t]*", " < "),
    ("rel_ge_gt", r"[ \t]*>=[ \t]*", " > "),
    ("rel_lt_le", r"\s<\s", " <= "),
    ("rel_gt_ge", r"\s>\s", " >= "),
    ("bool_and_or", r"[ \t]*&&[ \t]*", " || "),
    ("bool_or_and", r"[ \t]*\|\|[ \t]*", " && "),
    ("arith_add_sub", r"\s\+\s", " - "),
    ("arith_sub_add", r"\s-\s", " + "),
    ("arith_mul_div", r"\s\*\s", " / "),
    ("arith_div_mul", r"\s/\s", " * "),
    ("assign_add_sub", r"[ \t]*\+=[ \t]*", " -= "),
    ("assign_sub_add", r"[ \t]*-=[ \t]*", " += "),
    ("assign_mul_div", r"[ \t]*\*=[ \t]*", " /= "),
    ("assign_div_mul", r"[ \t]*/=[ \t]*", " *= "),
    ("assign_and_or", r"[ \t]*&=[ \t]*", " |= "),
    ("assign_or_and", r"[ \t]*\|=[ \t]*", " &= "),
    ("assign_shl_shr", r"[ \t]*<<=[ \t]*", " >>= "),
    ("assign_shr_shl", r"[ \t]*>>=[ \t]*", " <<= "),
    ("bit_and_or", r"\s&\s", " | "),
    ("bit_or_and", r"\s\|\s", " & "),
    ("bit_xor_or", r"\s\^\s", " | "),
    ("shift_left_right", r"\s<<\s", " >> "),
    ("shift_right_left", r"\s>>\s", " << "),
    ("bool_true_false", r"\btrue\b", "false"),
    ("bool_false_true", r"\bfalse\b", "true"),
    ("const_0_1", r"(?<![0-9A-Za-z_])0(?![0-9A-Za-z_])", "1"),
    ("const_1_0", r"(?<![0-9A-Za-z_])1(?![0-9A-Za-z_])", "0"),
    ("const_2_3", r"(?<![0-9A-Za-z_])2(?![0-9A-Za-z_])", "3"),
    ("const_3_2", r"(?<![0-9A-Za-z_])3(?![0-9A-Za-z_])", "2"),
    ("const_4_8", r"(?<![0-9A-Za-z_])4(?![0-9A-Za-z_])", "8"),
    ("const_8_4", r"(?<![0-9A-Za-z_])8(?![0-9A-Za-z_])", "4"),
    ("const_8_16", r"(?<![0-9A-Za-z_])8(?![0-9A-Za-z_])", "16"),
    ("const_16_8", r"(?<![0-9A-Za-z_])16(?![0-9A-Za-z_])", "8"),
    ("const_16_32", r"(?<![0-9A-Za-z_])16(?![0-9A-Za-z_])", "32"),
    ("const_32_16", r"(?<![0-9A-Za-z_])32(?![0-9A-Za-z_])", "16"),
    ("const_32_64", r"(?<![0-9A-Za-z_])32(?![0-9A-Za-z_])", "64"),
    ("const_64_32", r"(?<![0-9A-Za-z_])64(?![0-9A-Za-z_])", "32"),
    ("const_64_128", r"(?<![0-9A-Za-z_])64(?![0-9A-Za-z_])", "128"),
    ("const_128_64", r"(?<![0-9A-Za-z_])128(?![0-9A-Za-z_])", "64"),
    ("const_128_256", r"(?<![0-9A-Za-z_])128(?![0-9A-Za-z_])", "256"),
    ("const_256_128", r"(?<![0-9A-Za-z_])256(?![0-9A-Za-z_])", "128"),
]

FN_RE = re.compile(
    r"^\s*(?:pub(?:\([^)]+\))?\s+)?(?:const\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)",
    re.M,
)


@dataclass(frozen=True)
class Mutation:
    file_path: str
    start: int
    end: int
    replacement: str
    operator: str


@dataclass
class Candidate:
    file_rel: str
    test_filter: str
    mutation: Mutation
    line: int
    routine: str


@dataclass
class MutantResult:
    mutant_id: str
    file_rel: str
    routine: str
    operator: str
    line: int
    original: str
    replacement: str
    status: str
    exit_code: int
    duration_seconds: float
    command: str
    log_file: str


def compute_code_mask(text: str) -> List[bool]:
    mask = [True] * len(text)
    i = 0
    state = "code"
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if state == "code":
            if ch == "/" and nxt == "/":
                state = "line_comment"
                mask[i] = mask[i + 1] = False
                i += 2
                continue
            if ch == "/" and nxt == "*":
                state = "block_comment"
                mask[i] = mask[i + 1] = False
                i += 2
                continue
            if ch == '"':
                state = "string"
                mask[i] = False
                i += 1
                continue
            if ch == "'":
                state = "char"
                mask[i] = False
                i += 1
                continue
        elif state == "line_comment":
            mask[i] = False
            if ch == "\n":
                state = "code"
            i += 1
            continue
        elif state == "block_comment":
            mask[i] = False
            if ch == "*" and nxt == "/":
                mask[i + 1] = False
                i += 2
                state = "code"
                continue
            i += 1
            continue
        elif state == "string":
            mask[i] = False
            if ch == "\\" and nxt:
                mask[i + 1] = False
                i += 2
                continue
            if ch == '"':
                state = "code"
            i += 1
            continue
        elif state == "char":
            mask[i] = False
            if ch == "\\" and nxt:
                mask[i + 1] = False
                i += 2
                continue
            if ch == "'":
                state = "code"
            i += 1
            continue
        i += 1
    return mask


def find_mutations(file_path: str, text: str) -> List[Mutation]:
    mask = compute_code_mask(text)
    mutations: List[Mutation] = []
    for op_name, pattern, replacement in OP_PATTERNS:
        for match in re.finditer(pattern, text):
            start, end = match.span()
            if all(mask[i] for i in range(start, end)):
                mutations.append(
                    Mutation(
                        file_path=file_path,
                        start=start,
                        end=end,
                        replacement=replacement,
                        operator=op_name,
                    )
                )
    return mutations


def apply_mutation(text: str, mutation: Mutation) -> str:
    return text[: mutation.start] + mutation.replacement + text[mutation.end :]


def line_at(text: str, index: int) -> Tuple[int, str]:
    line_no = text.count("\n", 0, index) + 1
    line_start = text.rfind("\n", 0, index)
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1
    line_end = text.find("\n", index)
    if line_end == -1:
        line_end = len(text)
    return line_no, text[line_start:line_end]


def unified_diff_for_mutant(file_rel: str, original_text: str, mutated_text: str) -> str:
    return "".join(
        difflib.unified_diff(
            original_text.splitlines(keepends=True),
            mutated_text.splitlines(keepends=True),
            fromfile=file_rel,
            tofile=file_rel,
            n=3,
        )
    )


def find_routine(content: str, offset: int) -> str:
    routine = "<module>"
    for match in FN_RE.finditer(content[:offset]):
        routine = match.group(1)
    return routine


def build_candidates(
    file_rel: str, test_filter: str, content: str, target_count: int
) -> List[Candidate]:
    candidates = find_mutations(file_rel, content)
    if not candidates:
        raise RuntimeError(f"No mutation candidates in {file_rel}")

    random.shuffle(candidates)
    selected = candidates[:target_count]
    out: List[Candidate] = []
    for mutation in selected:
        line_no, _ = line_at(content, mutation.start)
        routine = find_routine(content, mutation.start)
        out.append(
            Candidate(
                file_rel=file_rel,
                test_filter=test_filter,
                mutation=mutation,
                line=line_no,
                routine=routine,
            )
        )
    return out


def run_mutation_suite(platform: str, seed: int, max_mutants: int) -> None:
    print(f"Starting mutation suite: platform={platform}", flush=True)
    random.seed(seed)

    artifacts_dir = SUITE_ROOT / "artifacts"
    logs_dir = SUITE_ROOT / "logs" / platform
    mutant_logs = logs_dir / "mutants"
    ensure_dir(artifacts_dir)
    ensure_dir(mutant_logs)

    originals: Dict[str, str] = {}
    for target in TARGETS:
        file_rel = target["file"]
        file_path = REPO_ROOT / file_rel
        originals[file_rel] = file_path.read_text(encoding="utf-8")

    candidates: List[Candidate] = []
    for target in TARGETS:
        file_rel = target["file"]
        target_candidates = build_candidates(
            file_rel=file_rel,
            test_filter=target["filter"],
            content=originals[file_rel],
            target_count=target["count"],
        )
        print(
            f"Candidate selection: file={file_rel} requested={target['count']} "
            f"selected={len(target_candidates)}",
            flush=True,
        )
        candidates.extend(target_candidates)

    if max_mutants > 0:
        candidates = candidates[:max_mutants]

    if len(candidates) < 300 and max_mutants == 0:
        raise RuntimeError(
            f"Not enough mutation candidates generated: {len(candidates)} (required at least 300)."
        )

    mutants_diff_path = artifacts_dir / f"mutants_{platform}.diff"
    mutants_csv_path = artifacts_dir / f"mutation_results_{platform}.csv"
    summary_json_path = artifacts_dir / f"mutation_summary_{platform}.json"
    run_manifest_path = artifacts_dir / f"mutation_run_manifest_{platform}.json"

    per_mutant_results: List[MutantResult] = []
    run_manifest = {
        "platform": platform,
        "seed": seed,
        "targets": TARGETS,
        "total_candidates_selected": len(candidates),
        "results": [],
    }

    if mutants_diff_path.exists():
        mutants_diff_path.unlink()

    try:
        for idx, candidate in enumerate(candidates, start=1):
            mutant_id = f"M{idx:04d}"
            file_path = REPO_ROOT / candidate.file_rel
            original = originals[candidate.file_rel]
            mutated = apply_mutation(original, candidate.mutation)
            file_path.write_text(mutated, encoding="utf-8")

            command = f"cargo test {candidate.test_filter} --quiet"
            log_path = mutant_logs / f"{mutant_id}.log"
            result = run_command(command=command, cwd=REPO_ROOT, log_path=log_path)
            status = "killed" if result.exit_code != 0 else "live"

            diff_text = unified_diff_for_mutant(candidate.file_rel, original, mutated)
            with mutants_diff_path.open("a", encoding="utf-8") as f:
                f.write(
                    f"### {mutant_id} | {candidate.file_rel}:{candidate.line} | {candidate.mutation.operator}\n"
                )
                f.write(diff_text)
                f.write("\n")

            mutant_result = MutantResult(
                mutant_id=mutant_id,
                file_rel=candidate.file_rel,
                routine=candidate.routine,
                operator=candidate.mutation.operator,
                line=candidate.line,
                original=original[candidate.mutation.start : candidate.mutation.end],
                replacement=candidate.mutation.replacement,
                status=status,
                exit_code=result.exit_code,
                duration_seconds=result.duration_seconds,
                command=command,
                log_file=str(log_path.relative_to(REPO_ROOT)),
            )
            per_mutant_results.append(mutant_result)

            run_manifest["results"].append(
                {
                    "mutant": {
                        "mutant_id": mutant_id,
                        "file_rel": candidate.file_rel,
                        "routine": candidate.routine,
                        "operator": candidate.mutation.operator,
                        "line": candidate.line,
                        "original": mutant_result.original,
                        "replacement": mutant_result.replacement,
                    },
                    "execution": result_to_jsonable(result),
                    "status": status,
                    "log_file": mutant_result.log_file,
                }
            )

            killed_so_far = sum(1 for r in per_mutant_results if r.status == "killed")
            print(
                f"[{platform}] mutant {idx}/{len(candidates)} {mutant_id} "
                f"status={status} killed_so_far={killed_so_far}",
                flush=True,
            )

            file_path.write_text(original, encoding="utf-8")
    finally:
        for file_rel, original in originals.items():
            (REPO_ROOT / file_rel).write_text(original, encoding="utf-8")

    with mutants_csv_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "mutant_id",
                "file",
                "routine",
                "operator",
                "line",
                "original",
                "replacement",
                "status",
                "exit_code",
                "duration_seconds",
                "command",
                "log_file",
            ]
        )
        for row in per_mutant_results:
            writer.writerow(
                [
                    row.mutant_id,
                    row.file_rel,
                    row.routine,
                    row.operator,
                    row.line,
                    row.original,
                    row.replacement,
                    row.status,
                    row.exit_code,
                    f"{row.duration_seconds:.6f}",
                    row.command,
                    row.log_file,
                ]
            )

    per_file = defaultdict(lambda: Counter())
    per_routine = defaultdict(lambda: Counter())
    live_mutants = []
    for row in per_mutant_results:
        per_file[row.file_rel]["total"] += 1
        per_file[row.file_rel][row.status] += 1
        key = f"{row.file_rel}::{row.routine}"
        per_routine[key]["total"] += 1
        per_routine[key][row.status] += 1
        if row.status == "live":
            live_mutants.append(
                {
                    "mutant_id": row.mutant_id,
                    "file": row.file_rel,
                    "routine": row.routine,
                    "operator": row.operator,
                    "line": row.line,
                    "original": row.original,
                    "replacement": row.replacement,
                    "log_file": row.log_file,
                }
            )

    per_file_summary = {}
    for file_rel, counts in per_file.items():
        total = counts["total"]
        killed = counts["killed"]
        live = counts["live"]
        per_file_summary[file_rel] = {
            "total_mutants": total,
            "killed": killed,
            "live": live,
            "kill_ratio": (killed / total) if total else 0.0,
        }

    per_routine_summary = {}
    for routine, counts in per_routine.items():
        total = counts["total"]
        killed = counts["killed"]
        live = counts["live"]
        per_routine_summary[routine] = {
            "total_mutants": total,
            "killed": killed,
            "live": live,
            "kill_ratio": (killed / total) if total else 0.0,
        }

    overall_total = len(per_mutant_results)
    overall_killed = sum(1 for r in per_mutant_results if r.status == "killed")
    overall_live = overall_total - overall_killed

    summary = {
        "platform": platform,
        "total_mutants": overall_total,
        "killed": overall_killed,
        "live": overall_live,
        "overall_kill_ratio": (overall_killed / overall_total) if overall_total else 0.0,
        "per_file": per_file_summary,
        "per_routine": per_routine_summary,
        "first_five_live_mutants": live_mutants[:5],
        "artifacts": {
            "mutants_diff": str(mutants_diff_path.relative_to(REPO_ROOT)),
            "mutants_csv": str(mutants_csv_path.relative_to(REPO_ROOT)),
            "run_manifest": str(run_manifest_path.relative_to(REPO_ROOT)),
        },
    }

    write_json(summary_json_path, summary)
    write_json(run_manifest_path, run_manifest)

    print(f"Mutation run complete for platform={platform}")
    print(f"Total mutants: {overall_total}")
    print(f"Killed: {overall_killed}")
    print(f"Live: {overall_live}")
    print(f"Kill ratio: {summary['overall_kill_ratio']:.4f}")
    print(f"Summary JSON: {summary_json_path.relative_to(REPO_ROOT)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run enhanced mutation adequacy suite.")
    parser.add_argument("--platform", required=True, choices=["windows", "wsl"])
    parser.add_argument("--seed", type=int, default=20260403)
    parser.add_argument("--max-mutants", type=int, default=0)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_mutation_suite(platform=args.platform, seed=args.seed, max_mutants=args.max_mutants)
