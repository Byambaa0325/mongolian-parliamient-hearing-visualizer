# Troubleshooting Connection Issues

## Problem: Frontend can't connect to backend (ECONNREFUSED)

### Symptoms
- Backend shows "Running on http://127.0.0.1:8080"
- Frontend shows "Proxy error: Could not proxy request... ECONNREFUSED"
- Backend API works when tested directly

### Common Causes

#### 1. IPv6/IPv4 Address Mismatch (Windows)
**Error**: `Proxy error: connect ECONNREFUSED ::1:8080`

This happens when Node.js tries to use IPv6 (`::1`) but Flask is listening on IPv4 (`127.0.0.1`).

**Solution**: The project uses `src/setupProxy.js` which forces IPv4 by targeting `127.0.0.1` instead of `localhost`.

**Technical Details**:
- Flask backend listens on `127.0.0.1:8080` (IPv4 only)
- Node.js may try to connect via `localhost` which resolves to `::1` (IPv6) on some Windows systems
- The manual proxy configuration in `src/setupProxy.js` explicitly uses `127.0.0.1` to force IPv4

If you're still seeing this error:
1. Make sure you have the latest code with `src/setupProxy.js`
2. Verify the proxy setup by checking the startup logs for `[HPM] Proxy created: /api -> http://127.0.0.1:8080`
3. Restart both servers with `npm run start:dev`

#### 2. Frontend Started Before Backend
The React dev server proxy tries to connect before Flask is ready.

**Solution**: Use the provided start script which includes a 3-second delay:
```powershell
npm run start:dev
```

Or use the sequential batch file:
```cmd
start_dev_sequential.bat
```

### Solution

**The React dev server needs to be restarted** to pick up the proxy configuration.

#### Option 1: Restart Both Servers
1. Stop both servers (Ctrl+C in both terminals)
2. Start them again:
   ```powershell
   .\start_dev.ps1
   ```

#### Option 2: Restart Only Frontend
1. Stop the React dev server (Ctrl+C in the frontend terminal)
2. Start it again:
   ```powershell
   npm start
   ```
   (Keep the backend running)

#### Option 3: Manual Start
1. **Terminal 1 - Backend:**
   ```powershell
   python server.py
   ```
   Wait until you see: `Running on http://127.0.0.1:8080`

2. **Terminal 2 - Frontend:**
   ```powershell
   npm start
   ```

### Verify It's Working

1. **Check backend is running:**
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:8080/api/transcripts" -UseBasicParsing
   ```
   Should return Status 200

2. **Check frontend:**
   - Open http://localhost:3000
   - Should see 4 transcript cards
   - No proxy errors in console

### Why This Happens

The React dev server's proxy configuration is only read when it starts. If you:
- Start the frontend before the backend
- Change the proxy config in `package.json`
- Start them in the wrong order

The proxy won't work until you restart the React dev server.

### Still Not Working?

1. **Check ports:**
   ```powershell
   netstat -ano | findstr :8080
   netstat -ano | findstr :3000
   ```

2. **Check backend logs:**
   - Look for errors in the backend terminal
   - Should see: `Database initialized successfully`

3. **Clear browser cache:**
   - Hard refresh: Ctrl+Shift+R
   - Or clear cache and reload

4. **Check firewall:**
   - Windows Firewall might be blocking localhost connections
   - Try disabling temporarily to test

