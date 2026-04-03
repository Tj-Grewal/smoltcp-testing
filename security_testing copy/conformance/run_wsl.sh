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

pushd "$SCRIPT_DIR/conformance_suite" >/dev/null
cargo test | tee "$LOG_DIR/conformance_wsl.log"
popd >/dev/null
