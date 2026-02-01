@echo off
REM Income Smoothing Platform - Quick Start Script (Windows)
REM This script starts both backend and frontend servers

echo.
echo Starting Income Smoothing Platform...
echo.

REM Start backend
echo Starting backend server on port 8000...
start "Backend Server" cmd /k "python -m uvicorn app.main:app --reload --port 8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend server on port 3000...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo Both servers are starting...
echo.
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend App: http://localhost:3000
echo.
echo Test Credentials:
echo   Email: testuser1@example.com
echo   Password: TestPass123
echo.
echo Close the terminal windows to stop the servers
echo.
pause
