@echo off
REM Start both backend and frontend for development

echo ========================================
echo Starting Development Servers
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.
    pause
    exit /b 1
)
python --version

REM Check if Node is available
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js not found. Please install Node.js.
    pause
    exit /b 1
)
node --version
echo.

REM Check if dependencies are installed
if not exist node_modules (
    echo Installing npm dependencies...
    call npm install
    if errorlevel 1 (
        echo Error: Failed to install npm dependencies
        pause
        exit /b 1
    )
)

REM Check Python dependencies
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install Python dependencies
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Starting Servers
echo ========================================
echo.
echo Backend (Flask):  http://localhost:8080
echo Frontend (React): http://localhost:3000
echo.
echo Press Ctrl+C in this window to stop both servers
echo.

REM Start backend in new window
start "Flask Backend - Port 8080" cmd /k "python server.py"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend (this will block)
echo Starting React frontend...
echo.
call npm start

REM If we get here, frontend stopped - cleanup
echo.
echo Stopping servers...
taskkill /FI "WINDOWTITLE eq Flask Backend - Port 8080*" /T /F >nul 2>&1
echo Servers stopped.
pause

