@echo off
echo Starting backend server...
start /B python server.py
timeout /t 3 /nobreak > nul
echo Backend should be ready, starting frontend...
npm start

