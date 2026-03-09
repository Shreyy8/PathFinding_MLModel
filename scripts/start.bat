@echo off
REM Full Stack Startup Script for Windows
REM Starts both backend (Python Flask) and frontend (Next.js)

echo.
echo Starting Interactive Road Mapping Interface
echo ==============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js not found. Please install Node.js 18+
    exit /b 1
)

REM Start backend server
echo Starting Backend Server (Python Flask)...
echo    URL: http://localhost:5000
start "Backend Server" cmd /k python run_server.py
timeout /t 3 /nobreak >nul
echo.

REM Navigate to frontend directory
cd frontend

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing frontend dependencies...
    call npm install
    echo.
)

REM Start frontend server
echo Starting Frontend Server (Next.js)...
echo    URL: http://localhost:3000
start "Frontend Server" cmd /k npm run dev
echo.

echo Both servers started successfully!
echo.
echo Access the application at: http://localhost:3000
echo Backend API available at: http://localhost:5000/api
echo.
echo Close the terminal windows to stop the servers
echo.

pause
