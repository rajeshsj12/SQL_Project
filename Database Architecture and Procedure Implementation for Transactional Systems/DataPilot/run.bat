@echo off
echo ========================================
echo    DATABASE EXPLORER - QUICK LAUNCH
echo ========================================
echo.

echo Starting Database Explorer...
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py --server.port 5000

pause