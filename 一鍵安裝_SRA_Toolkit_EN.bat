@echo off
title Auto-Install SRA Toolkit from NCBI

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install_SRA_Toolkit.ps1"

if errorlevel 1 (
    echo.
    echo Installation failed. Check the error messages above.
    echo.
    pause
)
