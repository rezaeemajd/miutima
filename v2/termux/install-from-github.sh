#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
BASE="$HOME/miutima-v2.0.1-src"
if [ -e "$BASE" ]; then
  echo "مسیر $BASE از قبل وجود دارد؛ برای جلوگیری از حذف فایل‌های کاربر، نصب متوقف شد."
  echo "اگر این پوشه فقط کپی قبلی پروژه است، آن را بررسی و در صورت نیاز دستی حذف کنید."
  exit 1
fi
git clone --depth 1 --branch v2.0.0 https://github.com/rezaeemajd/miutima.git "$BASE"
bash "$BASE/v2/install.sh"
