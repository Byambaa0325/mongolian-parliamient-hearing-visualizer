# Database Setup for Cloud Run

## Overview

Since Cloud Run is **serverless and stateless**, we need a **managed database service** for persistent storage. This guide sets up **Cloud SQL PostgreSQL** which is the recommended database for Cloud Run applications.

## Why Cloud SQL?

- ✅ **Persistent storage** - Data survives container restarts
- ✅ **Managed service** - Google handles backups, updates, scaling
- ✅ **Cloud Run integration** - Easy connection via Unix sockets
- ✅ **Production-ready** - Supports high concurrency and large datasets

## Quick Setup

### Step 1: Create Cloud SQL Instance

Run the setup script:

```bash
# Linux/Mac
export PROJECT_ID=your-project-id
./setup_cloud_sql.sh

# Windows PowerShell
$env:PROJECT_ID = "your-project-id"
.\setup_cloud_sql.ps1
```

This will:
- Create a PostgreSQL 14 instance
- Create the `transcripts` database
- Create a database user
- Generate a secure password
- Show you the connection details

**⚠️ Save the password!** You'll need it for the DATABASE_URL.

### Step 2: Get Connection Name

After setup, get your connection name:

```bash
gcloud sql instances describe transcript-db \
  --format='value(connectionName)'
```

Output format: `PROJECT_ID:REGION:transcript-db`

### Step 3: Update Cloud Run Service

After deploying your app, connect it to Cloud SQL:

```bash
# Set variables
export PROJECT_ID=your-project-id
export REGION=us-central1
export CONNECTION_NAME=$(gcloud sql instances describe transcript-db \
  --format='value(connectionName)')
export DB_USER=transcript_user
export DB_PASSWORD=your-password-from-step-1
export DATABASE_NAME=transcripts

# Update Cloud Run service
gcloud run services update transcript-tagger \
  --add-cloudsql-instances=$CONNECTION_NAME \
  --set-env-vars DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@localhost/$DATABASE_NAME?host=/cloudsql/$CONNECTION_NAME" \
  --region $REGION \
  --project $PROJECT_ID
```

### Step 4: Load Transcripts

After connecting to Cloud SQL, load the transcripts:

**Option A: Cloud Run Job (Recommended)**

```bash
# Create a one-time job
gcloud run jobs create load-transcripts \
  --image gcr.io/$PROJECT_ID/transcript-tagger \
  --region $REGION \
  --command python3 \
  --args -m,backend.load_transcripts \
  --set-env-vars DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@localhost/$DATABASE_NAME?host=/cloudsql/$CONNECTION_NAME" \
  --add-cloudsql-instances=$CONNECTION_NAME \
  --project $PROJECT_ID

# Execute the job
gcloud run jobs execute load-transcripts \
  --region $REGION \
  --project $PROJECT_ID
```

**Option B: Local with Cloud SQL Proxy**

```bash
# Install Cloud SQL Proxy
# https://cloud.google.com/sql/docs/postgres/connect-instance-auth-proxy

# Start proxy
./cloud-sql-proxy $CONNECTION_NAME

# In another terminal, set DATABASE_URL
export DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@127.0.0.1:5432/$DATABASE_NAME"

# Load transcripts
python3 -m backend.load_transcripts
```

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Instance

```bash
gcloud sql instances create transcript-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=$(openssl rand -base64 32)
```

### 2. Create Database

```bash
gcloud sql databases create transcripts \
  --instance=transcript-db
```

### 3. Create User

```bash
gcloud sql users create transcript_user \
  --instance=transcript-db \
  --password=YOUR_SECURE_PASSWORD
```

### 4. Get Connection Name

```bash
gcloud sql instances describe transcript-db \
  --format='value(connectionName)'
```

## DATABASE_URL Format

For Cloud SQL via Unix socket (Cloud Run):

```
postgresql://USER:PASSWORD@localhost/DATABASE?host=/cloudsql/CONNECTION_NAME
```

Example:
```
postgresql://transcript_user:mypassword@localhost/transcripts?host=/cloudsql/myproject:us-central1:transcript-db
```

## Cost Estimation

**Cloud SQL db-f1-micro:**
- ~$7-10/month for the instance
- Storage: $0.17/GB/month
- Network egress: Standard pricing

**For development/testing:**
- Can use SQLite locally (free)
- Switch to Cloud SQL only for production

## Troubleshooting

### Connection Refused

**Problem:** Cloud Run can't connect to Cloud SQL

**Solution:**
1. Verify Cloud SQL instance is running:
   ```bash
   gcloud sql instances describe transcript-db
   ```

2. Check Cloud Run has Cloud SQL connection:
   ```bash
   gcloud run services describe transcript-tagger \
     --format='value(spec.template.spec.containers[0].env)' | grep cloudsql
   ```

3. Verify connection name format: `PROJECT_ID:REGION:INSTANCE_NAME`

### Authentication Failed

**Problem:** Wrong username/password

**Solution:**
1. Reset password:
   ```bash
   gcloud sql users set-password transcript_user \
     --instance=transcript-db \
     --password=NEW_PASSWORD
   ```

2. Update Cloud Run with new password:
   ```bash
   gcloud run services update transcript-tagger \
     --update-env-vars DATABASE_URL="postgresql://user:NEW_PASSWORD@localhost/db?host=/cloudsql/CONNECTION"
   ```

### Database Not Found

**Problem:** Database doesn't exist

**Solution:**
```bash
gcloud sql databases create transcripts --instance=transcript-db
```

### Local Development

For local development, you can use SQLite (default):

```bash
# No setup needed - uses SQLite by default
python3 -m backend.load_transcripts
```

Or connect to Cloud SQL via proxy:

```bash
# Start proxy
./cloud-sql-proxy PROJECT_ID:REGION:transcript-db

# Set DATABASE_URL
export DATABASE_URL="postgresql://user:pass@127.0.0.1:5432/transcripts"

# Load transcripts
python3 -m backend.load_transcripts
```

## Security Best Practices

1. **Use Secret Manager** for passwords (instead of env vars):
   ```bash
   # Store password in Secret Manager
   echo -n "your-password" | gcloud secrets create db-password --data-file=-
   
   # Reference in Cloud Run
   gcloud run services update transcript-tagger \
     --update-secrets DATABASE_URL=db-password:latest
   ```

2. **Use least privilege** - Create separate users for read/write

3. **Enable SSL** for connections (Cloud SQL does this by default)

4. **Regular backups** - Cloud SQL provides automatic backups

## Monitoring

### View Database Metrics

```bash
# In Cloud Console: SQL > transcript-db > Monitoring
```

### Check Connection Count

```bash
gcloud sql instances describe transcript-db \
  --format='value(settings.ipConfiguration.authorizedNetworks)'
```

### View Logs

```bash
gcloud logging read "resource.type=cloudsql_database" \
  --limit 50
```

## Backup and Restore

### Manual Backup

```bash
gcloud sql backups create \
  --instance=transcript-db
```

### Restore from Backup

```bash
gcloud sql backups restore BACKUP_ID \
  --backup-instance=transcript-db
```

---

## Summary

1. **Run setup script** → Creates Cloud SQL instance
2. **Deploy app** → Standard Cloud Run deployment
3. **Connect to Cloud SQL** → Update service with connection
4. **Load transcripts** → Run load job or script
5. **Done!** → App now has persistent database

The database persists independently of Cloud Run containers, so your data survives deployments and restarts! 🎉

