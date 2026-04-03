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

python3 "$SCRIPT_DIR/scripts/run_fuzzing.py" --platform wsl |
  tee "$LOG_DIR/fuzzing_stdout_wsl.log"
