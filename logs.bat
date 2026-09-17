@echo off
cd /d "%~dp0"
if not exist "logs\bot.log" (
    echo [ERROR] logs\bot.log not found.
    pause
    exit /b 1
)
powershell -NoProfile -Command "Get-Content -Path 'logs\bot.log' -Wait -Tail 50"
