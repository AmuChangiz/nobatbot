@echo off
cd /d "%~dp0\.."

echo.
echo ========================================
echo   WARNING - Factory Reset
echo ========================================
echo.
echo Deletes ALL database data and logs.
echo Only .env file stays on disk.
echo.
set /p CONFIRM=Type RESET to confirm: 
if /I not "%CONFIRM%"=="RESET" (
    echo Cancelled.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Run setup.bat first.
    pause
    exit /b 1
)

echo.
echo Stopping bot...
call stop.bat >nul 2>&1

echo Resetting...
set PYTHONPATH=%CD%
call .venv\Scripts\python.exe scripts\reset_clinic_data.py
if errorlevel 1 (
    echo [ERROR] Reset failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Reset complete
echo ========================================
echo Edit .env then run start.bat
echo.
pause
