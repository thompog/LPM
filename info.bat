@echo off
title Info getter
:: This file is for getting data that python is not good at getting, such as the current directory and windows username and windows version just stuff like that, and then it will write it to a file called info.txt

@echo off
rem -- Prefer running the PowerShell collector when available
where powershell >nul 2>&1
if %ERRORLEVEL%==0 (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0info.ps1"
) else (
    echo PowerShell not found. Please run info.ps1 manually on a system with PowerShell.
)