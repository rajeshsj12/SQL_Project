@echo off
echo ========================================
echo    MySQL Database Manager - Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to your PATH
    pause
    exit /b 1
)

echo Python detected: 
python --version

REM Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Streamlit is not installed
    echo Please run setup.bat first to install dependencies
    echo.
    set /p choice="Do you want to install dependencies now? (y/n): "
    if /i "%choice%"=="y" (
        call setup.bat
        if errorlevel 1 (
            echo Failed to install dependencies
            pause
            exit /b 1
        )
    ) else (
        echo Please install dependencies manually and try again
        pause
        exit /b 1
    )
)

echo.
echo Checking MySQL connection requirements...
echo - Host: localhost
echo - Port: 3306
echo - Default Username: root
echo - Default Password: password
echo.
echo Make sure your MySQL server is running before proceeding!
echo.

set /p proceed="Press Enter to start the application (or Ctrl+C to cancel)..."

echo.
echo Starting MySQL Database Manager...
echo Application will be available at: http://localhost:5000
echo.
echo To stop the application, press Ctrl+C in this window
echo.

REM Start Streamlit application
streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true

echo.
echo Application stopped.
pause
