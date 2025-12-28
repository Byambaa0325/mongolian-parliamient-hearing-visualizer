# PowerShell script to start both backend and frontend servers for local development

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Development Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
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

# Check if Node is available
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Node.js not found. Please install Node.js." -ForegroundColor Red
    exit 1
}

Write-Host "Node.js found: $(node --version)" -ForegroundColor Green
Write-Host ""

# Check if dependencies are installed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install npm dependencies" -ForegroundColor Red
        exit 1
    }
}

# Check if Python dependencies are installed
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
Write-Host "Starting Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend (Flask):  http://localhost:8080" -ForegroundColor Green
Write-Host "Frontend (React): http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
Write-Host ""

# Start backend in background job
Write-Host "Starting Flask backend..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python3 -ErrorAction SilentlyContinue
    }
    & $python.Source server.py
}

# Wait a moment for backend to start
Start-Sleep -Seconds 2

# Start frontend (this will block)
Write-Host "Starting React frontend..." -ForegroundColor Yellow
Write-Host ""

try {
    npm start
}
finally {
    # Clean up: Stop backend job when frontend stops
    Write-Host ""
    Write-Host "Stopping backend server..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Write-Host "Servers stopped." -ForegroundColor Green
}

