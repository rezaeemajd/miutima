#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

APP="$HOME/.miutima-v2"
SRC="$(cd "$(dirname "$0")" && pwd)"
SHORTCUTS="$HOME/.shortcuts"

printf '\n=== miutima v2.0.0 — Termux installer ===\n'
printf 'نسخه‌های قبلی miutima حذف یا تغییر داده نمی‌شوند.\n\n'

pkg install -y python git ffmpeg termux-api
termux-setup-storage || true

# Do not fail the installation because Android shared-storage permission is unavailable.
# The application now automatically falls back to ~/.miutima-v2/downloads.
mkdir -p "$APP" "$SHORTCUTS" "$APP/downloads"
cp -a "$SRC/app.py" "$SRC/requirements.txt" "$SRC/web" "$APP/"
python -m venv "$APP/.venv"
"$APP/.venv/bin/python" -m pip install --upgrade pip
"$APP/.venv/bin/python" -m pip install -r "$APP/requirements.txt"

cat > "$SHORTCUTS/miutima-v2.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
set -u
APP="$HOME/.miutima-v2"
PID="$APP/miutima.pid"
URL="http://127.0.0.1:8765"
mkdir -p "$APP"
if [ -f "$PID" ] && kill -0 "$(cat "$PID")" 2>/dev/null; then
  termux-open-url "$URL"
  exit 0
fi
nohup "$APP/.venv/bin/python" "$APP/app.py" > "$APP/server.log" 2>&1 &
echo $! > "$PID"
sleep 1
if ! kill -0 "$(cat "$PID")" 2>/dev/null; then
  echo "miutima failed to start. Log: $APP/server.log"
  tail -n 30 "$APP/server.log" 2>/dev/null || true
  rm -f "$PID"
  exit 1
fi
termux-open-url "$URL"
EOF

cat > "$SHORTCUTS/miutima-v2-stop.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
APP="$HOME/.miutima-v2"; PID="$APP/miutima.pid"
if [ -f "$PID" ]; then kill "$(cat "$PID")" 2>/dev/null || true; rm -f "$PID"; fi
pkill -f "$APP/app.py" 2>/dev/null || true
echo "miutima v2 stopped."
EOF

cat > "$SHORTCUTS/miutima-v2-open.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
termux-open-url "http://127.0.0.1:8765"
EOF
chmod +x "$SHORTCUTS"/miutima-v2*.sh

printf '\n✓ نصب کامل شد.\n✓ ویجت‌های Termux:Widget ساخته شدند.\n✓ محل ذخیره اصلی: ~/storage/downloads/miutima-v2 در صورت داشتن دسترسی\n✓ محل جایگزین امن: ~/.miutima-v2/downloads\n✓ کلیپ‌بورد: ابتدا Clipboard مرورگر، سپس Termux:API\n✓ اجرا: از ویجت miutima v2 را بزنید.\n✓ آدرس: http://127.0.0.1:8765\n'
