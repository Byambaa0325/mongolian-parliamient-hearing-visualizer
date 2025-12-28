# Database Connection Setup

## Existing Cloud SQL Database

Your Cloud SQL PostgreSQL database is already set up:

- **Connection Name**: `lazy-jeopardy:europe-west1:parliamient-hearing-db`
- **Project**: `lazy-jeopardy`
- **Region**: `europe-west1`
- **Public IP**: `35.205.155.54`
- **Port**: `5432`

## Quick Connection Setup

### Option 1: Using the Script (Recommended)

**Windows PowerShell:**
```powershell
# Set your database password
$env:DB_PASSWORD = "your-database-password"
$env:DB_USER = "your-database-user"  # Optional, defaults to transcript_user
$env:DB_NAME = "your-database-name"  # Optional, defaults to transcripts

# Run the connection script
.\scripts\database\connect_database.ps1
```

**Linux/Mac:**
```bash
# Set your database password
export DB_PASSWORD="your-database-password"
export DB_USER="your-database-user"  # Optional
export DB_NAME="your-database-name"  # Optional

# Run the connection script
./scripts/database/connect_database.sh
```

### Option 2: Manual gcloud Command

```bash
# Set variables
export PROJECT_ID=lazy-jeopardy
export REGION=europe-west1
export SERVICE_NAME=transcript-tagger
export CONNECTION_NAME=lazy-jeopardy:europe-west1:parliamient-hearing-db
export DB_USER=your-database-user
export DB_PASSWORD=your-database-password
export DB_NAME=transcripts

# Build DATABASE_URL
DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}?host=/cloudsql/${CONNECTION_NAME}"

# Update Cloud Run service
gcloud run services update $SERVICE_NAME \
  --add-cloudsql-instances=$CONNECTION_NAME \
  --set-env-vars DATABASE_URL="$DATABASE_URL" \
  --region $REGION \
  --project $PROJECT_ID
```

## Database Credentials

You'll need:
- **Database User**: The PostgreSQL user (e.g., `postgres` or a custom user)
- **Database Password**: The user's password
- **Database Name**: The database name (e.g., `transcripts` or `postgres`)

### Finding/Setting Credentials

**Check existing users:**
```bash
gcloud sql users list \
  --instance=parliamient-hearing-db \
  --project=lazy-jeopardy
```

**Create new user (if needed):**
```bash
gcloud sql users create transcript_user \
  --instance=parliamient-hearing-db \
  --password=YOUR_SECURE_PASSWORD \
  --project=lazy-jeopardy
```

**List databases:**
```bash
gcloud sql databases list \
  --instance=parliamient-hearing-db \
  --project=lazy-jeopardy
```

**Create database (if needed):**
```bash
gcloud sql databases create transcripts \
  --instance=parliamient-hearing-db \
  --project=lazy-jeopardy
```

## Connection Methods

### 1. Cloud Run (Unix Socket - Recommended)

For Cloud Run services, use Unix socket connection:

```
postgresql://user:password@localhost/database?host=/cloudsql/CONNECTION_NAME
```

Example:
```
postgresql://transcript_user:mypassword@localhost/transcripts?host=/cloudsql/lazy-jeopardy:europe-west1:parliamient-hearing-db
```

### 2. Local Development (Public IP)

For local development, you can connect via public IP:

```
postgresql://user:password@35.205.155.54:5432/database
```

**Note**: Make sure your IP is authorized in Cloud SQL authorized networks.

### 3. Cloud SQL Proxy (Local Development)

For secure local connection:

```bash
# Download Cloud SQL Proxy
# https://cloud.google.com/sql/docs/postgres/connect-instance-auth-proxy

# Start proxy
./cloud-sql-proxy lazy-jeopardy:europe-west1:parliamient-hearing-db

# Connect via localhost
DATABASE_URL=postgresql://user:password@127.0.0.1:5432/database
```

## Update .env File

For local development, update your `.env` file:

```bash
# For Cloud SQL via public IP (if authorized)
DATABASE_URL=postgresql://user:password@35.205.155.54:5432/transcripts

# Or via Cloud SQL Proxy
DATABASE_URL=postgresql://user:password@127.0.0.1:5432/transcripts
```

## Verify Connection

### Test from Cloud Run

After deployment, check logs:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=transcript-tagger" \
  --project=lazy-jeopardy \
  --limit=20
