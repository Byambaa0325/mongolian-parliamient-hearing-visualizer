# Update .env file with Cloud SQL connection info
# This is a PowerShell command to update the .env file

$envFile = Get-Content .env -Raw
$newContent = $envFile -replace 'DATABASE_URL=sqlite:///transcripts\.db', @'
# Default: SQLite (no setup required)
# DATABASE_URL=sqlite:///transcripts.db

# For Cloud SQL PostgreSQL (Production - lazy-jeopardy project)
# Uncomment and set your credentials:
# DATABASE_URL=postgresql://user:password@localhost/transcripts?host=/cloudsql/lazy-jeopardy:europe-west1:parliamient-hearing-db

# For local development via public IP (if authorized):
# DATABASE_URL=postgresql://user:password@35.205.155.54:5432/transcripts

# For local development via Cloud SQL Proxy:
# DATABASE_URL=postgresql://user:password@127.0.0.1:5432/transcripts
'@
Set-Content -Path .env -Value $newContent
Write-Host ".env file updated with Cloud SQL connection info"
