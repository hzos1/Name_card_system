@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

echo ======================================
echo 打包 Name Card System (.exe)
echo ======================================
echo.
echo 注意：必須在 Windows 電腦上執行此腳本。
echo.

set "VENV_PY=.venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
    py -3 -m venv .venv >nul 2>nul
    if not exist "%VENV_PY%" python -m venv .venv >nul 2>nul
)
if not exist "%VENV_PY%" (
    echo [ERROR] 找不到 Python 3，請先執行 install_python_windows.bat
    pause
    exit /b 1
)

echo [1/4] 安裝依賴...
"%VENV_PY%" -m pip install --upgrade pip
"%VENV_PY%" -m pip install -r requirements.txt -r requirements-build.txt
if errorlevel 1 (
    echo [ERROR] 安裝依賴失敗
    pause
    exit /b 1
)

echo [2/4] 開始打包（可能需要數分鐘）...
"%VENV_PY%" -m PyInstaller --noconfirm name_card_system.spec
if errorlevel 1 (
    echo [ERROR] 打包失敗
    pause
    exit /b 1
)

set "DIST_DIR=dist\Name_card_system"
echo [3/4] 複製資料檔到輸出資料夾...
if not exist "%DIST_DIR%\file Name_Card_system" mkdir "%DIST_DIR%\file Name_Card_system"
xcopy /E /I /Y "file Name_Card_system\*" "%DIST_DIR%\file Name_Card_system\" >nul
copy /Y "A Namecard-system-database.xlsx" "%DIST_DIR%\" >nul

echo [4/4] 完成
echo.
echo 輸出位置：
echo   %CD%\%DIST_DIR%
echo.
echo 使用方式：
echo   1. 把整個資料夾 %DIST_DIR% 複製到其他 Windows 電腦
echo   2. 雙擊 Name_card_system.exe
echo   3. 瀏覽器會自動開啟 http://127.0.0.1:5000
echo.
pause
endlocal
