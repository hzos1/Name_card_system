@echo off
chcp 65001 >nul
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
echo   2. 下載 Python 3.11 或 3.12（Windows installer）
echo   3. 執行安裝程式時，務必勾選：
echo      [x] Add python.exe to PATH
echo   4. 按 Install Now 完成安裝
echo   5. 關閉此視窗，重新雙擊：
echo      start_upload_app_windows_auto_venv.bat
echo.
echo ======================================

start "" "https://www.python.org/downloads/windows/"

pause
endlocal
