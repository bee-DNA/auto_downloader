@echo off
chcp 65001 >nul
title 安裝 Visual C++ Redistributable

echo ================================================================================
echo 安裝 Visual C++ Redistributable
echo ================================================================================
echo.
echo 💡 SRA Toolkit 需要 Visual C++ 執行環境
echo.
echo 📥 即將下載並安裝 Visual C++ Redistributable (約 25 MB)
echo.
echo ⚠️  安裝過程中會彈出 UAC 權限請求視窗，請點選「是」
echo.
pause

echo.
echo 正在下載...
powershell -NoProfile -Command "& { $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile 'vc_redist.x64.exe' }"

if errorlevel 1 (
    echo.
    echo ❌ 下載失敗
    echo.
    echo 請手動下載並安裝:
    echo https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ 下載完成
echo.
echo 正在啟動安裝程式...
echo （請在彈出視窗中完成安裝）
echo.

start /wait vc_redist.x64.exe /install /quiet /norestart

if errorlevel 1 (
    echo.
    echo ⚠️  自動安裝可能失敗，請手動執行安裝
    echo.
    start vc_redist.x64.exe
    pause
) else (
    echo.
    echo ✅ 安裝完成！
    echo.
    echo 正在清理暫存檔...
    del /f /q vc_redist.x64.exe
    echo.
    echo ✅ 可以繼續執行 SETUP.bat 了
    echo.
)

pause
