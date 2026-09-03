@echo off
setlocal
cd /d "%~dp0.."
where python >nul 2>nul || (echo Python was not found in PATH.& pause& exit /b 1)
python -m pip install -r requirements.txt
if errorlevel 1 (echo Dependency installation failed.& pause& exit /b 1)
python miutima.py
pause
