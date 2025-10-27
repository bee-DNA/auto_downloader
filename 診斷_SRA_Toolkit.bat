@echo off
chcp 65001 >nul
title 診斷 SRA Toolkit 問題

echo ================================================================================
echo 🔍 診斷 SRA Toolkit 執行問題
echo ================================================================================
echo.

echo [1/5] 檢查檔案是否存在...
echo.

if exist "sratoolkit.3.2.1-win64\bin\prefetch.exe" (
    echo ✅ prefetch.exe 存在
    dir "sratoolkit.3.2.1-win64\bin\prefetch.exe"
) else (
    echo ❌ prefetch.exe 不存在
    echo 請確認 sratoolkit.3.2.1-win64 資料夾已完整複製
    pause
    exit /b 1
)

echo.
echo [2/5] 檢查檔案大小...
echo.

for %%F in ("sratoolkit.3.2.1-win64\bin\prefetch.exe") do (
    echo prefetch.exe 大小: %%~zF bytes
    if %%~zF LSS 1000000 (
        echo ⚠️ 檔案太小，可能下載不完整
    ) else (
        echo ✅ 檔案大小正常
    )
)

echo.
echo [3/5] 嘗試直接執行...
echo.

echo 執行: sratoolkit.3.2.1-win64\bin\prefetch.exe --version
"sratoolkit.3.2.1-win64\bin\prefetch.exe" --version
if errorlevel 1 (
    echo ❌ 執行失敗，錯誤碼: %ERRORLEVEL%
) else (
    echo ✅ 執行成功
)

echo.
echo [4/5] 檢查依賴的 DLL...
echo.

if exist "sratoolkit.3.2.1-win64\bin\ncbi-vdb.dll" (
    echo ✅ ncbi-vdb.dll 存在
) else (
    echo ⚠️ ncbi-vdb.dll 不存在
)

echo.
echo [5/5] 列出 bin 目錄內容...
echo.
dir /B "sratoolkit.3.2.1-win64\bin\*.exe" | findstr /I "prefetch fasterq vdb-validate"

echo.
echo ================================================================================
echo 診斷完成
echo ================================================================================
echo.
echo 💡 如果看到執行失敗，可能的原因:
echo    1. Windows Defender 或防毒軟體封鎖
echo    2. 檔案損壞或下載不完整
echo    3. 需要 Visual C++ Redistributable
echo    4. 檔案被標記為不安全 (需要解除封鎖)
echo.

pause
