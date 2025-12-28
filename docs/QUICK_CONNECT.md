# Quick Database Connection Guide

## Your Database Info

- **Connection Name**: `lazy-jeopardy:europe-west1:parliamient-hearing-db`
- **Public IP**: `35.205.155.54`
- **Port**: `5432`
- **Project**: `lazy-jeopardy`
- **Region**: `europe-west1`

## Connect Cloud Run Service (After Deployment)

### Windows PowerShell:
```powershell
# Set your database credentials
$env:DB_PASSWORD = "your-database-password"
$env:DB_USER = "your-database-user"  # e.g., postgres
$env:DB_NAME = "transcripts"  # or your database name

# Run connection script
.\scripts\database\connect_database.ps1
```

### Linux/Mac:
```bash
# Set your database credentials
export DB_PASSWORD="your-database-password"
export DB_USER="your-database-user"
export DB_NAME="transcripts"

# Run connection script
./scripts/database/connect_database.sh
```

## Manual Connection (Alternative)

```bash
# Set variables
export PROJECT_ID=lazy-jeopardy
export REGION=europe-west1
export SERVICE_NAME=transcript-tagger
export CONNECTION_NAME=lazy-jeopardy:europe-west1:parliamient-hearing-db
export DB_USER=your-database-user
export DB_PASSWORD=your-database-password
export DB_NAME=transcripts

# Build connection string
DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}?host=/cloudsql/${CONNECTION_NAME}"

# Connect Cloud Run
gcloud run services update $SERVICE_NAME \
  --add-cloudsql-instances=$CONNECTION_NAME \
  --set-env-vars DATABASE_URL="$DATABASE_URL" \
  --region $REGION \
  --project $PROJECT_ID
```

## Find Database Credentials

If you don't know your database credentials:

```bash
# List users
gcloud sql users list \
  --instance=parliamient-hearing-db \
  --project=lazy-jeopardy

# List databases
gcloud sql databases list \
  --instance=parliamient-hearing-db \
  --project=lazy-jeopardy
```

## Initialize Database

After connecting, initialize the schema and load transcripts:

```bash
# Set DATABASE_URL for local execution
export DATABASE_URL="postgresql://user:password@35.205.155.54:5432/transcripts"

# Initialize schema
python3 -c "from backend.api import app; app.app_context().push(); from backend.database import db; db.create_all(); print('Schema created')"

# Load transcripts
python3 -m backend.load_transcripts
```

## Next Steps

1. ✅ Deploy the app (if not already deployed)
2. ✅ Connect to database using script above
3. ✅ Initialize database schema
4. ✅ Load transcript files
5. ✅ Start tagging!

See [DATABASE_CONNECTION.md](DATABASE_CONNECTION.md) for detailed instructions.

