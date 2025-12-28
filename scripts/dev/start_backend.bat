@echo off
REM Start only the Flask backend server

echo Starting Flask Backend Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.
    pause
    exit /b 1
)

REM Check if port 8080 is in use
netstat -ano | findstr :8080 >nul
if not errorlevel 1 (
    echo Warning: Port 8080 is already in use!
    echo.
    set /p response="Kill existing process and start new server? (y/n): "
    if /i "%response%"=="y" (
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
            taskkill /PID %%a /F >nul 2>&1
        )
        timeout /t 2 /nobreak >nul
    ) else (
        echo Exiting. Please stop the existing server first.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Starting Flask Backend
echo ========================================
echo.
echo Server will run on: http://localhost:8080
echo API endpoint: http://localhost:8080/api/transcripts
echo.
echo Press Ctrl+C to stop the server
echo.

python server.py

