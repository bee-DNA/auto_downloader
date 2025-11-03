# PowerShell 腳本 - 下載最後 3 個缺失的樣本
# 這個腳本應該在運行 Docker 的機器上執行

# 確保 runs_to_fix.txt 存在
if (!(Test-Path "runs_to_fix.txt")) {
    Write-Host "❌ 找不到 runs_to_fix.txt" -ForegroundColor Red
    Write-Host "請先在開發機器上運行 verify_fastq_smart.py 生成該檔案" -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 runs_to_fix.txt 內容:" -ForegroundColor Cyan
Get-Content runs_to_fix.txt

Write-Host ""
Write-Host "🚀 開始下載..." -ForegroundColor Green
Write-Host ""

# 方法 1: 使用 runs_to_fix.txt
docker run --rm `
  -v "${PWD}\data:/app/data" `
  -e RUNS_FILE=runs_to_fix.txt `
  auto_downloader

Write-Host ""
Write-Host "✅ 下載完成！" -ForegroundColor Green
Write-Host "請在開發機器上運行 verify_fastq_smart.py 確認全部完整" -ForegroundColor Yellow
