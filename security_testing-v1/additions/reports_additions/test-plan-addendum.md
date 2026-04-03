# Test Plan Addendum: V1 Additions

## 1. Purpose

This addendum layers the best parts of security_testing-v0 onto security_testing-v1 without modifying any existing v1 files. All new suites live under security_testing-v1/additions and run independently of the original v1 suites.

## 2. New Suites Added

1. mutation_enhanced
   - Broader operator coverage with code masking and safer constant matching.
   - JSON summary, per-mutant logs, run manifest, and diff artifacts.
2. fuzzing_enhanced
   - Sanitizer-backed fuzzing without the Windows -s none issue.
   - Crash reproduction and distinct signature summaries.
3. ipv4_combinatorial
   - IPv4 category-partition coverage (216 cases) in a standalone Cargo suite.
   - CSV case matrix and JSON run summary.
4. perf_microbench
   - Microbench metrics (ipv4_parse, udp_parse_emit, ring_buffer_cycle) with repeated runs.
   - CSV metrics and JSON summary.
5. whitebox_safety_enhanced
   - Coverage (llvm-cov + lcov) for the new suites.
   - Optional static checks (clippy and cargo-audit) recorded in JSON.

## 3. Evidence Outputs

Each suite writes:
- logs/<platform>/... for command output and failures.
- artifacts/*.json for machine-readable summaries.
- CSV or diff artifacts where applicable.

## 4. Execution Order (Additions Only)

Recommended order for add-on suites:
1. mutation_enhanced
2. ipv4_combinatorial
3. perf_microbench
4. fuzzing_enhanced
5. whitebox_safety_enhanced

## 5. Notes

- These suites do not overwrite any v1 test data.
- The IPv4 combinatorial suite aligns expected results with smoltcp behavior (header_len < 20 accepted when buffer length is sufficient).
- Fragmented IPv4 cases are expected to be rejected unless proto-ipv4-fragmentation is enabled.
