# Unblock SRA Toolkit Files
# Windows marks downloaded files as unsafe - this script unblocks them

Write-Host "================================================================================"
Write-Host "Unblocking SRA Toolkit Files"
Write-Host "================================================================================"
Write-Host ""

$toolkitPath = ".\sratoolkit.3.2.1-win64"

# Check if toolkit folder exists
if (-not (Test-Path $toolkitPath)) {
    Write-Host "ERROR: sratoolkit.3.2.1-win64 folder not found" -ForegroundColor Red
    Write-Host "Please ensure the toolkit is in this directory" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "[Step 1/3] Unblocking all files..." -ForegroundColor Cyan
Write-Host ""

try {
    # Unblock all files recursively
    Get-ChildItem -Path $toolkitPath -Recurse -File | Unblock-File -ErrorAction SilentlyContinue
    Write-Host "SUCCESS: All files have been unblocked" -ForegroundColor Green
}
catch {
    Write-Host "WARNING: Some files could not be unblocked: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[Step 2/3] Testing prefetch.exe..." -ForegroundColor Cyan
Write-Host ""

$prefetchPath = Join-Path $toolkitPath "bin\prefetch.exe"

if (Test-Path $prefetchPath) {
    Write-Host "Running: prefetch.exe --version" -ForegroundColor Gray
    
    try {
        $output = & $prefetchPath --version 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-Host "SUCCESS: prefetch.exe works correctly" -ForegroundColor Green
            Write-Host "Version: $($output[0])" -ForegroundColor Gray
        }
        else {
            Write-Host "ERROR: prefetch.exe failed (exit code: $exitCode)" -ForegroundColor Red
            Write-Host "Output: $output" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "ERROR: Exception occurred: $($_.Exception.Message)" -ForegroundColor Red
    }
}
else {
    Write-Host "ERROR: prefetch.exe not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "[Step 3/3] Testing fasterq-dump.exe..." -ForegroundColor Cyan
Write-Host ""

$fasterqPath = Join-Path $toolkitPath "bin\fasterq-dump.exe"

if (Test-Path $fasterqPath) {
    try {
        $output = & $fasterqPath --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "SUCCESS: fasterq-dump.exe works correctly" -ForegroundColor Green
            Write-Host "Version: $($output[0])" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "WARNING: fasterq-dump.exe test failed" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "================================================================================"
Write-Host "Complete"
Write-Host "================================================================================"
Write-Host ""

Write-Host "If tools still don't work, you may need to:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Install Visual C++ Redistributable" -ForegroundColor Gray
Write-Host "   Download: https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Check antivirus software" -ForegroundColor Gray
Write-Host "   Temporarily disable or add to exceptions" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Run as Administrator" -ForegroundColor Gray
Write-Host "   Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Gray
Write-Host ""

pause
