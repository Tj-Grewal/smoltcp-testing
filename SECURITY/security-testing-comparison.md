# Security Testing Comparison: security_testing vs security_testing-v1
Date: 2026-04-03

## Overall Verdict
Overall winner: security_testing (new) for completeness and auditability. It is the only version that shows a concrete defect correction and produces fuzzing artifacts, and it has structured JSON summaries for every suite. security_testing-v1 is stronger for consistency across Windows/WSL and broader protocol coverage in mutation and safety, but it does not document any defect fix and it found no fuzzing crashes.

## Requirement Scorecard (SECURITY/1)
| Requirement | security_testing | security_testing-v1 | Better |
| --- | --- | --- | --- |
| Mutation adequacy evaluation (>=300) | 350 mutants; WSL kill ratio 9.14% | 333 mutants; kill ratio 68.77% on both | Split (scale vs consistency) |
| Test-suite improvement from adequacy | Partial evidence; no clear new tests | Not documented | Tie (both partial) |
| Functional testing (combinatorial/partition) | IPv4 combinatorial, 216 cases | UDP partitioning, 480 cases | Split (method vs case volume) |
| Security analysis and fuzzing | WSL 3 distinct crash signatures; Windows blocked | WSL 0 crashes; Windows blocked | security_testing |
| Conformance testing | 9/9 pass both platforms | 9/9 pass; deviations documented | Tie (v1 has more commentary) |
| Performance testing | Microbench ns/iter metrics | Loopback throughput Gbps | Split (different focus) |
| White-box adequacy | 80.63% Win, 5.09% WSL; Win clippy/tests fail | 80.63% Win, 79.60% WSL | security_testing-v1 |
| Software safety | clippy + cargo audit (Win audit exit 1; WSL audit unavailable) | Unsafe inventory = 18 | Split (different safety signals) |
| Defect correction | Yes, parser safety fix | Not documented | security_testing |
| Refactoring | Minimal, safety-oriented | Not documented | security_testing |

## Weighted Scoring Rubric (100-point)
Scoring is 0-5 per category. Weighted points = weight * (score/5). Scores are based on available artifacts; when evidence is missing or not comparable, the score is reduced.

| Category | Weight | security_testing score | security_testing-v1 score | Rationale (short) |
| --- | --- | --- | --- | --- |
| Mutation adequacy | 15 | 3 | 4 | New meets scale but WSL filters are narrow; v1 is consistent across platforms. |
| Test-suite improvement | 10 | 2 | 1 | Partial evidence vs not documented. |
| Functional testing | 10 | 4 | 4 | Both passed; different protocol focus. |
| Security fuzzing | 15 | 3 | 2 | New has 3 WSL signatures; v1 has none. |
| Conformance testing | 10 | 4 | 4 | 9/9 on both. |
| Performance testing | 10 | 3 | 3 | Both produce stable metrics, different units. |
| White-box adequacy | 10 | 2 | 4 | New WSL coverage very low; v1 is balanced. |
| Software safety | 10 | 3 | 3 | New runs clippy/audit but Windows failures; v1 has unsafe inventory. |
| Defect correction | 5 | 5 | 1 | New includes a fix in [src/wire/ipv4.rs](src/wire/ipv4.rs); v1 does not document a fix. |
| Refactoring | 5 | 2 | 1 | Minimal safety refactor vs not documented. |

Weighted totals:
- security_testing: 61.0 / 100
- security_testing-v1: 58.0 / 100

Numeric winner: security_testing by a narrow margin. The margin is sensitive to fuzzing and defect-correction weights.

## Key Metrics Side-by-Side
| Dimension | security_testing | security_testing-v1 | Notes |
| --- | --- | --- | --- |
| Mutation scale | 350 mutants | 333 mutants | v1 covers UDP/TCP; new covers storage + IPv4 only |
| Mutation kill ratio | Win 67.71%, WSL 9.14% | 68.77% on both | WSL run in new uses narrow single-test filters |
| Functional cases | 216 IPv4 frames (216/216 pass) | 480 UDP cases (all pass) | Different protocol focus |
| Conformance cases | 9/9 pass | 9/9 pass | v1 documents RFC deviations explicitly |
| Fuzzing findings | 3 distinct WSL signatures; Win blocked | 0 crashes; Win blocked | New closer to >=6 goal but still short |
| Performance metrics | ipv4_parse 4.03 ns/iter (Win mean) | 17.1062 Gbps avg (Win) | Different performance strategy |
| White-box coverage | 80.63% Win; 5.09% WSL | 80.63% Win; 79.60% WSL | New WSL coverage likely misconfigured |
| Safety evidence | clippy + cargo audit + tests | unsafe inventory CSV | Complementary, not equivalent |

## Charts

### Mutation kill ratios
```mermaid
xychart-beta
	title "Mutation Kill Ratio by Platform"
	x-axis ["sec_test Win","sec_test WSL","v1 Win","v1 WSL"]
	y-axis "Kill ratio" 0 1
	bar [0.6771,0.0914,0.6877,0.6877]
```

### Fuzzing signatures
```mermaid
xychart-beta
	title "Distinct Fuzzing Signatures"
	x-axis ["sec_test Win","sec_test WSL","v1 Win","v1 WSL"]
	y-axis "Distinct signatures" 0 6
	bar [0,3,0,0]
```

