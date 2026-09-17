#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

APP="$HOME/.miutima-v2"
SRC="$(cd "$(dirname "$0")" && pwd)"
SHORTCUTS="$HOME/.shortcuts"

printf '\n=== miutima v2.0.0 — Termux installer ===\n'
printf 'نسخه‌های قبلی miutima حذف یا تغییر داده نمی‌شوند.\n\n'

pkg install -y python git ffmpeg termux-api
termux-setup-storage || true

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

is_miutima_running() {
  local p="${1:-}"
  [ -n "$p" ] || return 1
  kill -0 "$p" 2>/dev/null || return 1
  [ -r "/proc/$p/cmdline" ] || return 1
  tr '\0' ' ' < "/proc/$p/cmdline" 2>/dev/null | grep -Fq "$APP/app.py"
}

if [ -f "$PID" ]; then
  saved_pid="$(cat "$PID" 2>/dev/null || true)"
  if is_miutima_running "$saved_pid"; then
    termux-open-url "$URL"
    exit 0
  fi
  rm -f "$PID"
fi

nohup "$APP/.venv/bin/python" "$APP/app.py" >> "$APP/server.log" 2>&1 &
echo $! > "$PID"
sleep 1

if ! is_miutima_running "$(cat "$PID" 2>/dev/null || true)"; then
  echo "miutima failed to start. Log: $APP/server.log"
  tail -n 30 "$APP/server.log" 2>/dev/null || true
  rm -f "$PID"
  exit 1
fi

termux-open-url "$URL"
EOF

cat > "$SHORTCUTS/miutima-v2-stop.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
set -u
APP="$HOME/.miutima-v2"
PID="$APP/miutima.pid"
if [ -f "$PID" ]; then
  p="$(cat "$PID" 2>/dev/null || true)"
  if [ -n "$p" ]; then kill "$p" 2>/dev/null || true; fi
fi
sleep 1
pkill -f "$APP/app.py" 2>/dev/null || true
rm -f "$PID"
echo "✓ miutima v2 متوقف شد."
EOF

cat > "$SHORTCUTS/miutima-v2-status.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
set -u
APP="$HOME/.miutima-v2"
PID="$APP/miutima.pid"
if [ ! -f "$PID" ]; then
  echo "miutima v2: متوقف است (PID file وجود ندارد)."
  exit 0
fi
p="$(cat "$PID" 2>/dev/null || true)"
if [ -z "$p" ] || ! kill -0 "$p" 2>/dev/null || [ ! -r "/proc/$p/cmdline" ] || ! tr '\0' ' ' < "/proc/$p/cmdline" 2>/dev/null | grep -Fq "$APP/app.py"; then
  echo "miutima v2: متوقف است (PID file قدیمی است)."
  rm -f "$PID"
  exit 0
fi
ps -p "$p" -o pid,ppid,user,args
printf '\nAPI: '
curl -s --max-time 3 "$URL/api/storage" 2>/dev/null || echo "در دسترس نیست"
EOF

cat > "$SHORTCUTS/miutima-v2-open.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
termux-open-url "http://127.0.0.1:8765"
EOF
chmod +x "$SHORTCUTS"/miutima-v2*.sh

printf '\n✓ نصب کامل شد.\n✓ ویجت‌های Termux:Widget ساخته شدند.\n✓ محل ذخیره اصلی: ~/storage/downloads/miutima-v2 در صورت داشتن دسترسی\n✓ محل جایگزین امن: ~/.miutima-v2/downloads\n✓ کلیپ‌بورد: ابتدا Clipboard مرورگر، سپس Termux:API\n✓ وضعیت: ویجت miutima v2 status\n✓ اجرا: از ویجت miutima v2 را بزنید.\n✓ آدرس: http://127.0.0.1:8765\n'
