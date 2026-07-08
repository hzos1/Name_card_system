@echo off
title 名片系統（區域網路）
cd /d "%~dp0dist\Name_card_system"
set NAMECARD_HOST=0.0.0.0
Name_card_system.exe
