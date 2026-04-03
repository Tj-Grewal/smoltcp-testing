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
LOG_PATH="$LOG_DIR/fuzzing_wsl.log"

REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FUZZ_DIR="$REPO_ROOT/fuzz"

if ! cargo fuzz --help >/dev/null 2>&1; then
  echo "Installing cargo-fuzz..." | tee -a "$LOG_PATH"
  cargo install cargo-fuzz | tee -a "$LOG_PATH"
fi

echo "Ensuring nightly toolchain for sanitizer support..." | tee -a "$LOG_PATH"
rustup toolchain install nightly | tee -a "$LOG_PATH"

TARGETS=(packet_parser tcp_headers dhcp_header ieee802154_header sixlowpan_packet)

pushd "$FUZZ_DIR" >/dev/null
for t in "${TARGETS[@]}"; do
  echo "=== Fuzz target: $t ===" | tee -a "$LOG_PATH"
  output=$(cargo +nightly fuzz run "$t" -- -max_total_time=60 2>&1)
  echo "$output" | tee -a "$LOG_PATH"

  if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "Target $t exited with failure. Checking artifacts..." | tee -a "$LOG_PATH"
    ART_DIR="$FUZZ_DIR/artifacts/$t"
    if [ -d "$ART_DIR" ]; then
      for crash in "$ART_DIR"/*; do
        [ -e "$crash" ] || continue
        echo "Reproducing crash: $crash" | tee -a "$LOG_PATH"
        RUST_BACKTRACE=1 cargo +nightly fuzz run "$t" "$crash" 2>&1 | tee -a "$LOG_PATH"
      done
    fi
  fi
done
popd >/dev/null
