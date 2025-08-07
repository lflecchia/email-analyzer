#!/bin/bash

# Email Space Analyzer - Linux/Mac Launcher

clear
echo "================================================"
echo "      📧 EMAIL SPACE ANALYZER"
echo "================================================"
echo

echo "Starting application..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found! Please install Python 3.8+ from https://python.org"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Show Python version
echo "✅ Python found:"
python3 --version

# Check if required packages are installed
echo
echo "📦 Checking dependencies..."
python3 -c "import flask, pandas, msal, requests" &> /dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required packages..."
    echo "This may take a few minutes..."
    
    # Install from requirements.txt if it exists, otherwise install manually
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    else
        pip3 install flask flask-cors pandas msal requests google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
    fi
    
    if [ $? -ne 0 ]; then
        echo
        echo "❌ Failed to install packages. Please try:"
        echo "pip3 install -r requirements.txt"
        echo
        echo "Or manually:"
        echo "pip3 install flask flask-cors pandas msal requests google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
        echo
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "✅ Dependencies ready!"
echo

# Check if frontend file exists
if [ ! -f "index.html" ]; then
    echo "⚠️  Warning: index.html not found in current directory"
    echo "The web interface may not work properly"
    echo "Please ensure index.html is in the same folder as this script"
    echo
fi

echo "🚀 Starting Email Space Analyzer..."
echo "📁 Data will be saved in: $(pwd)/data"
echo "🌐 Web interface will open automatically"
echo
echo "⚙️  Configuration:"
echo "   - Max emails per account: 5000 (configurable in web interface)"
echo "   - Resume mode: Enabled by default"
echo "   - Supported providers: Outlook, Gmail"
echo
echo "🛑 Press Ctrl+C to stop"
echo

# Make script executable if not already
chmod +x "$0"

# Create data directory if it doesn't exist
mkdir -p data/cache data/exports

# Start the Python backend server
python3 email_analyzer_backend.py

echo
echo "👋 Email Space Analyzer stopped"ne 0 ]; then
        echo "❌ Failed to install packages. Please run:"
        echo "pip3 install flask flask-cors pandas msal requests google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "✅ Dependencies ready!"
echo
echo "🚀 Starting Email Space Analyzer..."
echo "📁 Data will be saved in: $(pwd)/data"
echo "🌐 Web interface will open automatically"
echo
echo "🛑 Press Ctrl+C to stop"
echo

# Make script executable if not already
chmod +x "$0"

# Start the Python backend server
python3 email_analyzer_backend.py

echo
echo "👋 Email Space Analyzer stopped"