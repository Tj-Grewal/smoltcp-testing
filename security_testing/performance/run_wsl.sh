#!/usr/bin/env bash
set -euo pipefail
if [ -f "$HOME/.cargo/env" ]; then
  source "$HOME/.cargo/env"
else
  export PATH="$HOME/.cargo/bin:$PATH"
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

RUNS=5
LOG_PATH="$LOG_DIR/loopback_benchmark_wsl.log"
CSV_PATH="$LOG_DIR/loopback_benchmark_wsl.csv"

printf "run,duration_s,bandwidth_gbps\n" > "$CSV_PATH"

pushd "$SCRIPT_DIR/loopback_perf_suite" >/dev/null
for i in $(seq 1 $RUNS); do
  echo "=== Run $i ===" >> "$LOG_PATH"
  output=$(cargo run --release 2>&1)
  echo "$output" >> "$LOG_PATH"

  duration=$(echo "$output" | sed -n 's/.*duration_s=\([0-9.]*\) bandwidth_gbps=\([0-9.]*\).*/\1/p' | tail -n 1)
  bandwidth=$(echo "$output" | sed -n 's/.*duration_s=\([0-9.]*\) bandwidth_gbps=\([0-9.]*\).*/\2/p' | tail -n 1)

  printf "%s,%s,%s\n" "$i" "$duration" "$bandwidth" >> "$CSV_PATH"
done
popd >/dev/null
