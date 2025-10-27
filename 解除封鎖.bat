@echo off
chcp 65001 >nul
title 解除 SRA Toolkit 封鎖

echo ================================================================================
echo 解除 SRA Toolkit 檔案封鎖
echo ================================================================================
echo.

echo 正在解除封鎖...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -Path '.\sratoolkit.3.2.1-win64' -Recurse -File | Unblock-File -ErrorAction SilentlyContinue"

if errorlevel 1 (
    echo.
    echo 警告: 解除封鎖時發生錯誤
    echo.
) else (
    echo.
    echo 完成: 已解除所有檔案的封鎖
    echo.
)

echo 測試 prefetch.exe...
echo.

if exist "sratoolkit.3.2.1-win64\bin\prefetch.exe" (
    "sratoolkit.3.2.1-win64\bin\prefetch.exe" --version
    if errorlevel 1 (
        echo.
        echo 錯誤: prefetch.exe 仍無法執行
        echo.
        echo 可能需要:
        echo   1. 安裝 Visual C++ Redistributable
        echo      下載: https://aka.ms/vs/17/release/vc_redist.x64.exe
        echo.
        echo   2. 檢查防毒軟體是否封鎖
        echo.
    ) else (
        echo.
        echo 成功: prefetch.exe 可以正常執行
        echo.
    )
) else (
    echo.
    echo 錯誤: 找不到 prefetch.exe
    echo 請確認 sratoolkit.3.2.1-win64 資料夾已放置到此目錄
    echo.
)

echo.
echo ================================================================================
pause

echo ================================================================================
echo.

pause
