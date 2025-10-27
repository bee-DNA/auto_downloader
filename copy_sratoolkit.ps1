Param(
    [string]$Source = "..\sratoolkit.3.2.1-win64",
    [string]$Dest = ".\sratoolkit.3.2.1-win64"
)

Write-Host "開始複製 SRA Toolkit..."
if (-Not (Test-Path $Source)) {
    Write-Host "找不到來源資料夾: $Source" -ForegroundColor Red
    exit 1
}

if (Test-Path $Dest) {
    Write-Host "目的地已存在: $Dest，將覆蓋/同步內容..." -ForegroundColor Yellow
}

robocopy $Source $Dest /MIR /NDL /NFL /NJH /NJS /MT:8
$rc = $LASTEXITCODE
if ($rc -lt 8) {
    Write-Host "✅ SRA Toolkit 已成功複製到 $Dest"
    exit 0
}
else {
    Write-Host "❌ 複製失敗，robocopy 返回代碼: $rc" -ForegroundColor Red
    exit $rc
}
