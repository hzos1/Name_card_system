@echo off
title 打包名片系統 EXE
if /I not "%~1"=="__run__" (
    start "Build Name Card EXE" cmd /k call "%~f0" __run__
    exit /b 0
)

setlocal EnableExtensions
chcp 65001 >nul 2>&1

set "ROOT=%~dp0"
cd /d "%ROOT%" || goto :fail_cd

set "LOG=%ROOT%build_log.txt"
set "VENV_PY=%ROOT%.venv\Scripts\python.exe"

echo ====================================== > "%LOG%"
echo Build started: %DATE% %TIME% >> "%LOG%"
echo Project folder: %ROOT% >> "%LOG%"
echo ====================================== >> "%LOG%"

echo ======================================
echo 打包 Name Card System (.exe)
echo ======================================
echo.
echo 專案資料夾：
echo   %ROOT%
echo.
echo 日誌檔案：
echo   %LOG%
echo.

if not exist "%ROOT%app.py" (
    echo [ERROR] 找不到 app.py
    echo 請確認你是在 Name_card_system 專案資料夾內執行。
    echo [ERROR] app.py not found >> "%LOG%"
    goto :fail
)

if not exist "%VENV_PY%" (
    echo [1/5] 建立虛擬環境 .venv ...
    echo [1/5] create venv >> "%LOG%"
    py -3 -m venv "%ROOT%.venv" >> "%LOG%" 2>&1
)
if not exist "%VENV_PY%" (
    python -m venv "%ROOT%.venv" >> "%LOG%" 2>&1
)
if not exist "%VENV_PY%" (
    echo.
    echo [ERROR] 無法建立 .venv
    echo 請先執行 check_python_windows.bat 檢查 Python。
    echo.
    echo 常見原因：
    echo   1. 未安裝 Python 3
    echo   2. 安裝時未勾選 Add python.exe to PATH
    echo   3. 資料夾路徑含特殊字元，建議移到例如 C:\Name_card_system
    goto :fail
)

echo [2/5] 檢查 Python 版本...
"%VENV_PY%" --version
"%VENV_PY%" --version >> "%LOG%" 2>&1

echo [3/5] 安裝依賴（可能需要幾分鐘）...
"%VENV_PY%" -m pip install --upgrade pip >> "%LOG%" 2>&1
if errorlevel 1 goto :fail_pip
"%VENV_PY%" -m pip install -r "%ROOT%requirements.txt" -r "%ROOT%requirements-build.txt" >> "%LOG%" 2>&1
if errorlevel 1 goto :fail_pip

echo [4/5] 開始打包（可能需要數分鐘）...
"%VENV_PY%" -m PyInstaller --noconfirm "%ROOT%name_card_system.spec" >> "%LOG%" 2>&1
if errorlevel 1 goto :fail_build

set "DIST_DIR=%ROOT%dist\Name_card_system"
echo [5/5] 複製資料檔...
if not exist "%DIST_DIR%\file Name_Card_system" mkdir "%DIST_DIR%\file Name_Card_system"
if exist "%ROOT%file Name_Card_system\*" (
    xcopy /E /I /Y "%ROOT%file Name_Card_system\*" "%DIST_DIR%\file Name_Card_system\" >> "%LOG%" 2>&1
)
if exist "%ROOT%A Namecard-system-database.xlsx" (
    copy /Y "%ROOT%A Namecard-system-database.xlsx" "%DIST_DIR%\" >> "%LOG%" 2>&1
)

echo.
echo ======================================
echo 完成！
echo ======================================
echo 輸出位置：
echo   %DIST_DIR%
echo.
echo 使用方式：
echo   1. 複製整個 dist\Name_card_system 資料夾到其他 Windows 電腦
echo   2. 雙擊 Name_card_system.exe
echo.
goto :done

:fail_cd
echo [ERROR] 無法進入資料夾：%ROOT%
pause
exit /b 1

:fail_pip
echo.
echo [ERROR] 安裝依賴失敗
echo 請打開 build_log.txt 查看詳細錯誤。
echo.
echo 若你使用 Python 3.13，可改裝 Python 3.12 後再試。
goto :fail

:fail_build
echo.
echo [ERROR] 打包失敗
echo 請打開 build_log.txt 查看詳細錯誤。
goto :fail

:fail
echo.
echo 按任意鍵關閉此視窗...
pause >nul
exit /b 1

:done
echo 按任意鍵關閉此視窗...
pause >nul
exit /b 0
