#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
python3 -m venv "$ROOT/.venv" 2>/dev/null || true
if [ -x "$ROOT/.venv/bin/python" ]; then "$ROOT/.venv/bin/python" -m pip install -r "$ROOT/requirements-desktop.txt"; else python3 -m pip install --user -r "$ROOT/requirements.txt"; fi
printf '\nmiutima v2.2.0 آماده است. اجرا: %s/run-linux.sh\n' "$ROOT"
