@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PY=%~dp0.venv\Scripts\python.exe"
) else (
    where py >nul 2>nul
    if %errorlevel%==0 (
        set "PY=py"
    ) else (
        set "PY=python"
    )
)

if exist ".venv\Scripts\python.exe" (
    "%PY%" -m pip install -r requirements-desktop.txt
    "%PY%" app.py
) else (
    %PY% -m pip install -r requirements-desktop.txt
    %PY% app.py
)
