# 自動安裝 SRA Toolkit
# 如果本地沒有 sratoolkit，從 NCBI 官方下載並安裝

param(
    [string]$Version = "3.2.1"
)

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "📦 自動安裝 SRA Toolkit" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$toolkitDir = "sratoolkit.${Version}-win64"
$zipFile = "${toolkitDir}.zip"
$downloadUrl = "https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/${Version}/sratoolkit.${Version}-win64.zip"

# 檢查是否已經存在
if (Test-Path $toolkitDir) {
    Write-Host "✅ SRA Toolkit 已存在: $toolkitDir" -ForegroundColor Green
    
    # 測試是否能執行
    $prefetch = Join-Path $toolkitDir "bin\prefetch.exe"
    if (Test-Path $prefetch) {
        try {
            $output = & $prefetch --version 2>&1
            Write-Host "✅ 版本: $($output[0])" -ForegroundColor Green
            Write-Host ""
            Write-Host "無需重新安裝。" -ForegroundColor Yellow
            exit 0
        }
        catch {
            Write-Host "⚠️ 現有的 toolkit 無法執行，將重新安裝" -ForegroundColor Yellow
        }
    }
}

Write-Host "[1/4] 下載 SRA Toolkit..." -ForegroundColor Cyan
Write-Host "來源: $downloadUrl" -ForegroundColor Gray
Write-Host ""

try {
    # 使用 WebClient 下載，顯示進度
    $webClient = New-Object System.Net.WebClient
    
    # 註冊進度事件
    Register-ObjectEvent -InputObject $webClient -EventName DownloadProgressChanged -SourceIdentifier WebClient.DownloadProgressChanged -Action {
        $percent = $EventArgs.ProgressPercentage
        Write-Progress -Activity "下載 SRA Toolkit" -Status "$percent% 完成" -PercentComplete $percent
    } | Out-Null
    
    # 開始下載
    $webClient.DownloadFileAsync((New-Object System.Uri($downloadUrl)), $zipFile)
    
    # 等待下載完成
    while ($webClient.IsBusy) {
        Start-Sleep -Milliseconds 100
    }
    
    # 取消註冊事件
    Unregister-Event -SourceIdentifier WebClient.DownloadProgressChanged -ErrorAction SilentlyContinue
    Write-Progress -Activity "下載 SRA Toolkit" -Completed
    
    Write-Host "✅ 下載完成: $zipFile" -ForegroundColor Green
    
    # 顯示檔案大小
    $fileSize = (Get-Item $zipFile).Length / 1MB
    Write-Host "   大小: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Gray
    
}
catch {
    Write-Host "❌ 下載失敗: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 請手動下載並放置到此目錄:" -ForegroundColor Yellow
    Write-Host "   1. 下載: $downloadUrl" -ForegroundColor Gray
    Write-Host "   2. 解壓縮到此目錄" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "[2/4] 檢查 ZIP 檔案完整性..." -ForegroundColor Cyan

if (-not (Test-Path $zipFile)) {
    Write-Host "❌ ZIP 檔案不存在" -ForegroundColor Red
    exit 1
}

$zipSize = (Get-Item $zipFile).Length
if ($zipSize -lt 10MB) {
    Write-Host "❌ ZIP 檔案太小，可能下載不完整" -ForegroundColor Red
    Write-Host "   大小: $([math]::Round($zipSize / 1MB, 2)) MB" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ ZIP 檔案完整" -ForegroundColor Green

Write-Host ""
Write-Host "[3/4] 解壓縮..." -ForegroundColor Cyan

try {
    # 如果舊資料夾存在，先刪除
    if (Test-Path $toolkitDir) {
        Write-Host "   清理舊版本..." -ForegroundColor Gray
        Remove-Item -Path $toolkitDir -Recurse -Force
    }
    
    # 解壓縮
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipFile, ".")
    
    Write-Host "✅ 解壓縮完成" -ForegroundColor Green
    
}
catch {
    Write-Host "❌ 解壓縮失敗: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[4/4] 解除封鎖並測試..." -ForegroundColor Cyan

# 解除封鎖所有檔案
try {
    Get-ChildItem -Path $toolkitDir -Recurse -File | Unblock-File -ErrorAction SilentlyContinue
    Write-Host "✅ 已解除檔案封鎖" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ 部分檔案無法解除封鎖: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 測試主要執行檔
$prefetchPath = Join-Path $toolkitDir "bin\prefetch.exe"
$fasterqPath = Join-Path $toolkitDir "bin\fasterq-dump.exe"
$validatePath = Join-Path $toolkitDir "bin\vdb-validate.exe"

$allOk = $true

foreach ($tool in @($prefetchPath, $fasterqPath, $validatePath)) {
    if (Test-Path $tool) {
        try {
            $toolName = Split-Path $tool -Leaf
            $output = & $tool --version 2>&1
            $version = $output[0]
            Write-Host "✅ $toolName : $version" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ $toolName 無法執行" -ForegroundColor Red
            $allOk = $false
        }
    }
    else {
        Write-Host "❌ 找不到: $tool" -ForegroundColor Red
        $allOk = $false
    }
}

Write-Host ""

if ($allOk) {
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "✅ SRA Toolkit 安裝成功！" -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📁 安裝位置: $((Get-Item $toolkitDir).FullName)" -ForegroundColor Gray
    Write-Host ""
    
    # 清理 ZIP 檔案
    Write-Host "🗑️  清理安裝檔案..." -ForegroundColor Gray
    Remove-Item $zipFile -Force -ErrorAction SilentlyContinue
    Write-Host "✅ 已刪除: $zipFile" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "下一步: 執行 SETUP.bat" -ForegroundColor Yellow
    
}
else {
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "⚠️ 安裝完成但部分工具無法執行" -ForegroundColor Yellow
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "💡 可能需要安裝 Visual C++ Redistributable" -ForegroundColor Yellow
    Write-Host "   下載: https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Gray
}

Write-Host ""
