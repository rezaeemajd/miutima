#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
pkg update -y
pkg install -y python ffmpeg git
python -m pip install -r "$(cd "$(dirname "$0")" && pwd)/requirements.txt"
echo "miutima v2.2.0 آماده است. اجرا: bash v2.2/run-termux.sh"
