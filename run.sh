#!/bin/bash

# Link Locator URL Shortener - Quick Start Script (macOS/Linux)

echo ""
echo "======================================"
echo "    Link Locator - Quick Start"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

echo "[1/4] Checking if virtual environment exists..."
if [ ! -d "venv" ]; then
    echo "[2/4] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
else
    echo "[2/4] Virtual environment already exists"
fi

echo "[3/4] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

echo "[4/4] Installing dependencies..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "======================================"
echo "    Starting Link Locator Server..."
echo "======================================"
echo ""
echo "Dashboard: http://localhost:5000/dashboard"
echo "API: http://localhost:5000/api"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
