# Test Plan - smoltcp Security/Quality Project

## Test Objectives
- Evaluate test adequacy via mutation analysis on three complex modules and quantify kill ratios.
- Improve tests based on surviving non-equivalent mutants.
- Perform functional testing using input space partitioning for UDP parsing.
- Perform security fuzzing with sanitizers/backtraces to locate root causes of crashes.
- Perform conformance testing against RFC 791 (IPv4) and RFC 768 (UDP).
- Perform performance testing using loopback benchmarks and compare Windows vs WSL.
- Evaluate test data adequacy using white-box coverage metrics.
- Assess software safety using panic-safety tests and unsafe usage review.
- Apply defect correction if defects are found, and perform a small refactor that preserves behavior.

## Software Under Test
- Project: smoltcp 0.12.0 (see [README.md](../../README.md))
- Focus modules:
  - [src/storage/assembler.rs](../../src/storage/assembler.rs)
  - [src/wire/ipv4.rs](../../src/wire/ipv4.rs)
  - [src/wire/udp.rs](../../src/wire/udp.rs)

## Test Environment
- Windows 10 (PowerShell), Rust 1.91+ and Cargo installed.
- WSL Ubuntu 24.04.2 LTS, Rust 1.91+ and Cargo installed.
- Optional tools (installed if missing):
  - cargo-fuzz (libFuzzer runner)
  - cargo-llvm-cov (coverage)
- No tests run in parallel. Each suite is run sequentially.

## Configurations
- Default Cargo features, unless a suite requires specific flags.
- Each suite is executed on Windows and WSL independently.

## Test Suites and Oracles
1. Mutation Adequacy
   - 3 files, 100+ mutants each (>= 300 total).
   - Operators: arithmetic, relational, boolean, constant, and boundary mutations.
   - Test suites: module unit tests plus added targeted tests.
   - Outputs: mutants diff file, per-mutant kill log, summary metrics.

2. Input Space Partitioning (UDP)
   - Component: UDP Packet parsing and Repr::parse.
   - Model based on RFC 768 and smoltcp behavior.
   - Pairwise coverage with constraints.
   - Outputs: generated test frames, test case file, results summary.

3. Security Fuzzing + Sanitizer/Backtrace Analysis
   - Targets: packet_parser, tcp_headers, dhcp_header, ieee802154_header, sixlowpan_packet.
   - Use cargo-fuzz runs with bounded time/iterations.
   - For any crash: re-run with backtrace/sanitizer to locate root cause.
   - Outputs: corpus/crash inputs, stack traces, bug summaries (>= 6 if found).

4. Conformance Testing (IPv4/UDP)
   - Standards: RFC 791, RFC 768.
   - Focus: header parsing rules, checksum validation, version/length constraints.
   - Outputs: conformance test cases and pass/fail logs.

5. Performance Testing
   - Target: examples/loopback_benchmark.rs
   - Run multiple trials, collect throughput and total time.
   - Outputs: CSV summary and logs per platform.

6. White-Box Test Data Adequacy
   - Tool: cargo-llvm-cov (or equivalent).
   - Focus: coverage for ipv4, udp, assembler modules.
   - Outputs: coverage summary and reports per platform.

7. Software Safety
   - Panic safety tests on invalid inputs.
   - Unsafe usage inventory with rationale.
   - Outputs: safety test logs and unsafe usage report.

8. Defect Correction and Refactoring
   - Apply fixes if defects are found by suites above.
   - Apply a small behavior-preserving refactor.
   - Outputs: diffs and test confirmations.

## Evaluation Criteria
- Mutation adequacy: K/(M-E) per routine and per file.
- Input partitioning: pairwise coverage achieved; % tests passing.
- Fuzzing: number of unique crashes; root cause identified for each.
- Conformance: % tests passing; any deviations documented.
- Performance: median throughput and variance across runs and platforms.
- White-box adequacy: statement/branch coverage % for target modules.
- Safety: no panics on invalid inputs; unsafe usage reviewed.

## Test Deliverables
- Test automation scripts and harnesses per suite.
- Test case data sets and generated frames.
- Test logs per suite and per platform.
- Mutation diff file and summary metrics.
- Coverage reports.
- Incident reports for failures.

## Schedule (Sequential)
1. Create suites and harnesses.
2. Run suites on Windows (one-by-one).
3. Run suites on WSL (one-by-one).
4. Analyze results, add tests for live mutants, re-run relevant suites.
5. Document fixes/refactors if any.
6. Write test plan and final project reports.
