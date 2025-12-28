# Quick script to restart the backend server

Write-Host "Stopping any existing backend servers..." -ForegroundColor Yellow

# Find and kill Python processes on port 8080
$connections = netstat -ano | findstr :8080 | findstr LISTENING
if ($connections) {
    $pid = ($connections -split '\s+')[-1]
    if ($pid) {
        Write-Host "Killing process $pid on port 8080..." -ForegroundColor Yellow
        taskkill /PID $pid /F 2>$null
        Start-Sleep -Seconds 1
    }
}

# Check if Python is available
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Host "Error: Python not found" -ForegroundColor Red
    exit 1
}

Write-Host "Starting backend server..." -ForegroundColor Green
Write-Host "Backend will be available at http://localhost:8080" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

& $python.Source server.py

