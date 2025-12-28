# Scripts

This directory contains all operational scripts for development, deployment, and database management.

## Directory Structure

```
scripts/
├── dev/        # Development scripts
├── deploy/     # Deployment scripts
└── database/   # Database management scripts
```

## 🛠️ Development Scripts (`dev/`)

Scripts for local development and testing.

### Starting the Application

**Option 1: Start Both Servers (Recommended)**

```bash
# Windows CMD
scripts\dev\start_dev.bat

# Windows PowerShell
.\scripts\dev\start_dev.ps1

# Linux/Mac
./scripts/dev/start_dev.sh
```

Starts both backend (Flask) and frontend (React) servers concurrently.

**Option 2: Sequential Start**

```bash
# Windows CMD
scripts\dev\start_dev_sequential.bat
```

Starts servers one after another (useful if concurrent start fails).

### Backend Only

```bash
# Windows CMD
scripts\dev\start_backend.bat

# Windows PowerShell
.\scripts\dev\start_backend.ps1

# Manual
python server.py
```

### Restarting Backend

```bash
# Windows PowerShell
.\scripts\dev\restart_backend.ps1
```

Kills existing backend process and restarts it.

---

## 🚀 Deployment Scripts (`deploy/`)

Scripts for deploying to Google Cloud Run.

### Deploy Application

```bash
# Linux/Mac
./scripts/deploy/deploy.sh

# Windows PowerShell
.\scripts\deploy\deploy.ps1
```

**What it does:**
- Builds Docker image using Cloud Build
- Deploys to Cloud Run
- Connects to Cloud SQL database
- Sets up environment variables

**Prerequisites:**
- Google Cloud SDK installed and configured
- Project ID set: `export PROJECT_ID=your-project-id`
- Cloud SQL instance created

### Setup Cloud SQL

```bash
# Linux/Mac
./scripts/deploy/setup_cloud_sql.sh

# Windows PowerShell
.\scripts\deploy\setup_cloud_sql.ps1
```

**What it does:**
- Creates Cloud SQL PostgreSQL instance
- Creates database and user
- Configures connection settings
- Outputs connection details

📖 See [docs/DEPLOY.md](../docs/DEPLOY.md) for detailed deployment instructions.

---

## 💾 Database Scripts (`database/`)

Scripts for database operations and management.

### Load Transcripts

```bash
# Linux/Mac
./scripts/database/load_transcripts.sh

# Windows PowerShell
.\scripts\database\load_transcripts.ps1
```

Loads transcript files (12.7.txt, 12.8.txt, etc.) into the database.

### Connect to Database

```bash
# Linux/Mac
./scripts/database/connect_database.sh

# Windows PowerShell
.\scripts\database\connect_database.ps1
```

Opens an interactive SQL connection to the database (local SQLite or Cloud SQL).

### Sync Database

```bash
# Windows PowerShell
.\scripts\database\sync_db.ps1
```

Syncs data between local and cloud databases. Wrapper around `agent/sync_database.py`.

### Update Environment Variables

```bash
# Windows PowerShell
.\scripts\database\update_env.ps1
```

Updates `.env` file with database connection details.

📖 See [docs/DATABASE_CONNECTION.md](../docs/DATABASE_CONNECTION.md) for database management guide.

---

## Quick Reference

| Task | Script | Platform |
|------|--------|----------|
| **Start Dev (Both)** | `scripts/dev/start_dev.*` | All |
| **Start Backend** | `scripts/dev/start_backend.*` | All |
| **Restart Backend** | `scripts/dev/restart_backend.ps1` | Windows |
| **Deploy App** | `scripts/deploy/deploy.*` | All |
| **Setup Cloud SQL** | `scripts/deploy/setup_cloud_sql.*` | All |
| **Load Transcripts** | `scripts/database/load_transcripts.*` | All |
| **Connect DB** | `scripts/database/connect_database.*` | All |
| **Sync DB** | `scripts/database/sync_db.ps1` | Windows |
| **Update Env** | `scripts/database/update_env.ps1` | Windows |

## Platform Notes

- **`.bat`** - Windows Command Prompt
- **`.ps1`** - Windows PowerShell
- **`.sh`** - Linux/Mac/WSL (requires `chmod +x`)

## Environment Variables

Most scripts support environment variables:

```bash
# Common variables
PROJECT_ID=your-gcp-project-id
DATABASE_URL=postgresql://user:pass@host/db
DB_TYPE=sqlite  # or postgresql

# For local development
export DB_TYPE=sqlite  # Linux/Mac
$env:DB_TYPE = "sqlite"  # PowerShell
```

📖 See [docs/README_ENV.md](../docs/README_ENV.md) for all environment variables.

## Troubleshooting

### Scripts Won't Execute (Linux/Mac)

Make scripts executable:
```bash
chmod +x scripts/dev/*.sh
chmod +x scripts/deploy/*.sh
chmod +x scripts/database/*.sh
```

### PowerShell Execution Policy Error

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use

```bash
# Find process on port 8080
netstat -ano | findstr :8080  # Windows
lsof -ti:8080  # Linux/Mac

# Kill process
taskkill /PID <PID> /F  # Windows
kill -9 <PID>  # Linux/Mac
```

📖 See [docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) for more solutions.

---

## Related Documentation

- [Quick Start Guide](../docs/QUICK_START.md) - Get started in 5 minutes
- [Local Development](../docs/LOCAL_DEVELOPMENT.md) - Development workflow
- [Deployment Guide](../docs/DEPLOY.md) - Cloud deployment
- [Database Setup](../docs/README_DATABASE.md) - Database schema and setup
- [Agent Tools](../agent/README.md) - ML and automation tools

---

## Navigation

- [Back to Main README](../README.md)
- [Documentation Index](../docs/INDEX.md)
- [Agent Tools](../agent/README.md)

