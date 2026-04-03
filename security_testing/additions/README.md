# security_testing-v1 additions

This folder adds the strongest elements from security_testing-v0 to security_testing-v1 without modifying existing v1 files.

New suites:
- mutation_enhanced
- fuzzing_enhanced
- ipv4_combinatorial
- perf_microbench
- whitebox_safety_enhanced
- reports_additions

Each suite provides its own run scripts for Windows and WSL. Logs and artifacts are created on demand in suite-specific folders.

Added a new additions layer under additions that ports the best V0 pieces into V1 without touching any existing V1 files. This includes a shared runner, enhanced mutation + fuzzing scripts with JSON artifacts, standalone IPv4 combinatorial and microbench suites, white‑box coverage with lcov, and report addenda. The IPv4 `check_len` ordering fix is already present in ipv4.rs, so no code change was needed there.
- New suites and harnesses: mutation_enhanced, fuzzing_enhanced, ipv4_combinatorial, perf_microbench, whitebox_safety_enhanced
- Shared runner + structured JSON summaries: runner.py
- Report addenda templates: test-plan-addendum.md, final-report-addendum.md

Errors fixed via new additions (no existing files modified):
- Windows fuzzing sanitizers enabled (removed `-s none`) in run_fuzzing.py
- Mutation constant matching tightened to avoid invalid replacements in mutation_runner.py
- Mutation test filters use module‑level scopes to avoid narrow single‑test WSL gaps in mutation_runner.py

Run plan (additions only). Run from repo root; scripts live in additions.

Windows:
```powershell
.\security_testing-v1\additions\mutation_enhanced\run_windows.ps1
.\security_testing-v1\additions\ipv4_combinatorial\run_windows.ps1
.\security_testing-v1\additions\perf_microbench\run_windows.ps1
.\security_testing-v1\additions\fuzzing_enhanced\run_windows.ps1
.\security_testing-v1\additions\whitebox_safety_enhanced\run_windows.ps1
```

WSL:
```bash
./security_testing-v1/additions/mutation_enhanced/run_wsl.sh
./security_testing-v1/additions/ipv4_combinatorial/run_wsl.sh
./security_testing-v1/additions/perf_microbench/run_wsl.sh
./security_testing-v1/additions/fuzzing_enhanced/run_wsl.sh
./security_testing-v1/additions/whitebox_safety_enhanced/run_wsl.sh
```

Optional (still additions only): include static checks in white‑box run
```bash
python3 security_testing-v1/additions/whitebox_safety_enhanced/scripts/run_whitebox_safety.py --platform wsl --include-static
```
```powershell
python security_testing-v1\additions\whitebox_safety_enhanced\scripts\run_whitebox_safety.py --platform windows --include-static
```
