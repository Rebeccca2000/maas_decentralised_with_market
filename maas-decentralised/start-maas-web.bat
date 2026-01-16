@echo off
echo ========================================
echo  MaaS Decentralized Platform - Web Mode
echo ========================================
echo.

echo Checking dependencies...

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js v16+ from https://nodejs.org/
    pause
    exit /b 1
)

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org/
    pause
    exit /b 1
)

echo Dependencies OK!
echo.

echo Installing Node.js dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install Node.js dependencies
    pause
    exit /b 1
)

echo Installing Python dependencies...
call pip install -r backend/requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Starting MaaS Platform Services
echo ========================================
echo.
echo This will start:
echo  - Hardhat Blockchain Node (Port 8545)
echo  - Python Backend API (Port 5000)  
echo  - React Frontend (Port 3000)
echo.
echo Press Ctrl+C to stop all services
echo.

:: Start all services
call npm run dev-full
