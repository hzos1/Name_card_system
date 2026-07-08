@echo off
setlocal

REM Move to project directory (location of this .bat file)
cd /d "%~dp0"

echo ======================================
echo Name Card Upload App (Windows)
echo ======================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Cannot find Python virtual environment: .venv\Scripts\python.exe
    echo Please create venv first, e.g.:
    echo   py -3 -m venv .venv
    echo   .venv\Scripts\python -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo [1/2] Installing required packages...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo [2/2] Starting web app...
start "" "http://127.0.0.1:5000"
".venv\Scripts\python.exe" app.py

if errorlevel 1 (
    echo.
    echo [ERROR] App exited with an error.
    pause
    exit /b 1
)

endlocal
