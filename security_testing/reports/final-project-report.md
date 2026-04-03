# Final Project Report - smoltcp

Date: 2026-04-02

## Scope
- Project: smoltcp 0.12.0
- Focus modules: [src/storage/assembler.rs](src/storage/assembler.rs), [src/wire/ipv4.rs](src/wire/ipv4.rs), [src/wire/udp.rs](src/wire/udp.rs), [src/wire/tcp.rs](src/wire/tcp.rs)
- Suites executed sequentially on Windows and WSL.

## Environments
- Windows 10 (PowerShell)
- WSL Ubuntu 24.04.2 LTS

## Test Suites Executed
- Mutation adequacy (333 mutants across four files)
- Input space partitioning (UDP parsing)
- Conformance testing (RFC 791, RFC 768)
- Security fuzzing (libFuzzer targets)
- Performance testing (custom loopback harness)
- White-box coverage (cargo-llvm-cov)
- Safety testing (panic safety + unsafe inventory)

## Results Summary
- Mutation adequacy: 333 mutants, 229 killed, 104 survived (kill ratio 0.6877) on both platforms.
- Input partitioning: 480 cases; all passed on both platforms.
- Conformance: 9 cases passed; two deviations from strict RFC expectations documented.
- Safety: panic-safety checks passed; unsafe inventory totals 18 occurrences.
- Fuzzing: Windows blocked by libFuzzer/MSVC coverage link errors; WSL completed 5 targets with no crashes in 60s runs.
- Performance: Windows avg 17.1062 Gbps; WSL avg 52.1534 Gbps using the same loopback harness.
- Coverage (regions/functions/lines): Windows 80.63% / 82.35% / 81.00%; WSL 79.60% / 81.09% / 79.82%.

## Portability Testing Across OS/Compiler Configurations
- Windows (MSVC) fuzzing failed due to sanitizer-coverage and runtime issues. The log shows STATUS_DLL_NOT_FOUND (exit code 0xc0000135) and unresolved sancov symbols (LNK2019 for __start___sancov_cntrs), which prevents libFuzzer-based targets from linking or running. See [security_testing/fuzzing/logs/fuzzing_windows.log](security_testing/fuzzing/logs/fuzzing_windows.log).
- The loopback performance example is not portable to Windows because `TunTapInterface` is gated to Linux/Android. The Windows build fails with an unresolved import of `smoltcp::phy::TunTapInterface`, so a custom loopback harness was required. See [security_testing/performance/logs/loopback_benchmark_windows.log](security_testing/performance/logs/loopback_benchmark_windows.log).
- These failures are OS/toolchain-specific: WSL/Linux (GNU/LLVM toolchain) ran fuzzing and the loopback benchmark path without the above errors, while Windows (MSVC) could not. This indicates portability gaps for certain tooling and OS-specific interfaces, even though core library tests (mutation, partitioning, conformance, safety, coverage) ran on both platforms.
- Hardware portability was not evaluated beyond the single host machine; only OS/toolchain differences were tested.

## Observations
- The implementation accepts IPv4 headers smaller than 20 bytes if the buffer is long enough.
- UDP over IPv6 accepts checksum=0, diverging from strict RFC guidance.
- WSL consistently outperforms Windows in loopback throughput, likely due to Linux networking stack behavior.
- Coverage is stable across platforms, with WSL slightly lower in total percentages.

## Limitations and Open Items
- Equivalent mutant analysis for 5 survivors is still pending.
- Fuzzing time budget was limited to 60 seconds per target; longer campaigns could surface deeper issues.

## Artifacts
- Test plan: [security_testing/reports/test-plan.md](security_testing/reports/test-plan.md)
- Windows results: [security_testing/reports/windows-report.md](security_testing/reports/windows-report.md)
- WSL results: [security_testing/reports/wsl-report.md](security_testing/reports/wsl-report.md)
