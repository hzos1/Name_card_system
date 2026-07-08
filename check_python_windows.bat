@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo ======================================
echo 檢查 Python 與打包環境
echo ======================================
echo 專案資料夾：%ROOT%
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
    pause
    exit /b 1
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
    set "CHECK_PY=%ROOT%.venv\Scripts\python.exe"
    "!CHECK_PY!" -m pip --version >nul 2>nul
    if errorlevel 1 (
        echo   [--] pip 不可用
    ) else (
        "!CHECK_PY!" -m pip --version
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
echo 若 [1] 顯示已安裝 Python（例如 3.13.14）：
echo   - 啟動系統：雙擊 啟動名片系統_Windows.bat
echo   - 打包 exe：雙擊 build_windows_exe.bat
echo.
echo 若 [1] 顯示未安裝：
echo   - 先雙擊 install_python_windows.bat
echo.
pause
endlocal
