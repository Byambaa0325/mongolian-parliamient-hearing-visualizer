# Quick Start Guide

## Start Development Servers

### Option 1: Both Servers Together (Easiest)

**Windows PowerShell:**
```powershell
.\scripts\dev\start_dev.ps1
```

**Windows CMD:**
```cmd
scripts\dev\start_dev.bat
```

**Or using npm:**
```bash
npm run start:dev
```

### Option 2: Separate Terminals

**Terminal 1 - Backend (Flask):**
```powershell
# Windows
.\scripts\dev\start_backend.ps1

# Or manually
python server.py
```

**Terminal 2 - Frontend (React):**
```bash
npm start
```

## Verify Everything is Working

1. **Backend should show:**
   ```
   * Running on http://127.0.0.1:8080
   ```

2. **Frontend should show:**
   ```
   Compiled successfully!
   Local: http://localhost:3000
   ```

3. **Open browser:** http://localhost:3000
   - You should see 4 transcripts
   - No proxy errors
   - Can select and tag transcripts

## Troubleshooting

### Proxy Errors (ECONNREFUSED)

**Problem:** Frontend can't connect to backend

**Solution:**
1. Make sure backend is running on port 8080
2. Check: `netstat -ano | findstr :8080` (should show LISTENING)
3. Test backend: Open http://localhost:8080/api/transcripts in browser
4. Restart backend if needed

### 500 Internal Server Error

**Problem:** Backend is running but returning errors

**Solution:**
1. Check backend terminal for error messages
2. Make sure database is initialized: `python agent/setup_local_db.py`
3. Restart backend server

### Port Already in Use

**Problem:** Port 8080 is already taken

**Solution:**
```powershell
# Find process using port 8080
netstat -ano | findstr :8080

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

## Next Steps

Once both servers are running:
1. Open http://localhost:3000
2. Select a transcript
3. Start tagging speakers!

