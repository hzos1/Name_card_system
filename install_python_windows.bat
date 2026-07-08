@echo off
title 安裝 Python 3
if /I not "%~1"=="__run__" (
    start "Install Python" cmd /k call "%~f0" __run__
    exit /b 0
)

chcp 65001 >nul 2>&1
setlocal

echo ======================================
echo 名片系統 - 安裝 Python 3
echo ======================================
echo.
echo 你的電腦目前找不到 Python 3，所以無法啟動名片系統。
echo.
echo 請依照以下步驟安裝：
echo.
echo   1. 瀏覽器會自動打開 Python 下載頁
echo   2. 下載 Python 3.11、3.12 或 3.13（Windows installer）
echo   3. 執行安裝程式時，務必勾選：
echo      [x] Add python.exe to PATH
echo   4. 按 Install Now 完成安裝
echo   5. 關閉此視窗，重新雙擊：
echo      check_python_windows.bat
echo.
echo ======================================

start "" "https://www.python.org/downloads/windows/"

echo 按任意鍵關閉此視窗...
pause >nul
endlocal
