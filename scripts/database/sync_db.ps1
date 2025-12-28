# Database Sync Helper Script for Windows PowerShell
#
# Usage:
#   .\sync_db.ps1 push      # Push local tags to cloud
#   .\sync_db.ps1 pull      # Pull cloud tags to local
#   .\sync_db.ps1 compare   # Compare databases
#   .\sync_db.ps1 export    # Export local to JSON
#   .\sync_db.ps1 import    # Import JSON to cloud

param(
    [Parameter(Position=0)]
    [ValidateSet("push", "pull", "compare", "export", "import", "help")]
    [string]$Command = "help",
    
    [string]$Mode = "tags_only",
    [string]$File = "db_backup.json"
)

# Check if Cloud SQL URL is configured
function Check-CloudConfig {
    if (-not $env:CLOUD_DATABASE_URL -and -not $env:DATABASE_URL) {
        Write-Host "`n[!] Cloud database URL not configured!" -ForegroundColor Yellow
        Write-Host "`nSet the connection URL:`n" -ForegroundColor White
        Write-Host '  $env:CLOUD_DATABASE_URL = "postgresql://user:password@35.205.155.54:5432/transcripts"' -ForegroundColor Cyan
        Write-Host "`nOr use Cloud SQL Proxy and set:" -ForegroundColor White
        Write-Host '  $env:CLOUD_DATABASE_URL = "postgresql://user:password@127.0.0.1:5432/transcripts"' -ForegroundColor Cyan
        Write-Host ""
        return $false
    }
    return $true
}

switch ($Command) {
    "push" {
        Write-Host "[>] Pushing local changes to cloud..." -ForegroundColor Cyan
        if (Check-CloudConfig) {
            python sync_database.py push --mode $Mode
        }
    }
    "pull" {
        Write-Host "[<] Pulling cloud changes to local..." -ForegroundColor Cyan
        if (Check-CloudConfig) {
            python sync_database.py pull --mode $Mode
        }
    }
    "compare" {
        Write-Host "[?] Comparing databases..." -ForegroundColor Cyan
        if (Check-CloudConfig) {
            python sync_database.py compare
        }
    }
    "export" {
        Write-Host "[^] Exporting local database to $File..." -ForegroundColor Cyan
        python sync_database.py export --output $File
    }
    "import" {
        Write-Host "[v] Importing $File to cloud..." -ForegroundColor Cyan
        if (Check-CloudConfig) {
            python sync_database.py import --input $File --mode $Mode
        }
    }
    "help" {
        Write-Host "`nDatabase Sync Commands" -ForegroundColor Green
        Write-Host "=" * 50
        Write-Host "`nCommands:"
        Write-Host "  push     - Push local tags to cloud database" -ForegroundColor Cyan
        Write-Host "  pull     - Pull cloud tags to local database" -ForegroundColor Cyan
        Write-Host "  compare  - Compare local and cloud databases" -ForegroundColor Cyan
        Write-Host "  export   - Export local database to JSON file" -ForegroundColor Cyan
        Write-Host "  import   - Import JSON file to cloud database" -ForegroundColor Cyan
        Write-Host "`nOptions:"
        Write-Host "  -Mode    - Sync mode: tags_only (default), merge, replace"
        Write-Host "  -File    - JSON file for export/import (default: db_backup.json)"
        Write-Host "`nExamples:"
        Write-Host '  .\sync_db.ps1 push                    # Push only tag changes' -ForegroundColor Gray
        Write-Host '  .\sync_db.ps1 push -Mode merge        # Push all changes' -ForegroundColor Gray
        Write-Host '  .\sync_db.ps1 pull                    # Pull tags from cloud' -ForegroundColor Gray
        Write-Host '  .\sync_db.ps1 export -File backup.json' -ForegroundColor Gray
        Write-Host "`nSetup (run once before push/pull):"
        Write-Host '  $env:CLOUD_DATABASE_URL = "postgresql://user:pass@35.205.155.54:5432/transcripts"' -ForegroundColor Yellow
        Write-Host ""
    }
}
