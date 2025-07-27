@echo off
echo ========================================
echo   MySQL Database Manager - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7+ from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python detected: 
python --version
echo.

REM Check if pip is available
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with your Python installation
    pause
    exit /b 1
)

echo pip detected:
python -m pip --version
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing with current version
)
echo.

REM Install requirements
echo Installing Python dependencies...
echo This may take a few minutes...
echo.

python -m pip install streamlit pandas plotly sqlalchemy pymysql mysql-connector-python openpyxl xlsxwriter

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install some dependencies
    echo Please check your internet connection and try again
    echo.
    echo You can also try installing manually:
    echo   pip install streamlit pandas plotly sqlalchemy pymysql mysql-connector-python openpyxl xlsxwriter
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo          Setup Complete!
echo ========================================
echo.
echo All dependencies have been installed successfully.
echo.
echo Next steps:
echo 1. Make sure MySQL server is running on localhost:3306
echo 2. Ensure you have appropriate database credentials
echo 3. Run 'run.bat' to start the application
echo.
echo Default connection settings:
echo - Host: localhost
echo - Port: 3306  
echo - Username: root
echo - Password: password
echo.
echo You can modify these in the application interface.
echo.

pause
