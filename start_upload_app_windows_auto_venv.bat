@echo off
title 名片系統 WebApp
if /I not "%~1"=="__run__" (
    start "Name Card System" cmd /k call "%~f0" __run__
    exit /b 0
)

setlocal EnableExtensions
chcp 65001 >nul 2>&1

set "ROOT=%~dp0"
cd /d "%ROOT%" || goto :fail_cd

echo ======================================
echo Name Card Upload App (Auto venv)
echo ======================================
echo 專案資料夾：
echo   "%ROOT%"
echo.

set "VENV_PY=%ROOT%.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo [1/5] Looking for Python 3...
    py -3 -m venv "%ROOT%.venv" 2>nul
    if not exist "%VENV_PY%" python -m venv "%ROOT%.venv" 2>nul
    if not exist "%VENV_PY%" python3 -m venv "%ROOT%.venv" 2>nul
)

if not exist "%VENV_PY%" (
    echo.
    echo [ERROR] 找不到 Python 3。
    echo 請先雙擊 install_python_windows.bat
    echo.
    goto :fail
)

echo [2/5] Upgrading pip...
"%VENV_PY%" -m pip install --upgrade pip

echo [3/5] Installing requirements...
"%VENV_PY%" -m pip install -r "%ROOT%requirements.txt"
if errorlevel 1 goto :fail

echo [4/5] Opening browser...
start "" "http://127.0.0.1:5000"

echo [5/5] Starting web app...
echo 請保持此視窗開啟。關閉視窗即停止系統。
echo.
"%VENV_PY%" "%ROOT%app.py"
if errorlevel 1 goto :fail
goto :done

:fail_cd
echo [ERROR] 無法進入資料夾：
echo   "%ROOT%"
echo 建議移到 C:\Name_card_system 後再試。
goto :done

:fail
echo.
echo [ERROR] 啟動失敗。
goto :done

:done
echo.
echo 按任意鍵關閉此視窗...
pause >nul
endlocal
exit /b 0
