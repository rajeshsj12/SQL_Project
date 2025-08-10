@echo off
echo ==========================================
echo PostgreSQL Database Manager
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run setup.bat first to install dependencies
    pause
    exit /b 1
)

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Streamlit is not installed
    echo Please run setup.bat first to install dependencies
    pause
    exit /b 1
)

echo ✓ Starting PostgreSQL Database Manager...
echo.
echo The application will open in your default web browser
echo If it doesn't open automatically, go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the application
echo ==========================================
echo.

REM Start the Streamlit application
streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true

pause
