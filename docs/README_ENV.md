# Environment Variables Guide

## Overview

This project uses environment variables for configuration. You can set them via:
1. `.env` file (for local development)
2. Environment variables (for Cloud Run)
3. System environment variables

## Environment Variables

All environment variables are defined in `.env` file. See the file for detailed comments.

### `DATABASE_URL`

Database connection string.

**Local Development (SQLite - default):**
```bash
# No need to set - defaults to SQLite
# Or explicitly:
DATABASE_URL=sqlite:///transcripts.db
```

**Local PostgreSQL:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/transcripts
```

**Cloud SQL (Cloud Run):**
```bash
DATABASE_URL=postgresql://user:password@localhost/transcripts?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME
```

### `PORT`

Server port (optional).

- **Cloud Run**: Automatically set by Cloud Run
- **Local dev**: Defaults to 8080
- **Override**: `PORT=3000`

### `REACT_APP_API_URL`

API base URL for React app (optional).

- **Default**: `/api` (same origin)
- **Separate backend**: `http://localhost:8080/api`
- **Production**: Usually not needed (same origin)

## Setup

### 1. Copy Example File

```bash
# Copy the example file
cp .env.example .env
```

### 2. Edit .env File

Open `.env` and uncomment/modify variables as needed:

```bash
# For local SQLite (default - no changes needed)
# DATABASE_URL=sqlite:///transcripts.db

# For local PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/transcripts
```

### 3. Load Variables

The app automatically loads `.env` file using `python-dotenv`.

**For Python/Flask:**
- Automatically loaded on import
- No additional setup needed

**For React:**
- Variables prefixed with `REACT_APP_` are available
- Must restart dev server after changes

## Local Development

### Option 1: Use .env File (Recommended)

1. Copy `.env.example` to `.env`
2. Edit `.env` with your settings
3. Run the app - variables are loaded automatically

### Option 2: Set Environment Variables

**Linux/Mac:**
```bash
export DATABASE_URL=sqlite:///transcripts.db
export PORT=8080
npm start
```

**Windows PowerShell:**
```powershell
$env:DATABASE_URL = "sqlite:///transcripts.db"
$env:PORT = "8080"
npm start
```

**Windows CMD:**
```cmd
set DATABASE_URL=sqlite:///transcripts.db
set PORT=8080
npm start
```

## Cloud Run Deployment

Environment variables are set via `gcloud`:

```bash
gcloud run services update transcript-tagger \
  --set-env-vars DATABASE_URL="postgresql://..." \
  --region us-central1
```

Or in `cloudbuild.yaml`:
```yaml
- '--set-env-vars'
- 'DATABASE_URL=${_DATABASE_URL}'
```

## Security

### ⚠️ Never Commit .env Files

- `.env` is in `.gitignore`
- `.env.example` is safe to commit (no secrets)
- Use `.env.example` as a template

### Secrets Management

For production, use **Google Secret Manager**:

```bash
# Store secret
echo -n "your-password" | gcloud secrets create db-password --data-file=-

# Reference in Cloud Run
gcloud run services update transcript-tagger \
  --update-secrets DATABASE_URL=db-password:latest
```

## Troubleshooting

### Variables Not Loading

1. **Check file location**: `.env` should be in project root
2. **Check syntax**: No spaces around `=`
3. **Restart server**: Changes require restart
4. **Check .gitignore**: Make sure `.env` isn't ignored incorrectly

### React Variables Not Working

- Must be prefixed with `REACT_APP_`
- Must restart dev server after changes
- Only available at build time (not runtime)

### Database Connection Issues

- Verify `DATABASE_URL` format
- Check database is running (for PostgreSQL)
- Verify credentials
- Check network/firewall rules

## Example .env Files

### Minimal (SQLite)
```bash
# Uses default SQLite - no variables needed
```

### Local PostgreSQL
```bash
DATABASE_URL=postgresql://transcript_user:mypassword@localhost:5432/transcripts
PORT=8080
```

### Cloud SQL
```bash
DATABASE_URL=postgresql://transcript_user:password@localhost/transcripts?host=/cloudsql/myproject:us-central1:transcript-db
```

### Development with Separate Backend
```bash
DATABASE_URL=sqlite:///transcripts.db
REACT_APP_API_URL=http://localhost:8080/api
```

