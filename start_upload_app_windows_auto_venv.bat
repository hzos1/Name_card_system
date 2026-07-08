@echo off
chcp 65001 >nul
setlocal

REM Move to project directory (location of this .bat file)
cd /d "%~dp0"

echo ======================================
echo Name Card Upload App (Auto venv)
echo ======================================

set "VENV_PY=.venv\Scripts\python.exe"

REM 1) Find a system Python to create venv if needed
if not exist "%VENV_PY%" (
    echo [1/5] Looking for Python 3...
    py -3 -m venv .venv >nul 2>nul
    if not exist "%VENV_PY%" python -m venv .venv >nul 2>nul
    if not exist "%VENV_PY%" python3 -m venv .venv >nul 2>nul
)

if not exist "%VENV_PY%" (
    echo.
    echo [ERROR] 找不到 Python 3。
    echo.
    call "%~dp0install_python_windows.bat"
    exit /b 1
)

REM 2) Upgrade pip (best effort)
echo [2/5] Upgrading pip...
"%VENV_PY%" -m pip install --upgrade pip

REM 3) Install dependencies
echo [3/5] Installing requirements...
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

REM 4) Start app and open browser
echo [4/5] Opening browser...
start "" "http://127.0.0.1:5000"

echo [5/5] Starting web app...
echo 請保持此視窗開啟。關閉視窗即停止系統。
echo.
"%VENV_PY%" app.py

if errorlevel 1 (
    echo.
    echo [ERROR] App exited with an error.
    pause
    exit /b 1
)

endlocal
