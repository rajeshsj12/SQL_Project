@echo off
echo ==========================================
echo PostgreSQL Database Manager Setup (Windows)
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python found
python --version

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    echo Please install pip or reinstall Python with pip included
    pause
    exit /b 1
)

echo ✓ pip found

REM Install required packages
echo.
echo Installing required Python packages...
echo ==========================================

pip install streamlit
if errorlevel 1 (
    echo ERROR: Failed to install streamlit
    pause
    exit /b 1
)

pip install psycopg2-binary
if errorlevel 1 (
    echo ERROR: Failed to install psycopg2-binary
    pause
    exit /b 1
)

pip install pandas
if errorlevel 1 (
    echo ERROR: Failed to install pandas
    pause
    exit /b 1
)

pip install plotly
if errorlevel 1 (
    echo ERROR: Failed to install plotly
    pause
    exit /b 1
)

pip install sqlalchemy
if errorlevel 1 (
    echo ERROR: Failed to install sqlalchemy
    pause
    exit /b 1
)

echo.
echo ==========================================
echo ✓ All packages installed successfully!
echo ==========================================
echo.

REM Check if PostgreSQL client tools are available (optional)
psql --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: PostgreSQL client tools (psql) not found in PATH
    echo This is optional but recommended for advanced database operations
    echo You can install PostgreSQL client from: https://www.postgresql.org/download/windows/
) else (
    echo ✓ PostgreSQL client tools found
    psql --version
)

echo.
echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo Next steps:
echo 1. Make sure your PostgreSQL server is running
echo 2. Run the application using: run.bat
echo 3. The application will open in your default web browser
echo.
echo Default connection settings:
echo - Host: localhost
echo - Port: 5432
echo - Username: postgres
echo - Password: password
echo.
echo You can modify these defaults by setting environment variables:
echo - PGHOST (default: localhost)
echo - PGPORT (default: 5432)
echo - PGUSER (default: postgres)
echo - PGPASSWORD (default: password)
echo.

pause
