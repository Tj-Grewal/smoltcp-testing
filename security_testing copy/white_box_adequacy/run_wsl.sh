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
LOG_PATH="$LOG_DIR/llvm_cov_wsl.log"

rustup component add llvm-tools-preview | tee -a "$LOG_PATH"

if ! cargo llvm-cov --version >/dev/null 2>&1; then
  cargo install cargo-llvm-cov | tee -a "$LOG_PATH"
fi

cargo llvm-cov --lib --summary-only 2>&1 | tee -a "$LOG_PATH"
