@echo off
REM Link Locator URL Shortener - Quick Start Script (Windows)

echo.
echo ======================================
echo    Link Locator - Quick Start
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Checking if virtual environment exists...
if not exist "venv" (
    echo [2/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo [2/4] Virtual environment already exists
)

echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

echo [4/4] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ======================================
echo    Starting Link Locator Server...
echo ======================================
echo.
echo Dashboard: http://localhost:5000/dashboard
echo API: http://localhost:5000/api
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
