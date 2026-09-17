@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Run setup.bat first.
    pause
    exit /b 1
)

if not exist ".env" (
    echo [ERROR] .env file not found.
    pause
    exit /b 1
)

if not exist "logs" mkdir logs
if not exist "data" mkdir data

powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -like '*bale_bot.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"

echo Bot starting... Press Ctrl+C to stop.
call .venv\Scripts\python.exe bale_bot.py
pause
