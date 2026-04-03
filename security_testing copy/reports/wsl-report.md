# WSL Report

Date: 2026-04-02

## Environment
- OS: WSL Ubuntu 24.04.2 LTS
- Rust toolchains: stable (project default), nightly 1.96.0-nightly for fuzzing
- Tooling installed during runs: cargo-fuzz 0.13.1, cargo-llvm-cov 0.8.5

## Summary (WSL)
- Mutation adequacy: 333 mutants, overall kill ratio 0.6877; per-file ratios listed below.
- Input partitioning: 480 generated cases, all passed.
- Conformance: 9 cases, all matched expected behavior; two standard deviations noted.
- Safety: panic-safety checks passed; unsafe inventory total 18 occurrences.
- Performance: loopback_perf_suite average 52.1534 Gbps (median 51.131, min 51.131, max 53.687).
- White-box adequacy (cargo-llvm-cov): total coverage 79.60% regions, 81.09% functions, 79.82% lines.
- Fuzzing: all 5 targets completed with no crashes in 60s runs.

## Mutation Adequacy (WSL)
- Overall: 333 mutants, 229 killed, 104 survived (raw kill ratio 0.6877).
- Per file:
  - [src/storage/assembler.rs](src/storage/assembler.rs): 76/85 killed (0.8941).
  - [src/wire/ipv4.rs](src/wire/ipv4.rs): 54/88 killed (0.6136).
  - [src/wire/udp.rs](src/wire/udp.rs): 23/40 killed (0.5750).
  - [src/wire/tcp.rs](src/wire/tcp.rs): 76/120 killed (0.6333).
- Equivalent mutant analysis: not yet completed; 5 survivors will be analyzed in the final report.
- Artifacts: [security_testing/mutation/logs/mutation_results_wsl.csv](security_testing/mutation/logs/mutation_results_wsl.csv), [security_testing/mutation/mutants.diff](security_testing/mutation/mutants.diff), [security_testing/mutation/logs/mutation_run_wsl.log](security_testing/mutation/logs/mutation_run_wsl.log)

## Input Space Partitioning (UDP)
- Model dimensions: buf_len, len_field, dst_port, checksum_mode, ip_family, rx_on.
- Generated cases: 480; all cases passed.
- Note: smoltcp accepts checksum=0 for UDP over IPv6 (observed in both partitioning and conformance).
- Artifacts: [security_testing/input_partition/udp_cases.csv](security_testing/input_partition/udp_cases.csv), [security_testing/input_partition/logs/input_partition_wsl.log](security_testing/input_partition/logs/input_partition_wsl.log)

## Conformance Testing (IPv4/UDP)
- 9 cases executed; all matched expected behavior in current implementation.
- Observed deviations from strict RFC expectations:
  - IPv4 header length less than 20 bytes is accepted when buffer is long enough.
  - UDP over IPv6 accepts checksum=0 (RFCs generally require checksum on IPv6).
- Artifacts: [security_testing/conformance/conformance_results.csv](security_testing/conformance/conformance_results.csv), [security_testing/conformance/logs/conformance_wsl.log](security_testing/conformance/logs/conformance_wsl.log)

## Safety
- Panic-safety tests: passed for invalid input buffers.
- Unsafe inventory: total 18 occurrences; top entries:
  - [src/phy/sys/tuntap_interface.rs](src/phy/sys/tuntap_interface.rs): 6
  - [src/phy/sys/bpf.rs](src/phy/sys/bpf.rs): 5
  - [src/phy/sys/raw_socket.rs](src/phy/sys/raw_socket.rs): 5
  - Remaining 2 occurrences are in other files (see CSV).
- Artifacts: [security_testing/safety/unsafe_inventory.csv](security_testing/safety/unsafe_inventory.csv), [security_testing/safety/logs/safety_wsl.log](security_testing/safety/logs/safety_wsl.log)

## Performance (Loopback)
- A loopback-specific harness was used (loopback_perf_suite) for cross-platform comparability.
- Results (5 runs): avg 52.1534 Gbps, median 51.131, min 51.131, max 53.687; duration avg 0.0206 s.
- Artifacts: [security_testing/performance/logs/loopback_benchmark_wsl.csv](security_testing/performance/logs/loopback_benchmark_wsl.csv), [security_testing/performance/logs/loopback_benchmark_wsl.log](security_testing/performance/logs/loopback_benchmark_wsl.log)

## White-Box Adequacy (Coverage)
- Total coverage: 79.60% regions, 81.09% functions, 79.82% lines.
- Target modules (region/function/line coverage):
  - [src/storage/assembler.rs](src/storage/assembler.rs): 98.28% / 98.41% / 98.46%
  - [src/wire/ipv4.rs](src/wire/ipv4.rs): 90.12% / 96.10% / 90.65%
  - [src/wire/udp.rs](src/wire/udp.rs): 90.98% / 91.67% / 87.45%
  - [src/wire/tcp.rs](src/wire/tcp.rs): 72.58% / 83.70% / 74.45%
- Artifacts: [security_testing/white_box_adequacy/logs/llvm_cov_wsl.log](security_testing/white_box_adequacy/logs/llvm_cov_wsl.log)

## Security Fuzzing (WSL)
- Targets: packet_parser, tcp_headers, dhcp_header, ieee802154_header, sixlowpan_packet.
- All targets executed for 60s each with libFuzzer; no crashes observed.
- Artifacts: [security_testing/fuzzing/logs/fuzzing_wsl.log](security_testing/fuzzing/logs/fuzzing_wsl.log)
