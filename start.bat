@echo off
echo Starting InhaleEase Application Environment...

rem Step 1: Start MongoDB Service
echo [1/3] Ensuring MongoDB is running...
net start MongoDB 2>nul || echo MongoDB already running or requires Admin privileges...

rem Step 2: Start Backend Server
echo [2/3] Starting Backend Server on port 5000...
start cmd /k "cd /d %~dp0..\backend && node server.js"

rem Step 3: Start Frontend Server
echo [3/3] Starting Frontend Server on port 3001...
start cmd /k "cd /d %~dp0 && python -m http.server 3001"

echo.
echo Application successfully launched!
echo Launching your browser to http://localhost:3001
ping 127.0.0.1 -n 4 >nul
start http://localhost:3001
