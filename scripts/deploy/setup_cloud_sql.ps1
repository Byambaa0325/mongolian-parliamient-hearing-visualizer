# PowerShell script to setup Cloud SQL PostgreSQL database

$ErrorActionPreference = "Stop"

$PROJECT_ID = if ($env:PROJECT_ID) { $env:PROJECT_ID } else { gcloud config get-value project }
$REGION = if ($env:REGION) { $env:REGION } else { "us-central1" }
$INSTANCE_NAME = if ($env:INSTANCE_NAME) { $env:INSTANCE_NAME } else { "transcript-db" }
$DATABASE_NAME = if ($env:DATABASE_NAME) { $env:DATABASE_NAME } else { "transcripts" }
$DB_USER = if ($env:DB_USER) { $env:DB_USER } else { "transcript_user" }

if (-not $PROJECT_ID) {
    Write-Host "Error: PROJECT_ID not set" -ForegroundColor Red
    Write-Host "Run: `$env:PROJECT_ID = 'your-project-id'"
    exit 1
}

Write-Host "Setting up Cloud SQL for project: $PROJECT_ID" -ForegroundColor Green

# Create Cloud SQL instance
Write-Host "Creating Cloud SQL instance..." -ForegroundColor Yellow
$rootPassword = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})

gcloud sql instances create $INSTANCE_NAME `
    --database-version=POSTGRES_14 `
    --tier=db-f1-micro `
    --region=$REGION `
    --project=$PROJECT_ID `
    --root-password=$rootPassword 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Instance may already exist, continuing..." -ForegroundColor Yellow
}

# Create database
Write-Host "Creating database..." -ForegroundColor Yellow
gcloud sql databases create $DATABASE_NAME `
    --instance=$INSTANCE_NAME `
    --project=$PROJECT_ID 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Database may already exist, continuing..." -ForegroundColor Yellow
}

# Create user
Write-Host "Creating database user..." -ForegroundColor Yellow
$DB_PASSWORD = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})

gcloud sql users create $DB_USER `
    --instance=$INSTANCE_NAME `
    --password=$DB_PASSWORD `
    --project=$PROJECT_ID 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "User may already exist, continuing..." -ForegroundColor Yellow
}

# Get connection name
$CONNECTION_NAME = gcloud sql instances describe $INSTANCE_NAME `
    --project=$PROJECT_ID `
    --format='value(connectionName)'

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Cloud SQL Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Connection Name: $CONNECTION_NAME" -ForegroundColor Cyan
Write-Host "Database: $DATABASE_NAME" -ForegroundColor Cyan
Write-Host "User: $DB_USER" -ForegroundColor Cyan
Write-Host "Password: $DB_PASSWORD" -ForegroundColor Cyan
Write-Host ""
Write-Host "Save this password securely!" -ForegroundColor Yellow
Write-Host ""
Write-Host "DATABASE_URL format:" -ForegroundColor Cyan
Write-Host "postgresql://$DB_USER`:$DB_PASSWORD@localhost/$DATABASE_NAME?host=/cloudsql/$CONNECTION_NAME"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update Cloud Run service to use Cloud SQL:"
Write-Host "   gcloud run services update transcript-tagger \"
Write-Host "     --add-cloudsql-instances=$CONNECTION_NAME \"
Write-Host "     --set-env-vars DATABASE_URL=postgresql://$DB_USER`:$DB_PASSWORD@localhost/$DATABASE_NAME?host=/cloudsql/$CONNECTION_NAME \"
Write-Host "     --region $REGION \"
Write-Host "     --project $PROJECT_ID"
Write-Host ""
Write-Host "2. Load transcripts after deployment"
Write-Host ""

