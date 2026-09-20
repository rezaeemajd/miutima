#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
pkg install -y python ffmpeg git >/dev/null 2>&1 || true
python -m pip install -r requirements.txt
exec python app.py
