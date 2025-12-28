# Local Development Guide

## Quick Start

### Option 1: Run Both Servers Together (Recommended)

**Windows:**
```cmd
scripts\dev\start_dev.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/dev/start_dev.sh
./scripts/dev/start_dev.sh
```

Or using npm:
```bash
npm install  # Install dependencies including concurrently
npm run start:dev
```

This will start:
- **Backend (Flask)**: http://localhost:8080
- **Frontend (React)**: http://localhost:3000

### Option 2: Run Servers Separately

**Terminal 1 - Backend:**

**Windows:**
```powershell
.\scripts\dev\start_backend.ps1
# or
scripts\dev\start_backend.bat
```

**Linux/Mac:**
```bash
python server.py
# or
python3 server.py
```

**Terminal 2 - Frontend:**
```bash
npm start
```

**Note:** The `npm run start:dev` command includes a startup delay to ensure the backend is ready before the frontend connects.

## Setup

### 1. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
npm install
```

### 2. Configure Database

For local development, SQLite is used by default (no setup needed).

If you want to use PostgreSQL:
```bash
# Update .env file
DATABASE_URL=postgresql://user:password@localhost:5432/transcripts
```

### 3. Initialize Database

**Quick setup (recommended):**
```bash
python agent/setup_local_db.py
```

This will:
- Create the database schema
- Load all 4 transcript files (12.7.txt, 12.8.txt, 12.10.txt, 12.12.txt)

**Manual setup:**
```bash
# Create database schema
python3 -c "from backend.api import app; app.app_context().push(); from backend.database import db; db.create_all(); print('Schema created')"

# Load transcripts
python3 -m backend.load_transcripts
```

## Troubleshooting

### Error: "Unexpected token '<', "<!DOCTYPE "... is not valid JSON"

**Problem**: The React app is trying to fetch from the API, but the Flask backend isn't running.

**Solution**:
1. Make sure the Flask backend is running on port 8080
2. The proxy is configured in `src/setupProxy.js` (uses IPv4 `127.0.0.1`)
3. Restart both servers with `npm run start:dev`

**Note**: The start script includes a 3-second delay to ensure the backend is ready before the frontend starts.

### Backend Not Starting

**Check**:
- Python is installed: `python --version`
- Dependencies installed: `pip install -r requirements.txt`
- Port 8080 is available: `netstat -an | findstr 8080` (Windows) or `lsof -i :8080` (Mac/Linux)

### Frontend Not Starting

**Check**:
- Node.js is installed: `node --version`
- Dependencies installed: `npm install`
- Port 3000 is available

### API Requests Failing

**Check**:
1. Backend is running: Visit http://localhost:8080/api/transcripts
2. Proxy is configured in `package.json`
3. No CORS errors in browser console
4. Backend logs show requests coming in

### Database Connection Issues

**For SQLite (default)**:
- No setup needed
- Database file will be created at `transcripts.db`

**For PostgreSQL**:
- Make sure PostgreSQL is running
- Check DATABASE_URL in `.env` file
- Verify credentials are correct

## Development Workflow

1. **Start both servers**: `npm run start:dev` or use the scripts
2. **Make changes**: Edit files in `src/` (React) or `backend/` (Flask)
3. **Hot reload**: Both servers support hot reload
4. **Check logs**: 
   - Backend logs in terminal running Flask
   - Frontend logs in terminal running React
   - Browser console for frontend errors

## API Endpoints

When backend is running, test these:

- http://localhost:8080/api/transcripts - List transcripts
- http://localhost:8080/api/transcripts/1 - Get transcript details
- http://localhost:8080/api/transcripts/1/lines - Get transcript lines

## Environment Variables

Create a `.env` file for local development:

```bash
# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///transcripts.db

# Server port (optional - defaults to 8080)
PORT=8080

# React API URL (optional - uses proxy by default)
REACT_APP_API_URL=/api
```

## Ports

- **Backend (Flask)**: 8080
- **Frontend (React)**: 3000
- **Database (PostgreSQL)**: 5432 (if using PostgreSQL)

To change ports:
- Backend: Set `PORT` environment variable or edit `server.py`
- Frontend: React Scripts will prompt to use a different port if 3000 is taken

