# Database Setup Guide

## Overview

The Transcript Speaker Tagger uses a database to store transcripts and tags. The 4 transcript files (12.7.txt, 12.8.txt, 12.10.txt, 12.12.txt) are loaded into the database for tagging.

## ⚠️ Important: Cloud Run is Serverless

**Cloud Run containers are ephemeral** - they don't have persistent storage. For production deployment, you **must** use a managed database service:

- **Cloud SQL PostgreSQL** (recommended for Cloud Run)
- **Cloud Firestore** (NoSQL alternative)
- **Cloud Spanner** (for global scale)

For **local development**, SQLite works fine (stored in a file).

See [DEPLOY_DATABASE.md](DEPLOY_DATABASE.md) for Cloud SQL setup instructions.

## Database Schema

### Tables

1. **transcripts** - Stores transcript file metadata
   - `id` - Primary key
   - `filename` - Name of the transcript file
   - `date` - Date of the transcript
   - `total_lines` - Total number of lines
   - `created_at` - Timestamp

2. **transcript_lines** - Stores individual lines
   - `id` - Primary key
   - `transcript_id` - Foreign key to transcripts
   - `line_number` - Line number in the transcript
   - `text` - Line content
   - `speaker` - Tagged speaker name (nullable)
   - `tagged_at` - When the line was tagged
   - `tagged_by` - Who tagged it

3. **speakers** - Reference table for speakers (optional)

## Loading Transcripts

### Local Development

1. **Set up database:**
   ```bash
   # SQLite (default for local dev)
   export DATABASE_URL=sqlite:///transcripts.db
   
   # Or PostgreSQL
   export DATABASE_URL=postgresql://user:password@localhost/transcripts
   ```

2. **Load transcripts:**
   ```bash
   # Linux/Mac
   python3 -m backend.load_transcripts
   
   # Windows PowerShell
   python -m backend.load_transcripts
   ```

   Or use the helper scripts:
   ```bash
   # Linux/Mac
   ./scripts/database/load_transcripts.sh
   
   # Windows
   .\scripts\database\load_transcripts.ps1
   ```

### Production (Cloud Run)

The transcripts should be loaded after deployment. You can:

1. **SSH into Cloud Run instance** (if enabled)
2. **Use Cloud SQL Proxy** to connect to database
3. **Run load script** via a one-time Cloud Run job

Or add an initialization endpoint that loads transcripts on first request (not recommended for production).

## Database Options

### SQLite (Default for Local)

- **Pros:** Simple, no setup needed, good for development
- **Cons:** Not suitable for production, limited concurrency
- **Use when:** Local development, testing

### PostgreSQL (Recommended for Production)

- **Pros:** Production-ready, handles concurrency, scalable
- **Cons:** Requires setup, more complex
- **Use when:** Cloud Run deployment, production use

**Setup PostgreSQL on Cloud SQL:**

```bash
# Create Cloud SQL instance
gcloud sql instances create transcript-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create transcripts --instance=transcript-db

# Set DATABASE_URL in Cloud Run
gcloud run services update transcript-tagger \
  --set-env-vars DATABASE_URL=postgresql://user:password@/transcripts?host=/cloudsql/PROJECT_ID:REGION:transcript-db \
  --add-cloudsql-instances=PROJECT_ID:REGION:transcript-db
```

## Environment Variables

- `DATABASE_URL` - Database connection string
  - SQLite: `sqlite:///transcripts.db`
  - PostgreSQL: `postgresql://user:password@host/database`

## API Endpoints

### Transcripts
- `GET /api/transcripts` - List all transcripts
- `GET /api/transcripts/<id>` - Get transcript details
- `GET /api/transcripts/<id>/lines` - Get lines (paginated)
- `GET /api/transcripts/<id>/stats` - Get statistics
- `GET /api/transcripts/<id>/speakers` - Get speakers for transcript
- `GET /api/transcripts/<id>/export` - Export transcript

### Tagging
- `PATCH /api/transcripts/<id>/lines/<line_id>` - Update single line
- `PATCH /api/transcripts/<id>/lines/bulk` - Bulk update lines

### Speakers
- `GET /api/speakers` - Get all speakers across all transcripts

## Backup and Restore

### Backup SQLite
```bash
cp transcripts.db transcripts.db.backup
```

### Backup PostgreSQL
```bash
pg_dump $DATABASE_URL > transcripts_backup.sql
```

### Restore
```bash
# SQLite
cp transcripts.db.backup transcripts.db

# PostgreSQL
psql $DATABASE_URL < transcripts_backup.sql
```

## Troubleshooting

### Database locked (SQLite)
- SQLite doesn't handle concurrent writes well
- Use PostgreSQL for production
- Or ensure only one process accesses the database

### Connection errors (PostgreSQL)
- Check DATABASE_URL format
- Verify Cloud SQL instance is running
- Check firewall rules
- Verify credentials

### Transcripts not loading
- Check file paths (12.7.txt, 12.8.txt, 12.10.txt, 12.12.txt)
- Verify file encoding (UTF-8)
- Check database permissions
- Review load script logs

