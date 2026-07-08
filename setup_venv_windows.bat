@echo off
title 建立 .venv 虛擬環境
if /I not "%~1"=="__run__" (
    start "Setup venv" cmd /k call "%~f0" __run__
    exit /b 0
)

setlocal EnableExtensions
chcp 65001 >nul 2>&1

set "ROOT=%~dp0"
cd /d "%ROOT%" || goto :fail_cd

set "LOG=%ROOT%setup_venv_log.txt"
set "VENV_PY=%ROOT%.venv\Scripts\python.exe"

echo Setup started: %DATE% %TIME% > "%LOG%"
echo Project folder: "%ROOT%" >> "%LOG%"

echo ======================================
echo 建立 .venv 虛擬環境
echo ======================================
echo 專案資料夾：
echo   "%ROOT%"
echo 日誌檔案：
echo   "%LOG%"
echo.

echo [1/4] 檢查 Python 3...
set "PY_CMD="
py -3 --version >> "%LOG%" 2>&1
if not errorlevel 1 set "PY_CMD=py -3"
if not defined PY_CMD (
    python --version >> "%LOG%" 2>&1
    if not errorlevel 1 set "PY_CMD=python"
)
if not defined PY_CMD (
    python3 --version >> "%LOG%" 2>&1
    if not errorlevel 1 set "PY_CMD=python3"
)
if not defined PY_CMD goto :no_python

echo 使用：%PY_CMD%
%PY_CMD% --version

if exist "%VENV_PY%" (
    echo.
    echo [2/4] 已存在 .venv，將重新安裝套件...
) else (
    echo.
    echo [2/4] 建立 .venv ...
    %PY_CMD% -m venv "%ROOT%.venv" >> "%LOG%" 2>&1
)

if not exist "%VENV_PY%" (
    echo [ERROR] 無法建立 .venv >> "%LOG%"
    echo [ERROR] 無法建立 .venv
    goto :fail
)

echo [3/4] 安裝 pip 與 requirements...
"%VENV_PY%" -m pip install --upgrade pip >> "%LOG%" 2>&1
if errorlevel 1 goto :fail_pip
"%VENV_PY%" -m pip install -r "%ROOT%requirements.txt" >> "%LOG%" 2>&1
if errorlevel 1 goto :fail_pip

echo [4/4] 完成
echo.
echo .venv 已建立成功：
echo   "%ROOT%.venv"
echo.
echo 下一步：
echo   雙擊 啟動名片系統_Windows.bat
echo   或執行：
echo   "%VENV_PY%" "%ROOT%app.py"
echo.
goto :done

:no_python
echo [ERROR] 找不到 Python 3
echo.
echo 請先手動安裝 Python：
echo   1. 開啟 https://www.python.org/downloads/windows/
echo   2. 下載 Python 3.12 或 3.13
echo   3. 安裝時勾選 Add python.exe to PATH
echo   4. 關閉此視窗，重新執行本腳本
echo.
echo 也可嘗試在 cmd 執行（需網路）：
echo   winget install Python.Python.3.12
echo.
goto :done

:fail_cd
echo [ERROR] 無法進入資料夾：
echo   "%ROOT%"
echo 建議移到 C:\Name_card_system
goto :done

:fail_pip
echo [ERROR] 安裝套件失敗
echo 請打開 setup_venv_log.txt 查看錯誤
echo.
echo 若使用 Python 3.13 失敗，可改裝 Python 3.12 後刪除 .venv 再試
goto :done

:fail
echo [ERROR] 建立 .venv 失敗
echo 請打開 setup_venv_log.txt 查看錯誤
goto :done

:done
echo.
echo 按任意鍵關閉此視窗...
pause >nul
endlocal
exit /b 0
