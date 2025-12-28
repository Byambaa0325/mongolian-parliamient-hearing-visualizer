# PowerShell script to start only the backend server

Write-Host "Starting Flask Backend Server..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Host "Error: Python not found. Please install Python 3." -ForegroundColor Red
    exit 1
}

Write-Host "Python found: $($python.Source)" -ForegroundColor Green

# Check if port 8080 is already in use
$portInUse = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "Warning: Port 8080 is already in use!" -ForegroundColor Yellow
    Write-Host "Process ID: $($portInUse.OwningProcess)" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Kill existing process and start new server? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Stop-Process -Id $portInUse.OwningProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    } else {
        Write-Host "Exiting. Please stop the existing server first." -ForegroundColor Red
        exit 1
    }
}

# Check Python dependencies
Write-Host "Checking Python dependencies..." -ForegroundColor Yellow
$flaskInstalled = & $python.Source -c "import flask" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    & $python.Source -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install Python dependencies" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Flask Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will run on: http://localhost:8080" -ForegroundColor Green
Write-Host "API endpoint: http://localhost:8080/api/transcripts" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
& $python.Source server.py

