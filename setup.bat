@echo off
cd /d "%~dp0"

echo ========================================
echo   Clinic Bot - Setup
echo ========================================
echo.

set "PY="
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
)
if not defined PY (
    where python >nul 2>&1 && for /f "delims=" %%p in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%p"
)

if not defined PY (
    echo [ERROR] Python not found. Install from python.org
    pause
    exit /b 1
)

echo Python: %PY%
"%PY%" --version

if not exist ".env" (
    copy /Y .env.example .env
    echo Created .env - edit BOT_TOKEN and SUPERADMIN_IDS, then run setup again.
    pause
    exit /b 1
)

if not exist "logs" mkdir logs
if not exist "data" mkdir data

echo.
echo Creating virtual environment...
if not exist ".venv" "%PY%" -m venv .venv

echo Installing packages...
call .venv\Scripts\python.exe -m pip install --upgrade pip -q
call .venv\Scripts\pip.exe install -r requirements.txt

echo.
echo ========================================
echo   Setup OK - run start.bat
echo ========================================
pause
