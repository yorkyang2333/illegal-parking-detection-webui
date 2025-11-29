@echo off
echo ========================================
echo   Vehicle Parking Violation Detection
echo   Starting Application...
echo ========================================

where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Node.js not installed
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python not installed
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

cd backend

if not exist .env (
    echo Error: .env file not found in backend directory
    echo Please create a .env file with your DASHSCOPE_API_KEY
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Python dependencies installed
) else (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

echo [2/4] Starting Flask backend...
start "Flask Backend (Port 5001)" python app.py
timeout /t 3 >nul
echo [OK] Backend started

cd ..\frontend

echo [3/4] Installing Node.js dependencies...
call npm install >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Node.js dependencies installed
) else (
    echo [ERROR] Failed to install Node.js dependencies
    pause
    exit /b 1
)

echo [4/4] Starting Vite dev server...
start "Vite Frontend (Port 3000)" npm run dev
timeout /t 3 >nul
echo [OK] Frontend started

echo ========================================
echo Application started successfully!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:5001
echo.
echo Close terminal windows to stop servers
pause
