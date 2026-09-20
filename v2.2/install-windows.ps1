$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$py=Get-Command py -ErrorAction SilentlyContinue
if($py){ $exe="py" } else { $exe="python" }
& $exe -m venv "$Root\.venv"
& "$Root\.venv\Scripts\python.exe" -m pip install --upgrade pip
& "$Root\.venv\Scripts\python.exe" -m pip install -r "$Root\requirements.txt"
Write-Host ""
Write-Host "miutima v2.2.0 آماده است. اجرا: .\run-windows.bat" -ForegroundColor Cyan
