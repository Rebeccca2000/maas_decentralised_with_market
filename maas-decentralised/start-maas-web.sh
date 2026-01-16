#!/bin/bash

echo "========================================"
echo " MaaS Decentralized Platform - Web Mode"
echo "========================================"
echo

echo "Checking dependencies..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js v16+ from https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://python.org/"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo "Dependencies OK!"
echo

echo "Installing Node.js dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Node.js dependencies"
    exit 1
fi

echo "Installing Python dependencies..."
$PYTHON_CMD -m pip install -r backend/requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies"
    exit 1
fi

echo
echo "========================================"
echo " Starting MaaS Platform Services"
echo "========================================"
echo
echo "This will start:"
echo " - Hardhat Blockchain Node (Port 8545)"
echo " - Python Backend API (Port 5000)"
echo " - React Frontend (Port 3000)"
echo
echo "Press Ctrl+C to stop all services"
echo

# Start all services
npm run dev-full
