# PowerShell script to load transcripts into database

Write-Host "Loading transcripts into database..." -ForegroundColor Green

# Check if Python is available
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Host "Error: Python not found" -ForegroundColor Red
    exit 1
}

# Run the load script
& $python -m backend.load_transcripts

Write-Host "Done!" -ForegroundColor Green

