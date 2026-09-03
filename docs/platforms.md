# miutima v1.1.0 — Platform Guide

This guide covers Windows CMD, Ubuntu/Debian Linux, WSL and Android Termux.

## 1. Common requirements

- Python 3.11 or newer
- Git
- Internet access
- FFmpeg recommended
- Packages in `requirements.txt`

Check:

```bash
python --version
ffmpeg -version
```

## 2. Windows CMD

Install Python 3.11+ and Git. Open **Command Prompt**.

```cmd
git clone -b v1.1.0 https://github.com/rezaeemajd/miutima.git
cd miutima
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python miutima.py
```

### Windows clipboard

1. Copy a YouTube URL with `Ctrl+C`.
2. Run miutima.
3. Select `2 - Clipboard`.

miutima uses PowerShell `Get-Clipboard`. No Python clipboard module is required.

Test independently:

```cmd
powershell -NoProfile -NonInteractive -Command "Get-Clipboard -Raw"
```

If that command prints the copied URL, miutima can read it too.

## 3. Ubuntu / Debian Linux

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git ffmpeg

git clone -b v1.1.0 https://github.com/rezaeemajd/miutima.git
cd miutima
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python miutima.py
```

### Linux clipboard — Wayland

```bash
sudo apt install -y wl-clipboard
wl-paste --no-newline
```

### Linux clipboard — X11

```bash
sudo apt install -y xclip
xclip -selection clipboard -o
```

Alternative:

```bash
sudo apt install -y xsel
xsel --clipboard --output
```

miutima checks Wayland first, then X11 tools.

## 4. WSL / Ubuntu on Windows

WSL uses the Linux code path but can read the Windows clipboard through Windows PowerShell.

### WSL clipboard

Copy text in Windows and run:

```bash
command -v powershell.exe
powershell.exe -NoProfile -NonInteractive -Command 'Get-Clipboard -Raw'
```

The second command should print the Windows clipboard.

v1.1.0 detects WSL and tries:

1. `powershell.exe`
2. `pwsh.exe`
3. Linux `wl-paste`
4. Linux `xclip`
5. Linux `xsel`

If `powershell.exe` is not found, check Windows interop:

```bash
ls -l /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
```

Do not install a Python clipboard package just to solve WSL clipboard access; the application is designed to use the Windows command directly.

## 5. WSL search / connection refused

If Search YouTube reports:

```text
Unable to download API page
Failed to establish a new connection
[Errno 111] Connection refused
```

v1.1.0 retries extraction without using a proxy after the normal attempt. If both attempts fail, inspect the WSL network.

Test Internet:

```bash
curl -I https://www.youtube.com
```

Test DNS:

```bash
getent hosts www.youtube.com
```

Check proxy variables:

```bash
env | grep -i proxy
```

If you find a dead local proxy, for example `127.0.0.1:<port>`, temporarily test without it:

```bash
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
curl -I https://www.youtube.com
```

If direct access works after unsetting the proxy, fix the proxy configuration in your shell startup files instead of changing miutima.

## 6. Android Termux

```bash
pkg update
pkg upgrade -y
pkg install python git ffmpeg termux-api -y

git clone -b v1.1.0 https://github.com/rezaeemajd/miutima.git
cd miutima
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python miutima.py
```

### Termux clipboard

Install the Termux package:

```bash
pkg install termux-api -y
```

Also install the **Termux:API companion Android application** that matches your Termux setup.

Test:

```bash
termux-clipboard-get
```

Copy a URL in Android first. The command must print the copied text. Then choose `2 - Clipboard` in miutima.

If the command is not found:

```bash
pkg install termux-api -y
```

If the command exists but returns empty output, check the Termux:API companion app and Android permissions.

## 7. Launchers

Windows CMD:

```cmd
windows\run_miutima.bat
```

Linux:

```bash
bash linux/run_miutima.sh
```

Termux:

```bash
bash termux/run_miutima.sh
```

Using `bash` avoids needing executable-bit changes after cloning.

## 8. Output and local data

```text
miutima/
├── mp4ytd/
└── mp3ytd/
```

Settings:

```text
~/.config/miutima/config.json
```

History:

```text
~/.config/miutima/history.json
```

## 9. Verification

```bash
python -m py_compile miutima.py
python -m pip show yt-dlp rich imageio-ffmpeg
ffmpeg -version
```

## 10. Updating

```bash
git checkout v1.1.0
git pull origin v1.1.0
python -m pip install --upgrade -r requirements.txt
```
