@echo off
setlocal

REM Move to project directory (location of this .bat file)
cd /d "%~dp0"

echo ======================================
echo Name Card Upload App (Auto venv)
echo ======================================

REM 1) Ensure Python launcher exists
where py >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Cannot find Python launcher "py".
    echo Please install Python 3 first and enable "Add python.exe to PATH".
    pause
    exit /b 1
)

REM 2) Create .venv automatically if missing
if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Creating virtual environment...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create .venv
        pause
        exit /b 1
    )
)

REM 3) Upgrade pip (best effort)
echo [2/4] Upgrading pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip

REM 4) Install dependencies
echo [3/4] Installing requirements...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

REM 5) Start app and open browser
echo [4/4] Starting web app...
start "" "http://127.0.0.1:5000"
".venv\Scripts\python.exe" app.py

if errorlevel 1 (
    echo.
    echo [ERROR] App exited with an error.
    pause
    exit /b 1
)

endlocal
