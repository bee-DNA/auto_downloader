# PowerShell Script for Automated Downloader (Docker-Ready)

# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Set window title
$Host.UI.RawUI.WindowTitle = "Auto Downloader"

Write-Host "================================="
Write-Host "Starting Auto Downloader System"
Write-Host "================================="
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# --- Step 1: Run quick check ---
Write-Host "[1/3] Running environment check..."
python quick_check.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Environment check failed. Please review the messages above." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Environment check OK." -ForegroundColor Green
Write-Host ""


# --- Step 2: Create local directories ---
Write-Host "[2/3] Creating local data directories..."
# Run the check_and_create_paths function from config.py
python -c "from config import check_and_create_paths; check_and_create_paths()"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create local directories." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Directory setup OK." -ForegroundColor Green
Write-Host ""


# --- Step 3: Run the main application ---
Write-Host "[3/3] Starting the main application..."
Write-Host "Press Ctrl+C to stop the process at any time."
Write-Host ""

python complete_downloader.py

Write-Host ""
Write-Host "================================="
Write-Host "Script finished. Exit code: $LASTEXITCODE"
Write-Host "================================="
Read-Host "Press Enter to exit"

