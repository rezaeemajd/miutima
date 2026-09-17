#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
BASE="$HOME/miutima-v2-src"
rm -rf "$BASE"
git clone --depth 1 --branch v2.0.0 https://github.com/rezaeemajd/miutima.git "$BASE"
bash "$BASE/v2/install.sh"
