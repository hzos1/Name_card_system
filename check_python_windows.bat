@echo off
title 檢查 Python 環境
if /I not "%~1"=="__run__" (
    start "Check Python" cmd /k call "%~f0" __run__
    exit /b 0
)

setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul 2>&1

set "ROOT=%~dp0"
cd /d "%ROOT%" || goto :fail_cd

set "LOG=%ROOT%check_log.txt"
echo Check started: %DATE% %TIME% > "%LOG%"
echo Project folder: "%ROOT%" >> "%LOG%"

echo ======================================
echo 檢查 Python 與打包環境
echo ======================================
echo 專案資料夾：
echo   "%ROOT%"
echo.

set "FOUND=0"
set "PYTHON_CMD="

echo [1] 檢查系統是否已安裝 Python...
echo.

where py >nul 2>nul
if not errorlevel 1 (
    echo   [OK] 找到 py 啟動器
    py -3 --version 2>nul
    if not errorlevel 1 (
        set "FOUND=1"
        set "PYTHON_CMD=py -3"
        echo   [OK] py -3 可用
        py -3 --version >> "%LOG%" 2>&1
    ) else (
        echo   [--] py -3 不可用
    )
) else (
    echo   [--] 找不到 py
)

where python >nul 2>nul
if not errorlevel 1 (
    echo   [OK] 找到 python
    python --version 2>nul
    if not errorlevel 1 (
        if "!FOUND!"=="0" (
            set "FOUND=1"
            set "PYTHON_CMD=python"
        )
        python --version >> "%LOG%" 2>&1
    )
) else (
    echo   [--] 找不到 python
)

where python3 >nul 2>nul
if not errorlevel 1 (
    echo   [OK] 找到 python3
    python3 --version 2>nul
) else (
    echo   [--] 找不到 python3
)

echo.
if "!FOUND!"=="0" (
    echo [結果] 未安裝 Python 3
    echo.
    echo 你目前無法打包 .exe，也無法直接啟動系統。
    echo 請先雙擊：install_python_windows.bat
    echo.
    echo 安裝時務必勾選：Add python.exe to PATH
    echo 安裝完成後，關閉並重新開啟命令提示字元，再執行此檢查。
    echo.
    goto :done
)

echo [結果] 已安裝 Python 3
echo 建議使用：!PYTHON_CMD!
echo.

echo [2] 檢查專案虛擬環境 .venv ...
if exist "%ROOT%.venv\Scripts\python.exe" (
    echo   [OK] 找到 .venv\Scripts\python.exe
    "%ROOT%.venv\Scripts\python.exe" --version
) else (
    echo   [--] 尚未建立 .venv
    echo   這是正常的，第一次啟動或打包時會自動建立。
)
echo.

echo [3] 檢查 pip ...
if exist "%ROOT%.venv\Scripts\python.exe" (
    "%ROOT%.venv\Scripts\python.exe" -m pip --version >nul 2>nul
    if errorlevel 1 (
        echo   [--] pip 不可用
    ) else (
        "%ROOT%.venv\Scripts\python.exe" -m pip --version
        echo   [OK] pip 可用
    )
) else if "!PYTHON_CMD!"=="py -3" (
    py -3 -m pip --version >nul 2>nul
    if errorlevel 1 (
        echo   [--] pip 不可用
    ) else (
        py -3 -m pip --version
        echo   [OK] pip 可用
    )
) else (
    "!PYTHON_CMD!" -m pip --version >nul 2>nul
    if errorlevel 1 (
        echo   [--] pip 不可用
    ) else (
        "!PYTHON_CMD!" -m pip --version
        echo   [OK] pip 可用
    )
)
echo.

echo [4] 檢查 PyInstaller（打包 .exe 需要）...
if exist "%ROOT%.venv\Scripts\python.exe" (
    "%ROOT%.venv\Scripts\python.exe" -m PyInstaller --version >nul 2>nul
    if errorlevel 1 (
        echo   [--] 尚未安裝 PyInstaller
        echo   執行 build_windows_exe.bat 時會自動安裝
    ) else (
        "%ROOT%.venv\Scripts\python.exe" -m PyInstaller --version
        echo   [OK] PyInstaller 已安裝
    )
) else (
    echo   [--] 需先建立 .venv 後才能檢查 PyInstaller
)
echo.

echo ======================================
echo 檢查完成
echo ======================================
echo.
echo 日誌檔案："%LOG%"
echo.
echo 若 [1] 顯示已安裝 Python（例如 3.13.14）：
echo   - 啟動系統：雙擊 啟動名片系統_Windows.bat
echo   - 打包 exe：雙擊 build_windows_exe.bat
echo.
echo 若 [1] 顯示未安裝：
echo   - 先雙擊 install_python_windows.bat
echo.
echo 若仍然閃退，請把專案移到簡單路徑，例如：
echo   C:\Name_card_system
echo.
goto :done

:fail_cd
echo [ERROR] 無法進入資料夾：
echo   "%ROOT%"
echo.
echo 建議把專案移到 C:\Name_card_system 後再試。
goto :done

:done
echo 按任意鍵關閉此視窗...
pause >nul
endlocal
exit /b 0