### Performance metrics
```mermaid
xychart-beta
	title "security_testing Microbench Means (ns/iter)"
	x-axis ["ipv4_parse","udp_parse_emit","ring_buffer_cycle"]
	y-axis "ns/iter" 0 80
	bar "Windows" [4.0272,17.7136,76.8812]
	bar "WSL" [4.7872,17.0178,26.4368]
```

```mermaid
xychart-beta
	title "security_testing-v1 Loopback Throughput (Gbps)"
	x-axis ["Windows","WSL"]
	y-axis "Gbps" 0 60
	bar [17.1062,52.1534]
```

## Execution Strategy Differences
- security_testing uses sequential suite scripts with JSON summaries and per-platform logs, plus consistent naming and manifests that capture test filters.
- security_testing-v1 uses per-suite run scripts and separate harness crates; target build outputs are stored inside the suite folders, increasing noise.
- security_testing includes explicit defect correction evidence in [src/wire/ipv4.rs](src/wire/ipv4.rs); security_testing-v1 does not show a fix.
- File sweep shows security_testing has far fewer files than security_testing-v1 because v1 includes target build artifacts.

## Appendix A: Per-File Mutation Coverage

security_testing (kill ratio by platform):

| File | Windows kill ratio | WSL kill ratio |
| --- | --- | --- |
| [src/storage/assembler.rs](src/storage/assembler.rs) | 0.8417 | 0.0000 |
| [src/storage/ring_buffer.rs](src/storage/ring_buffer.rs) | 0.7182 | 0.1636 |
| [src/wire/ipv4.rs](src/wire/ipv4.rs) | 0.4750 | 0.1167 |

security_testing-v1 (reported same for Windows and WSL):

| File | Kill ratio |
| --- | --- |
| [src/storage/assembler.rs](src/storage/assembler.rs) | 0.8941 |
| [src/wire/ipv4.rs](src/wire/ipv4.rs) | 0.6136 |
| [src/wire/udp.rs](src/wire/udp.rs) | 0.5750 |
| [src/wire/tcp.rs](src/wire/tcp.rs) | 0.6333 |

## Appendix B: Safety Findings Summary

security_testing:
- Coverage regions: 80.63% Windows, 5.09% WSL (coverage disparity is likely configuration-related).
- clippy: Windows exit 101, WSL exit 0.
- Full tests: Windows exit 101, WSL exit 0.
- cargo_audit: Windows exit 1; WSL unavailable.

security_testing-v1:
- Panic-safety tests passed (per [security_testing-v1/reports/windows-report.md](security_testing-v1/reports/windows-report.md) and [security_testing-v1/reports/wsl-report.md](security_testing-v1/reports/wsl-report.md)).
- Unsafe inventory totals 18 occurrences, concentrated in the files below:

| File | Unsafe count |
| --- | --- |
| [src/phy/sys/tuntap_interface.rs](src/phy/sys/tuntap_interface.rs) | 6 |
| [src/phy/sys/bpf.rs](src/phy/sys/bpf.rs) | 5 |
| [src/phy/sys/raw_socket.rs](src/phy/sys/raw_socket.rs) | 5 |
| [src/phy/sys/mod.rs](src/phy/sys/mod.rs) | 2 |

## Evidence Index
- security_testing reports: [security_testing/90_reports/FINAL_PROJECT_REPORT.md](security_testing/90_reports/FINAL_PROJECT_REPORT.md), [security_testing/90_reports/TEST_PLAN.md](security_testing/90_reports/TEST_PLAN.md)
- security_testing mutation summaries: [security_testing/01_mutation/artifacts/mutation_summary_windows.json](security_testing/01_mutation/artifacts/mutation_summary_windows.json), [security_testing/01_mutation/artifacts/mutation_summary_wsl.json](security_testing/01_mutation/artifacts/mutation_summary_wsl.json), [security_testing/01_mutation/artifacts/mutation_run_manifest_wsl.json](security_testing/01_mutation/artifacts/mutation_run_manifest_wsl.json)
- security_testing combinatorial and fuzzing: [security_testing/02_combinatorial/artifacts/combinatorial_summary_windows.json](security_testing/02_combinatorial/artifacts/combinatorial_summary_windows.json), [security_testing/03_fuzzing_sanitizers/artifacts/fuzzing_summary_wsl.json](security_testing/03_fuzzing_sanitizers/artifacts/fuzzing_summary_wsl.json)
- security_testing performance and white-box: [security_testing/05_performance/artifacts/performance_summary_windows.json](security_testing/05_performance/artifacts/performance_summary_windows.json), [security_testing/06_whitebox_safety/artifacts/whitebox_safety_summary_windows.json](security_testing/06_whitebox_safety/artifacts/whitebox_safety_summary_windows.json)
- security_testing-v1 reports: [security_testing-v1/reports/final-project-report.md](security_testing-v1/reports/final-project-report.md), [security_testing-v1/reports/windows-report.md](security_testing-v1/reports/windows-report.md), [security_testing-v1/reports/wsl-report.md](security_testing-v1/reports/wsl-report.md)
- security_testing-v1 key artifacts: [security_testing-v1/mutation/logs/mutation_results_windows.csv](security_testing-v1/mutation/logs/mutation_results_windows.csv), [security_testing-v1/input_partition/udp_cases.csv](security_testing-v1/input_partition/udp_cases.csv), [security_testing-v1/performance/logs/loopback_benchmark_windows.csv](security_testing-v1/performance/logs/loopback_benchmark_windows.csv), [security_testing-v1/safety/unsafe_inventory.csv](security_testing-v1/safety/unsafe_inventory.csv)
