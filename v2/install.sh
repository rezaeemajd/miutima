#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

APP="$HOME/.miutima-v2"
SRC="$(cd "$(dirname "$0")" && pwd)"
SHORTCUTS="$HOME/.shortcuts"
PID="$APP/miutima.pid"

printf '\n=== miutima v2.1.0 — Termux installer ===\n'
printf 'این نصب نسخه‌های قبلی miutima را حذف یا تغییر نمی‌دهد.\n\n'

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
APP="$HOME/.miutima-v2"; PID="$APP/miutima.pid"; URL="http://127.0.0.1:8765"
mkdir -p "$APP"
is_our_server(){ [ -f "$PID" ] || return 1; local p; p="$(cat "$PID" 2>/dev/null || true)"; [ -n "$p" ] || return 1; kill -0 "$p" 2>/dev/null || return 1; tr '\0' ' ' < "/proc/$p/cmdline" 2>/dev/null | grep -Fq "$APP/app.py"; }
if is_our_server; then termux-open-url "$URL"; exit 0; fi
rm -f "$PID"
nohup "$APP/.venv/bin/python" "$APP/app.py" > "$APP/server.log" 2>&1 &
echo $! > "$PID"
sleep 1
if ! is_our_server; then echo "miutima failed to start. Log: $APP/server.log"; tail -n 40 "$APP/server.log" 2>/dev/null || true; rm -f "$PID"; exit 1; fi
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

cat > "$SHORTCUTS/miutima-v2-status.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
APP="$HOME/.miutima-v2"; PID="$APP/miutima.pid"
echo "=== miutima v2.1.0 status ==="
if [ -f "$PID" ] && kill -0 "$(cat "$PID")" 2>/dev/null; then
  ps -p "$(cat "$PID")" -o pid,ppid,user,args
else
  echo "Server: STOPPED"
fi
echo
echo "API:"
curl -s --max-time 3 http://127.0.0.1:8765/api/storage 2>/dev/null || echo "API unavailable"
echo
echo "App: $APP"
EOF
chmod +x "$SHORTCUTS"/miutima-v2*.sh

printf '\n✓ نصب miutima v2.1.0 کامل شد.\n✓ پخش‌کننده داخلی MP4/MP3 و نمایش فایل اضافه شد.\n✓ افکت پردازش/انتقال و افکت موفقیت اضافه شد.\n✓ ویجت‌های Termux:Widget ساخته/به‌روزرسانی شدند.\n✓ محل ذخیره اصلی: ~/storage/downloads/miutima-v2\n✓ محل جایگزین امن: ~/.miutima-v2/downloads\n✓ آدرس: http://127.0.0.1:8765\n'
