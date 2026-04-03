# Final Report Addendum: V1 Additions

## 1. Executive Summary (Additions)

- Mutation enhancement results:
  - Total mutants: 333 (Windows), 333 (WSL)
  - Kill ratio: 69.67% (Windows), 69.67% (WSL)
  - Live mutant highlights: M0004 (assembler::peek_front), M0009 (assembler::add), M0015 (assembler::fmt), M0020 (assembler::remove_front), M0038 (assembler::add)
- IPv4 combinatorial results:
  - Total cases: 216 (Windows), 216 (WSL)
  - Matched expectations: 216 (Windows), 216 (WSL)
- Microbench results:
  - ipv4_parse mean ns/iter: 10.726 (Windows), 12.148 (WSL)
  - udp_parse_emit mean ns/iter: 24.436 (Windows), 24.649 (WSL)
  - ring_buffer_cycle mean ns/iter: 0.474 (Windows), 0.474 (WSL)
- Fuzzing enhancement results:
  - Distinct error signatures: 0 (Windows), 0 (WSL)
  - Notable artifacts: none; Windows fuzz runs failed to start due to STATUS_DLL_NOT_FOUND (missing ASAN runtime DLL)
- White-box additions:
  - Coverage percent: 98.53% for IPv4 combinatorial (Windows/WSL) and 98.76% for microbench (Windows/WSL)
  - LCOV artifacts generated: IPv4 combinatorial + microbench

Portability and OS notes:
- Windows fuzzing is blocked by a missing ASAN runtime DLL (clang_rt.asan_dynamic-x86_64.dll); this is a portability gap for Windows execution.
- WSL (Ubuntu) fuzzing runs complete with the same targets and time budget but produced zero crash artifacts.

Note on structure: the v0 integration lives under security_testing/additions (not a v0_additions folder). The report addenda use addendum naming instead of *_v0plus.

## 2. Mutation Enhanced Suite

Artifacts:
- additions/mutation_enhanced/artifacts/mutation_summary_<platform>.json
- additions/mutation_enhanced/artifacts/mutation_run_manifest_<platform>.json
- additions/mutation_enhanced/artifacts/mutants_<platform>.diff

Key metrics:
- Total mutants: 333 (Windows), 333 (WSL)
- Kill ratio: 69.67% (Windows), 69.67% (WSL)
- Per-file kill ratios (Windows/WSL identical):
  - src/storage/assembler.rs: 0.8941
  - src/wire/ipv4.rs: 0.6136
  - src/wire/udp.rs: 0.5750
  - src/wire/tcp.rs: 0.6583

Live mutant analysis (top 5):
- M0004 src/storage/assembler.rs::peek_front const_0_1 line 154
- M0009 src/storage/assembler.rs::add rel_lt_le line 224
- M0015 src/storage/assembler.rs::fmt bool_and_or line 29
- M0020 src/storage/assembler.rs::remove_front rel_gt_ge line 289
- M0038 src/storage/assembler.rs::add rel_gt_ge line 267

## 3. IPv4 Combinatorial Suite

Artifacts:
- additions/ipv4_combinatorial/ipv4_cases_<platform>.csv
- additions/ipv4_combinatorial/artifacts/ipv4_combinatorial_summary_<platform>.json

Key findings:
- Oracle aligned to smoltcp's default fragmentation behavior; suite now passes on both platforms.
- 216/216 cases matched; exit code 0 for Windows and WSL.

## 4. Performance Microbench Suite

Artifacts:
- additions/perf_microbench/artifacts/microbench_summary_<platform>.json
- additions/perf_microbench/artifacts/microbench_metrics_<platform>.csv

Key findings:
- Windows and WSL both completed successfully; metrics captured across 5 repetitions.
- Mean ns/iter (Windows): ipv4_parse 10.726, udp_parse_emit 24.436, ring_buffer_cycle 0.474.
- Mean ns/iter (WSL): ipv4_parse 12.148, udp_parse_emit 24.649, ring_buffer_cycle 0.474.

## 5. Fuzzing Enhanced Suite

Artifacts:
- additions/fuzzing_enhanced/artifacts/fuzzing_summary_<platform>.json
- additions/fuzzing_enhanced/logs/<platform>/repro_*.log

Key findings:
- Windows: all five targets failed to launch with STATUS_DLL_NOT_FOUND; no artifacts produced (missing clang_rt.asan_dynamic-x86_64.dll).
- WSL: all five targets ran for 180 seconds each and produced zero crash artifacts.
- Distinct error signatures: 0 on both platforms.

## 6. White-Box Additions

Artifacts:
- additions/whitebox_safety_enhanced/artifacts/whitebox_safety_summary_<platform>.json
- additions/whitebox_safety_enhanced/artifacts/coverage_*_<platform>.lcov

Key findings:
- IPv4 combinatorial coverage succeeded on both platforms (98.53% regions; 273 regions, 4 missed).
- Microbench coverage succeeded on both platforms (98.76% regions; 161 regions, 2 missed).
- LCOV artifacts were generated for both IPv4 combinatorial and microbench.

## 7. Defect Correction Status

The existing ipv4 check_len ordering fix is already present in src/wire/ipv4.rs. No fixes were applied during this addendum run; all defects were recorded before any remediation.

## 8. Remaining Gaps

- Resolve Windows fuzzing runtime dependency issues (STATUS_DLL_NOT_FOUND, missing clang_rt.asan_dynamic-x86_64.dll).
- Increase fuzzing budgets and/or expand corpora/targets to reach >= 6 distinct errors (WSL currently 0).
