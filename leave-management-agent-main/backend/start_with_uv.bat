@echo off
echo ========================================
echo Leave Management System - Starting with UV
echo ========================================
echo.

REM Check if uv is available
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: uv is not installed or not in PATH
    echo Install uv from: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/3] Syncing Python dependencies with uv...
uv sync

echo.
echo [2/3] Starting Flask API Server with uv on port 5000...
start "Leave Management API (UV)" cmd /k "uv run api_server.py"

timeout /t 3 >nul

echo.
echo [3/3] Starting React Frontend on port 5173...
cd frontend
start "Leave Management Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo Servers Starting!
echo ========================================
echo.
echo API Server:      http://localhost:5000
echo Frontend:        http://localhost:5173
echo.
echo Two new windows should open:
echo   1. API Server (Flask with UV)
echo   2. Frontend Server (Vite + React)
echo.
echo To stop the servers, close both windows or press Ctrl+C in each.
echo.
echo Waiting 5 seconds before opening browser...
timeout /t 5 >nul

REM Open browser
start http://localhost:5173

echo.
echo Browser opened. Enjoy!
echo.
pause
