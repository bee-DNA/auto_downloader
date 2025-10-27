# 解除 SRA Toolkit 檔案封鎖
# Windows 從網路下載的檔案會被標記為不安全，需要解除封鎖才能執行

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "解除 SRA Toolkit 檔案封鎖" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$toolkitPath = ".\sratoolkit.3.2.1-win64"

if (-not (Test-Path $toolkitPath)) {
    Write-Host "錯誤: 找不到 sratoolkit.3.2.1-win64 資料夾" -ForegroundColor Red
    Write-Host "請確認已將 sratoolkit 複製到此目錄" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "[1/3] 檢查需要解除封鎖的檔案..." -ForegroundColor Cyan
Write-Host ""

# 解除所有檔案的封鎖（簡化版本，避免編碼問題）
try {
    Get-ChildItem -Path $toolkitPath -Recurse -File | Unblock-File -ErrorAction SilentlyContinue
    Write-Host "完成: 已解除所有檔案的封鎖" -ForegroundColor Green
}
catch {
    Write-Host "警告: 部分檔案無法解除封鎖" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[2/3] 測試 prefetch.exe..." -ForegroundColor Cyan
Write-Host ""

$prefetchPath = Join-Path $toolkitPath "bin\prefetch.exe"

if (Test-Path $prefetchPath) {
    Write-Host "執行: $prefetchPath --version" -ForegroundColor Gray
    
    try {
        $output = & $prefetchPath --version 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-Host "成功: prefetch.exe 可以正常執行" -ForegroundColor Green
            Write-Host "版本: $($output[0])" -ForegroundColor Gray
        }
        else {
            Write-Host "失敗: prefetch.exe 執行失敗 (exit code: $exitCode)" -ForegroundColor Red
            Write-Host "輸出: $output" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "錯誤: 執行時發生問題: $($_.Exception.Message)" -ForegroundColor Red
    }
}
else {
    Write-Host "錯誤: 找不到 prefetch.exe" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "完成" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "如果仍然無法執行，可能需要:" -ForegroundColor Yellow
Write-Host "1. 安裝 Visual C++ Redistributable" -ForegroundColor Gray
Write-Host "   下載: https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 檢查防毒軟體是否封鎖" -ForegroundColor Gray
Write-Host "   暫時停用或加入例外清單" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 以系統管理員身分執行" -ForegroundColor Gray
Write-Host "   右鍵 PowerShell 選擇以系統管理員身分執行" -ForegroundColor Gray
Write-Host ""

pause
