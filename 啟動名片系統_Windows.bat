@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"
call "%~dp0start_upload_app_windows_auto_venv.bat"
endlocal
