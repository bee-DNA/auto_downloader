@echo off
chcp 65001 >nul
title 一鍵安裝 SRA Toolkit

echo ================================================================================
echo 📦 一鍵安裝 SRA Toolkit
echo ================================================================================
echo.
echo 此腳本將自動從 NCBI 官方下載並安裝 SRA Toolkit 3.2.1
echo.
echo 需要:
echo   - 網路連線
echo   - 約 60 MB 下載
echo   - 1-2 分鐘時間
echo.

pause

echo.
echo ⏳ 開始安裝...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "安裝_SRA_Toolkit.ps1"

if errorlevel 1 (
    echo.
    echo ❌ 安裝失敗
    echo.
    echo 💡 請嘗試:
    echo    1. 檢查網路連線
    echo    2. 手動下載: https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/3.2.1/sratoolkit.3.2.1-win64.zip
    echo    3. 解壓縮到此目錄
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ================================================================================
    echo ✅ 安裝完成！
    echo ================================================================================
    echo.
    echo 下一步: 執行 SETUP.bat
    echo.
    pause
)
