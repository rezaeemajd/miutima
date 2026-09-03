#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
command -v python3 >/dev/null || { echo "Python 3 not found."; exit 1; }
python3 -m pip install -r requirements.txt
exec python3 miutima.py
