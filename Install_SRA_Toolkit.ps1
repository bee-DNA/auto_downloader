# Install SRA Toolkit from NCBI
# English version to avoid encoding issues

$ErrorActionPreference = "Stop"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Auto-Install SRA Toolkit from NCBI Official" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if already exists
$toolkitDir = ".\sratoolkit.3.2.1-win64"
$prefetch = "$toolkitDir\bin\prefetch.exe"

if (Test-Path $prefetch) {
    Write-Host "[INFO] Found existing toolkit, testing..." -ForegroundColor Yellow
    Write-Host ""
    
    $output = & $prefetch --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Toolkit already installed and working!" -ForegroundColor Green
        Write-Host ""
        Write-Host $output
        Write-Host ""
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 0
    }
    else {
        Write-Host "[WARNING] Existing toolkit cannot execute" -ForegroundColor Yellow
        Write-Host "[INFO] Will download fresh copy from NCBI..." -ForegroundColor Cyan
        Write-Host ""
        
        # Backup old version
        if (Test-Path $toolkitDir) {
            $backupName = "sratoolkit.3.2.1-win64.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Write-Host "[INFO] Backing up old version to: $backupName" -ForegroundColor Cyan
            Rename-Item $toolkitDir $backupName
        }
    }
}

# Download settings
$downloadUrl = "https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/3.2.1/sratoolkit.3.2.1-win64.zip"
$zipFile = "sratoolkit.3.2.1-win64.zip"

Write-Host "[1/4] Downloading from NCBI..." -ForegroundColor Cyan
Write-Host "URL: $downloadUrl" -ForegroundColor Gray
Write-Host ""

try {
    # Create WebClient with progress
    $webClient = New-Object System.Net.WebClient
    
    # Progress handler
    $progressHandler = {
        param($sender, $e)
        $percent = $e.ProgressPercentage
        $received = [math]::Round($e.BytesReceived / 1MB, 2)
        $total = [math]::Round($e.TotalBytesToReceive / 1MB, 2)
        Write-Progress -Activity "Downloading SRA Toolkit" -Status "$received MB / $total MB" -PercentComplete $percent
    }
    
    Register-ObjectEvent -InputObject $webClient -EventName DownloadProgressChanged -Action $progressHandler | Out-Null
    
    # Start download
    $downloadTask = $webClient.DownloadFileTaskAsync($downloadUrl, $zipFile)
    
    # Wait for completion
    while (!$downloadTask.IsCompleted) {
        Start-Sleep -Milliseconds 100
    }
    
    # Cleanup events
    Get-EventSubscriber | Where-Object { $_.SourceObject -eq $webClient } | Unregister-Event
    
    Write-Progress -Activity "Downloading SRA Toolkit" -Completed
    
    Write-Host "[SUCCESS] Download completed" -ForegroundColor Green
    
    # Verify file size
    $fileSize = (Get-Item $zipFile).Length / 1MB
    Write-Host "[INFO] File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    
    if ($fileSize -lt 50) {
        throw "File size too small, download may be incomplete"
    }
    
}
catch {
    Write-Host ""
    Write-Host "[ERROR] Download failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please manually download from:" -ForegroundColor Yellow
    Write-Host $downloadUrl -ForegroundColor Gray
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "[2/4] Extracting files..." -ForegroundColor Cyan

try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipFile, ".")
    Write-Host "[SUCCESS] Extraction completed" -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "[ERROR] Extraction failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "[3/4] Unblocking files..." -ForegroundColor Cyan

try {
    $files = Get-ChildItem -Path $toolkitDir -Recurse -File
    $count = 0
    foreach ($file in $files) {
        Unblock-File -Path $file.FullName -ErrorAction SilentlyContinue
        $count++
    }
    Write-Host "[SUCCESS] Unblocked $count files" -ForegroundColor Green
}
catch {
    Write-Host "[WARNING] Some files may not be unblocked" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/4] Testing installation..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path $prefetch) {
    $output = & $prefetch --version 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] prefetch.exe is working!" -ForegroundColor Green
        Write-Host $output
        Write-Host ""
        
        # Test fasterq-dump
        $fasterq = "$toolkitDir\bin\fasterq-dump.exe"
        if (Test-Path $fasterq) {
            $output2 = & $fasterq --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[SUCCESS] fasterq-dump.exe is working!" -ForegroundColor Green
                Write-Host $output2
            }
        }
        
        Write-Host ""
        Write-Host "[INFO] Cleaning up..." -ForegroundColor Cyan
        Remove-Item $zipFile -Force -ErrorAction SilentlyContinue
        
        Write-Host ""
        Write-Host "================================================================================" -ForegroundColor Green
        Write-Host "  Installation Complete!" -ForegroundColor Green
        Write-Host "================================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next step: Run SETUP.bat to initialize the system" -ForegroundColor Cyan
        Write-Host ""
        
    }
    else {
        Write-Host "[ERROR] prefetch.exe cannot execute" -ForegroundColor Red
        Write-Host ""
        Write-Host "This may be caused by:" -ForegroundColor Yellow
        Write-Host "  1. Missing Visual C++ Redistributable" -ForegroundColor Yellow
        Write-Host "  2. Antivirus software blocking" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Try installing Visual C++ Redistributable:" -ForegroundColor Cyan
        Write-Host "  Run: .\Install_VC++_Redistributable.bat" -ForegroundColor Gray
        Write-Host "  Or download: https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Gray
        Write-Host ""
    }
}
else {
    Write-Host "[ERROR] prefetch.exe not found after extraction" -ForegroundColor Red
    Write-Host ""
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
