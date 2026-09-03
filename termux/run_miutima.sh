#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")/.."
pkg install python ffmpeg termux-api git -y
python -m pip install -r requirements.txt
exec python miutima.py
