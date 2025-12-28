# PowerShell script to connect Cloud Run service to existing Cloud SQL database

$ErrorActionPreference = "Stop"

$PROJECT_ID = if ($env:PROJECT_ID) { $env:PROJECT_ID } else { "lazy-jeopardy" }
$REGION = if ($env:REGION) { $env:REGION } else { "europe-west1" }
$SERVICE_NAME = if ($env:SERVICE_NAME) { $env:SERVICE_NAME } else { "transcript-tagger" }
$CONNECTION_NAME = if ($env:CONNECTION_NAME) { $env:CONNECTION_NAME } else { "lazy-jeopardy:europe-west1:parliamient-hearing-db" }

# Database credentials
$DB_USER = if ($env:DB_USER) { $env:DB_USER } else { "transcript_user" }
$DB_PASSWORD = if ($env:DB_PASSWORD) { $env:DB_PASSWORD } else { $null }
$DB_NAME = if ($env:DB_NAME) { $env:DB_NAME } else { "transcripts" }

if (-not $DB_PASSWORD) {
    Write-Host "Error: DB_PASSWORD not set" -ForegroundColor Red
    Write-Host "Please set the database password:"
    Write-Host "  `$env:DB_PASSWORD = 'your-password'"
    exit 1
}

Write-Host "Connecting Cloud Run service to Cloud SQL..." -ForegroundColor Green
Write-Host "Project: $PROJECT_ID"
Write-Host "Service: $SERVICE_NAME"
Write-Host "Connection: $CONNECTION_NAME"
Write-Host ""

# Build DATABASE_URL for Cloud SQL Unix socket connection
$DATABASE_URL = "postgresql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}?host=/cloudsql/${CONNECTION_NAME}"

# Update Cloud Run service
Write-Host "Updating Cloud Run service..." -ForegroundColor Yellow
gcloud run services update $SERVICE_NAME `
  --add-cloudsql-instances=$CONNECTION_NAME `
  --set-env-vars DATABASE_URL="$DATABASE_URL" `
  --region $REGION `
  --project $PROJECT_ID

Write-Host ""
Write-Host "✓ Service updated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Database connection configured:"
Write-Host "  Connection: $CONNECTION_NAME" -ForegroundColor Cyan
Write-Host "  Database: $DB_NAME" -ForegroundColor Cyan
Write-Host "  User: $DB_USER" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Verify connection by checking service logs"
Write-Host "2. Load transcripts: python3 -m backend.load_transcripts"
Write-Host ""

