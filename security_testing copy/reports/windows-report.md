# Windows Report

Date: 2026-04-02

## Environment
- OS: Windows 10
- Rust toolchains: stable (project default), nightly 1.96.0-nightly for fuzzing attempts
- Tooling installed during runs: cargo-fuzz 0.13.1, cargo-llvm-cov 0.8.5

## Summary (Windows)
- Mutation adequacy: 333 mutants, overall kill ratio 0.6877; per-file ratios listed below.
- Input partitioning: 480 generated cases, all passed.
- Conformance: 9 cases, all matched expected behavior; two standard deviations noted.
- Safety: panic-safety checks passed; unsafe inventory total 18 occurrences.
- Performance: loopback_perf_suite average 17.1062 Gbps (median 16.777, min 16.026, max 19.174).
- White-box adequacy (cargo-llvm-cov): total coverage 80.63% regions, 82.35% functions, 81.00% lines.
- Fuzzing: blocked on Windows due to libFuzzer/MSVC coverage link errors; deferred to WSL.

## Mutation Adequacy (Windows)
- Overall: 333 mutants, 229 killed, 104 survived (raw kill ratio 0.6877).
- Per file:
  - src/storage/assembler.rs: 76/85 killed (0.8941).
  - src/wire/ipv4.rs: 54/88 killed (0.6136).
  - src/wire/udp.rs: 23/40 killed (0.5750).
  - src/wire/tcp.rs: 76/120 killed (0.6333).
- Equivalent mutant analysis: not yet completed; 5 survivors will be analyzed during the cross-platform phase.
- Artifacts: [security_testing/mutation/logs/mutation_results_windows.csv](security_testing/mutation/logs/mutation_results_windows.csv), [security_testing/mutation/mutants.diff](security_testing/mutation/mutants.diff), [security_testing/mutation/logs/mutation_run_windows.log](security_testing/mutation/logs/mutation_run_windows.log)

## Input Space Partitioning (UDP)
- Model dimensions: buf_len, len_field, dst_port, checksum_mode, ip_family, rx_on.
- Generated cases: 480; all cases passed.
- Note: smoltcp accepts checksum=0 for UDP over IPv6 (observed in both partitioning and conformance).
- Artifacts: [security_testing/input_partition/udp_cases.csv](security_testing/input_partition/udp_cases.csv), [security_testing/input_partition/logs/input_partition_windows.log](security_testing/input_partition/logs/input_partition_windows.log)

## Conformance Testing (IPv4/UDP)
- 9 cases executed; all matched expected behavior in current implementation.
- Observed deviations from strict RFC expectations:
  - IPv4 header length less than 20 bytes is accepted when buffer is long enough.
  - UDP over IPv6 accepts checksum=0 (RFCs generally require checksum on IPv6).
- Artifacts: [security_testing/conformance/conformance_results.csv](security_testing/conformance/conformance_results.csv), [security_testing/conformance/logs/conformance_windows.log](security_testing/conformance/logs/conformance_windows.log)

## Safety
- Panic-safety tests: passed for invalid input buffers.
- Unsafe inventory: total 18 occurrences; top entries:
  - src/phy/sys/tuntap_interface.rs: 6
  - src/phy/sys/bpf.rs: 5
  - src/phy/sys/raw_socket.rs: 5
  - Remaining 2 occurrences are in other files (see CSV).
- Artifacts: [security_testing/safety/unsafe_inventory.csv](security_testing/safety/unsafe_inventory.csv), [security_testing/safety/logs/safety_windows.log](security_testing/safety/logs/safety_windows.log)

## Performance (Loopback)
- Windows cannot build examples/loopback_benchmark.rs due to TunTap being Linux-only.
- A Windows-specific loopback harness was used (loopback_perf_suite) to measure throughput.
- Results (5 runs): avg 17.1062 Gbps, median 16.777, min 16.026, max 19.174; duration avg 0.063 s.
- Artifacts: [security_testing/performance/logs/loopback_benchmark_windows.csv](security_testing/performance/logs/loopback_benchmark_windows.csv), [security_testing/performance/logs/loopback_benchmark_windows.log](security_testing/performance/logs/loopback_benchmark_windows.log)

## White-Box Adequacy (Coverage)
- Total coverage: 80.63% regions, 82.35% functions, 81.00% lines.
- Target modules (region/function/line coverage):
  - storage/assembler.rs: 98.28% / 98.41% / 98.46%
  - wire/ipv4.rs: 90.12% / 96.10% / 90.65%
  - wire/udp.rs: 90.98% / 91.67% / 87.45%
  - wire/tcp.rs: 72.58% / 83.70% / 74.45%
- Artifacts: [security_testing/white_box_adequacy/logs/llvm_cov_windows.log](security_testing/white_box_adequacy/logs/llvm_cov_windows.log)

## Security Fuzzing (Windows)
- Nightly toolchain installed; cargo-fuzz attempts failed on Windows due to libFuzzer/MSVC coverage link errors.
- Errors include missing sancov symbols (e.g., __start___sancov_cntrs) and earlier STATUS_DLL_NOT_FOUND when ASan runtime was required.
- Fuzzing will be executed on WSL where libFuzzer and sanitizers are supported.
- Artifacts: [security_testing/fuzzing/logs/fuzzing_windows.log](security_testing/fuzzing/logs/fuzzing_windows.log)

## Portability Notes (Windows)
- Fuzzing failed under the MSVC toolchain due to sanitizer-coverage instrumentation and runtime availability issues. The log shows a runtime failure (STATUS_DLL_NOT_FOUND, exit code 0xc0000135) and unresolved sancov symbols (LNK2019 for __start___sancov_cntrs), which prevents libFuzzer from linking or running on Windows with this setup. See [security_testing/fuzzing/logs/fuzzing_windows.log](security_testing/fuzzing/logs/fuzzing_windows.log).
- The official loopback performance example is not portable to Windows because `TunTapInterface` is gated to Linux/Android. The build fails with an unresolved import of `smoltcp::phy::TunTapInterface`. See [security_testing/performance/logs/loopback_benchmark_windows.log](security_testing/performance/logs/loopback_benchmark_windows.log).
- These issues did not occur on WSL/Linux, indicating OS/toolchain portability gaps for fuzzing and the TunTap-based example, even though the core library tests and coverage ran on Windows.
