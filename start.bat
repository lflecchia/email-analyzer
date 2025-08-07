@echo off
title Email Space Analyzer

echo.
echo ================================================
echo      📧 EMAIL SPACE ANALYZER
echo ================================================
echo.
echo Starting application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ from https://python.org
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Show Python version
echo ✅ Python found:
python --version

REM Check if required packages are installed
echo.
echo 📦 Checking dependencies...
python -c "import flask, pandas, msal, requests" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing required packages...
    echo This may take a few minutes...
    
    REM Install from requirements.txt if it exists, otherwise install manually
    if exist requirements.txt (
        pip install -r requirements.txt
    ) else (
        pip install flask flask-cors pandas msal requests google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
    )
    
    if errorlevel 1 (
        echo.
        echo ❌ Failed to install packages. Please try:
        echo pip install -r requirements.txt
        echo.
        echo Or manually:
        echo pip install flask flask-cors pandas msal requests google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
        echo.
        pause
        exit /b 1
    )
)

echo ✅ Dependencies ready!
echo.

REM Check if frontend file exists
if not exist index.html (
    echo ⚠️  Warning: index.html not found in current directory
    echo The web interface may not work properly
    echo Please ensure index.html is in the same folder as this script
    echo.
)

echo 🚀 Starting Email Space Analyzer...
echo 📁 Data will be saved in: %cd%\data
echo 🌐 Web interface will open automatically
echo.
echo ⚙️  Configuration:
echo    - Max emails per account: 5000 (configurable in web interface)
echo    - Resume mode: Enabled by default
echo    - Supported providers: Outlook, Gmail
echo.
echo 🛑 Press Ctrl+C to stop
echo.

REM Create data directory if it doesn't exist
if not exist data mkdir data
if not exist data\cache mkdir data\cache
if not exist data\exports mkdir data\exports

REM Start the Python backend server
python email_analyzer_backend.py

echo.
echo 👋 Email Space Analyzer stopped
pause