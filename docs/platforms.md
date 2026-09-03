# miutima v1.0.0 — Platform Guide

## Windows CMD

### Install Git and Python

Install Python 3.11+ and Git, then open **Command Prompt**.

```cmd
git clone -b v1.0.0 https://github.com/rezaeemajd/miutima.git
cd miutima
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python miutima.py
```

If you do not want a virtual environment:

```cmd
python -m pip install -r requirements.txt
python miutima.py
```

### Update dependencies

```cmd
python -m pip install --upgrade -r requirements.txt
```

## Ubuntu / Debian / WSL

Install the system packages:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv ffmpeg git
```

Clone the exact v1.0.0 snapshot:

```bash
git clone -b v1.0.0 https://github.com/rezaeemajd/miutima.git
cd miutima
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python miutima.py
```

For WSL, Windows clipboard integration is not part of v1.0.0. The later v1.1.0 branch adds clipboard support and a WSL-specific Windows PowerShell fallback.

## Android Termux

Install packages:

```bash
pkg update
pkg upgrade -y
pkg install python git ffmpeg -y
```

Clone and install:

```bash
git clone -b v1.0.0 https://github.com/rezaeemajd/miutima.git
cd miutima
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python miutima.py
```

If the virtual environment is not desired, install directly into the Termux Python environment instead.

## Internet requirements

All three platforms require working Internet access to the target service. DNS problems, firewall rules, VPN/proxy configuration, network filtering or a blocked route can prevent downloads.

## File permissions

The project creates `mp4ytd` and `mp3ytd` beside `miutima.py`. Make sure the current user can write to the repository directory.

## Clipboard

There is no clipboard feature in v1.0.0. Clipboard support belongs to v1.1.0 and later.
