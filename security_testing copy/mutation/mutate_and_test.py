#!/usr/bin/env python3
"""Generate first-order mutants, run tests, and log kill results."""

from __future__ import annotations

import argparse
import csv
import os
import random
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class Mutation:
    file_path: str
    start: int
    end: int
    replacement: str
    operator: str


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

# Regex patterns are kept conservative to avoid generics and comments.
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
    ("const_0_1", r"\b0\b", "1"),
    ("const_1_0", r"\b1\b", "0"),
    ("const_2_3", r"\b2\b", "3"),
    ("const_3_2", r"\b3\b", "2"),
    ("const_4_8", r"\b4\b", "8"),
    ("const_8_4", r"\b8\b", "4"),
    ("const_8_16", r"\b8\b", "16"),
    ("const_16_8", r"\b16\b", "8"),
    ("const_16_32", r"\b16\b", "32"),
    ("const_32_16", r"\b32\b", "16"),
    ("const_32_64", r"\b32\b", "64"),
    ("const_64_32", r"\b64\b", "32"),
    ("const_64_128", r"\b64\b", "128"),
    ("const_128_64", r"\b128\b", "64"),
    ("const_128_256", r"\b128\b", "256"),
    ("const_256_128", r"\b256\b", "128"),
]


def compute_code_mask(text: str) -> List[bool]:
    """Return a boolean mask of positions that are code (not in comment/string)."""
    mask = [True] * len(text)
    i = 0
    state = "code"  # code, line_comment, block_comment, string, char
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
            if ch == "\"":
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
            if ch == "\"":
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


def format_diff(line_no: int, original_line: str, mutated_line: str) -> str:
    return "@@ -{ln},1 +{ln},1 @@\n-{orig}\n+{mut}\n".format(
        ln=line_no, orig=original_line, mut=mutated_line
    )


def run_tests(repo_root: str, test_filter: str) -> Tuple[int, float, str]:
    start = time.time()
    result = subprocess.run(
        ["cargo", "test", test_filter],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    duration = time.time() - start
    return result.returncode, duration, result.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", required=True)
    parser.add_argument("--seed", type=int, default=20260402)
    parser.add_argument("--output-dir", default="logs")
    parser.add_argument("--max-mutants", type=int, default=0)
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    output_dir = os.path.join(script_dir, args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    random.seed(args.seed)

    all_mutants: List[Tuple[str, Mutation]] = []
    diff_path = os.path.join(script_dir, "mutants.diff")

    with open(diff_path, "w", newline="", encoding="utf-8") as diff_file:
        for target in TARGETS:
            abs_path = os.path.join(repo_root, target["file"])
            with open(abs_path, "r", encoding="utf-8") as f:
                original = f.read()
            candidates = find_mutations(target["file"], original)
            if not candidates:
                raise RuntimeError(f"No mutation candidates in {target['file']}")

            random.shuffle(candidates)
            selected = candidates[: target["count"]]
            for idx, mutation in enumerate(selected, 1):
                mutant_id = f"{os.path.basename(target['file'])}-{idx:03d}"
                mutated = apply_mutation(original, mutation)
                line_no, orig_line = line_at(original, mutation.start)
                _, mut_line = line_at(mutated, mutation.start)
                diff_file.write(f"### {mutant_id} {target['file']} {mutation.operator}\n")
                diff_file.write(format_diff(line_no, orig_line, mut_line))
                diff_file.write("\n")
                all_mutants.append((target["filter"], mutation))

    if args.max_mutants and args.max_mutants > 0:
        all_mutants = all_mutants[: args.max_mutants]

    print(f"Generated {len(all_mutants)} mutants")

    csv_path = os.path.join(output_dir, f"mutation_results_{args.platform}.csv")
    log_path = os.path.join(output_dir, f"mutation_run_{args.platform}.log")

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file, open(
        log_path, "w", encoding="utf-8"
    ) as log_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "mutant_id",
                "file",
                "line",
                "operator",
                "status",
                "duration_s",
                "test_filter",
            ]
        )

        log_file.write(f"Total mutants: {len(all_mutants)}\n\n")

        for index, (test_filter, mutation) in enumerate(all_mutants, 1):
            abs_path = os.path.join(repo_root, mutation.file_path)
            with open(abs_path, "r", encoding="utf-8") as f:
                original = f.read()

            mutated = apply_mutation(original, mutation)
            line_no, orig_line = line_at(original, mutation.start)
            mutant_id = f"mutant-{index:04d}"

            log_file.write(f"=== {mutant_id} {mutation.file_path} {mutation.operator} ===\n")
            log_file.write(f"Line {line_no}: {orig_line}\n")
            print(f"Running {mutant_id} ({index}/{len(all_mutants)})")

            try:
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(mutated)

                code, duration, output = run_tests(repo_root, test_filter)
                status = "killed" if code != 0 else "survived"
                log_file.write(output)
                log_file.write("\n")
            finally:
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(original)

            writer.writerow(
                [
                    mutant_id,
                    mutation.file_path,
                    line_no,
                    mutation.operator,
                    status,
                    f"{duration:.2f}",
                    test_filter,
                ]
            )
            csv_file.flush()
            log_file.flush()

    return 0


if __name__ == "__main__":
    sys.exit(main())