```

### Test from Local

```bash
# Set DATABASE_URL
export DATABASE_URL="postgresql://user:password@35.205.155.54:5432/transcripts"

# Test connection
python3 -c "from backend.database import db; from flask import Flask; app = Flask(__name__); app.config['SQLALCHEMY_DATABASE_URI'] = '$DATABASE_URL'; db.init_app(app); print('Connection OK')"
```

## Initialize Database Schema

After connecting, initialize the database schema:

```bash
# Set DATABASE_URL
export DATABASE_URL="postgresql://user:password@35.205.155.54:5432/transcripts"

# Initialize schema (creates tables)
python3 -c "from backend.api import app; app.app_context().push(); from backend.database import db; db.create_all(); print('Schema created')"
```

## Load Transcripts

After schema is created, load the transcript files:

```bash
# Set DATABASE_URL
export DATABASE_URL="postgresql://user:password@35.205.155.54:5432/transcripts"

# Load transcripts
python3 -m backend.load_transcripts
```

## Troubleshooting

### Connection Refused

**Problem**: Can't connect to database

**Solutions**:
1. Verify Cloud SQL instance is running:
   ```bash
   gcloud sql instances describe parliamient-hearing-db --project=lazy-jeopardy
   ```

2. Check authorized networks (for public IP):
   ```bash
   gcloud sql instances describe parliamient-hearing-db \
     --format='value(settings.ipConfiguration.authorizedNetworks)' \
     --project=lazy-jeopardy
   ```

3. Add your IP to authorized networks:
   ```bash
   gcloud sql instances patch parliamient-hearing-db \
     --authorized-networks=YOUR_IP_ADDRESS/32 \
     --project=lazy-jeopardy
   ```

### Authentication Failed

**Problem**: Wrong username/password

**Solution**: Reset password:
```bash
gcloud sql users set-password transcript_user \
  --instance=parliamient-hearing-db \
  --password=NEW_PASSWORD \
  --project=lazy-jeopardy
```

### Database Not Found

**Problem**: Database doesn't exist

**Solution**: Create database:
```bash
gcloud sql databases create transcripts \
  --instance=parliamient-hearing-db \
  --project=lazy-jeopardy
```

### Cloud Run Can't Connect

**Problem**: Cloud Run service can't reach Cloud SQL

**Solutions**:
1. Verify Cloud SQL instance is added:
   ```bash
   gcloud run services describe transcript-tagger \
     --region=europe-west1 \
     --format='value(spec.template.spec.containers[0].env)' \
     --project=lazy-jeopardy | grep cloudsql
   ```

2. Re-add Cloud SQL connection:
   ```bash
   gcloud run services update transcript-tagger \
     --add-cloudsql-instances=lazy-jeopardy:europe-west1:parliamient-hearing-db \
     --region=europe-west1 \
     --project=lazy-jeopardy
   ```

## Security Notes

1. **Never commit passwords** to git
2. **Use Secret Manager** for production:
   ```bash
   echo -n "your-password" | gcloud secrets create db-password --data-file=-
   
   gcloud run services update transcript-tagger \
     --update-secrets DATABASE_URL=db-password:latest
   ```

3. **Use least privilege** - Create dedicated database user with only necessary permissions

4. **Enable SSL** - Cloud SQL uses SSL by default for connections

## Syncing Local and Cloud Databases

Use the `agent/sync_database.py` script to sync data between local SQLite and Cloud SQL.

### Setup

```powershell
# Set your cloud database URL
$env:CLOUD_DATABASE_URL = "postgresql://user:password@35.205.155.54:5432/transcripts"
```

### Commands

```powershell
# Compare databases (see differences)
python agent/sync_database.py compare

# Push local tags to cloud
python agent/sync_database.py push

# Pull cloud tags to local
python agent/sync_database.py pull

# Export local DB to JSON backup
python agent/sync_database.py export --output backup.json

# Import JSON to cloud (full data)
python agent/sync_database.py import --input backup.json --mode merge
```

### Sync Modes

| Mode | Description |
|------|-------------|
| `tags_only` | Only sync speaker tags (default, safest) |
| `merge` | Add new transcripts, update existing tags |
| `replace` | Clear target and import fresh (destructive!) |

### PowerShell Helper

```powershell
.\scripts\database\sync_db.ps1 push      # Push local → cloud
.\scripts\database\sync_db.ps1 pull      # Pull cloud → local
.\scripts\database\sync_db.ps1 compare   # Show differences
```

