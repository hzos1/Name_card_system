@echo off
title 安裝 Python 3
if /I not "%~1"=="__run__" (
    start "Install Python" cmd /k call "%~f0" __run__
    exit /b 0
)

chcp 65001 >nul 2>&1
setlocal EnableExtensions

echo ======================================
echo 名片系統 - 安裝 Python 3
echo ======================================
echo.
echo 注意：此腳本不會自動安裝 Python，
echo 只會提供安裝方法。請選擇其中一種：
echo.
echo --------------------------------------
echo 方法 A（推薦）：官網下載安裝
echo --------------------------------------
echo   1. 打開 https://www.python.org/downloads/windows/
echo   2. 下載 Python 3.12 或 3.13
echo   3. 執行安裝程式
echo   4. 務必勾選 [x] Add python.exe to PATH
echo   5. 按 Install Now
echo.
echo --------------------------------------
echo 方法 B：用 winget 安裝（Windows 11）
echo --------------------------------------
echo   在 cmd 輸入：
echo   winget install Python.Python.3.12
echo.
echo --------------------------------------
echo 安裝完成後
echo --------------------------------------
echo   1. 關閉所有 cmd 視窗
echo   2. 雙擊 check_python_windows.bat 確認
echo   3. 雙擊 setup_venv_windows.bat 建立 .venv
echo   4. 雙擊 啟動名片系統_Windows.bat
echo.
echo ======================================
echo.

set /p OPEN_WEB=是否現在打開 Python 下載頁？(Y/N): 
if /I "%OPEN_WEB%"=="Y" start "" "https://www.python.org/downloads/windows/"

set /p RUN_WINGET=是否嘗試用 winget 安裝 Python 3.12？(Y/N): 
if /I "%RUN_WINGET%"=="Y" (
    winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements
)

echo.
echo 按任意鍵關閉此視窗...
pause >nul
endlocal
