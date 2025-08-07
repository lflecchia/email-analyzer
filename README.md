# 📧 Email Space Analyzer

**Discover who's filling up your inbox and reclaim your email space.**

A powerful, user-friendly web application that analyzes your Outlook and Gmail accounts to help you understand email usage patterns, identify space-consuming senders, and optimize your email storage.

![Email Space Analyzer](https://img.shields.io/badge/Email-Space%20Analyzer-orange?style=for-the-badge&logo=gmail)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## ✨ New Features (v2.0)

### 🔐 **Real Authentication System**
- **Microsoft OAuth2**: Secure device code flow for Outlook accounts
- **Google OAuth2**: Full credentials setup with step-by-step guide
- **Multi-Account Support**: Connect multiple accounts per provider
- **Account Management**: Add, remove, and refresh accounts individually

### ⚙️ **Advanced Configuration**
- **Email Limits**: Configure max emails per account (100 - 100,000)
- **Resume Mode**: Continue from where you left off or start fresh
- **Account Identification**: Each email tagged with source account
- **Enhanced Size Detection**: Improved Outlook email size calculation

### 📊 **Better Analytics**
- **Per-Account Analysis**: See which accounts consume most space
- **Individual Account Charts**: Separate visualizations per account
- **Improved Size Accuracy**: Better estimation algorithms for Outlook
- **Export Enhancement**: Separate files per provider for Power BI

## 🚀 Quick Start

### **Option 1: One-Click Launch (Recommended)**

1. **Download** all project files to a folder
2. **Double-click** `start.bat` (Windows) or `start.sh` (Mac/Linux)
3. **Wait** for automatic setup and browser opening
4. **Follow the setup guides** for your email providers

### **Option 2: Manual Setup**

```bash
# Clone or download the project
git clone https://github.com/your-username/email-space-analyzer.git
cd email-space-analyzer

# Install dependencies
pip install -r requirements.txt

# Start the application
python email_analyzer_backend.py
```

## 📁 Project Files

```
email-space-analyzer/
├── 📄 index.html                    # Web interface (save this file)
├── 🐍 email_analyzer_backend.py     # Python API server (save this file)
├── 📋 requirements.txt               # Python dependencies (save this file)
├── 🚀 start.bat                     # Windows launcher (save this file)
├── 🚀 start.sh                      # Linux/Mac launcher (save this file)
├── 📖 README.md                     # This documentation
├── 📊 data/                         # Created automatically
│   ├── cache/                       # Authentication tokens & account data
│   └── exports/                     # Analysis results & CSV exports
└── 🔧 gmail_credentials.json        # Gmail API credentials (you create)
```

## 🔑 Email Provider Setup

### **Microsoft Outlook** ✅ *Works Immediately*

1. **Click "Add Account"** in the Outlook section
2. **Follow the authentication guide** in the modal
3. **Open the verification URL** in your browser
4. **Enter the device code** shown in the app
5. **Sign in** with your Microsoft account
6. **Done!** Your account is connected

**Supported Account Types:**
- Personal: @outlook.com, @hotmail.com, @live.com
- Microsoft 365: Work/school (may require admin approval)

### **Gmail** 📧 *Requires Google Cloud Setup*

#### **Step 1: Google Cloud Console Setup**

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create new project**: Click "New Project" → Name it "Email Analyzer"
3. **Enable Gmail API**: 
   - "APIs & Services" → "Library"
   - Search "Gmail API" → Enable
4. **Create OAuth Credentials**:
   - "APIs & Services" → "Credentials" 
   - "Create Credentials" → "OAuth 2.0 Client ID"
   - **Configure consent screen** if prompted:
     - User Type: External
     - App name: "Email Space Analyzer"
     - Add your email as test user
   - Application type: **Desktop application**
   - Name: "Email Analyzer Desktop"
   - Click **Create**

#### **Step 2: Download & Upload Credentials**

1. **Download JSON file** from Google Cloud Console
2. **In the app**: Click "Add Account" in Gmail section
3. **Upload the JSON file** using the file picker
4. **Click "Start Authentication"**
5. **Complete OAuth flow** in browser
6. **Return to app** - account will be connected

## 📊 Using the Application

### **Analysis Configuration**
- **Max Emails**: Set how many recent emails to analyze per account
- **Resume Mode**: ✅ Continue from existing data, ❌ Start fresh
- **Multiple Accounts**: Connect multiple accounts per provider

### **Running Analysis**
1. **Connect at least one account** (Outlook or Gmail)
2. **Configure settings** (max emails, resume mode)
3. **Click "Analyze My Emails"** 
4. **Monitor progress** with real-time updates
5. **View interactive dashboard** when complete

### **Dashboard Features**

#### **📈 Key Statistics**
- **Total Emails**: Count across all connected accounts
- **Storage Used**: Combined space consumption
- **Average Size**: Mean email size for optimization
- **Largest Email**: Biggest space consumer

#### **📊 Interactive Charts**
- **Top Senders (Volume)**: Most frequent emailers
- **Top Senders (Space)**: Biggest storage consumers
- **Account Distribution**: Space usage per account
- **Timeline Trends**: Email patterns over 12 months

#### **💾 Export Options**
- **Combined CSV**: All accounts in one file
- **Per-Provider CSV**: Separate Outlook/Gmail files
- **Power BI Ready**: Optimized column structure

## 📋 Data Structure

### **CSV Export Columns**
```csv
from_name,from_email,receivedDateTime,hasAttachments,size_bytes,subject,provider,account_id,account_email
John Doe,john@company.com,2024-01-15T09:30:00Z,true,1024576,Project Update,outlook,abc123,user@outlook.com
Jane Smith,jane@gmail.com,2024-01-15T10:15:00Z,false,2048,Meeting Notes,gmail,def456,user@gmail.com
```

### **Key Improvements**
- **account_id**: Unique identifier for each connected account
- **account_email**: Source account email address
- **Enhanced size_bytes**: Better accuracy for Outlook emails
- **Provider tracking**: Clear distinction between email sources

## 🔧 Advanced Features

### **Multi-Account Management**
- **Add Multiple**: Connect several accounts per provider
- **Individual Control**: Remove or refresh specific accounts
- **Account Stats**: See email count and last sync per account
- **Separate Analysis**: Data tagged by source account

### **Resume Functionality**
- **Smart Resume**: Automatically continues from last analysis
- **Fresh Start**: Option to restart and overwrite existing data
- **Per-Account Resume**: Continues from last email per account
- **Progress Tracking**: Visual indication of resume vs new data

### **Enhanced Size Detection**
- **Extended Properties**: Uses Outlook's native size fields
- **Header Analysis**: Falls back to Content-Length headers
- **Content Estimation**: Intelligent size estimation when unavailable
- **Attachment Detection**: Accounts for attachment overhead

## 🚨 Troubleshooting

### **Common Issues**

#### **"Python not found"**
- **Install Python 3.8+** from [python.org](https://python.org)
- **Windows**: Check "Add Python to PATH" during installation
- **Mac/Linux**: Use `python3` command

#### **"Package installation failed"**
```bash
# Try updating pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

#### **"Gmail credentials not found"**
1. **Download credentials** from Google Cloud Console
2. **Ensure file is valid JSON** format
3. **Upload through web interface** (don't manually copy)
4. **Check file permissions** if on Linux/Mac

#### **"Outlook token expired"**
1. **Remove the account** from the interface
2. **Add it again** with fresh authentication
3. **Check internet connection** for token refresh

#### **"Analysis fails or stops"**
- **Check account connections** in dashboard
- **Reduce max email count** for large mailboxes
- **Disable resume mode** if data seems corrupted
- **Check browser console** for error messages

### **Performance Tips**
- **Start small**: Begin with 1,000-5,000 emails per account
- **Use resume mode**: Avoid re-downloading existing data
- **Stable connection**: Ensure reliable internet during analysis
- **Close other apps**: Free up memory for large analyses

## 📞 Support & Development

### **Getting Help**
- **Check logs**: Terminal/command prompt shows detailed progress
- **Browser console**: F12 → Console for frontend errors
- **GitHub Issues**: Report bugs and request features
- **Documentation**: This README covers most scenarios

### **Contributing**
We welcome contributions! Areas for development:
- 🤖 **Spam Detection**: ML-based spam identification
- 🗑️ **Email Deletion**: Direct cleanup capabilities
- 📱 **Mobile App**: React Native/Flutter interface
- ☁️ **Cloud Version**: Hosted service option
- 🔌 **More Providers**: Yahoo, iCloud, Exchange

### **Development Setup**
```bash
git clone https://github.com/your-username/email-space-analyzer.git
cd email-space-analyzer

# Install development dependencies
pip install -r requirements.txt

# Run in development mode
python email_analyzer_backend.py --debug
```

## 📊 Power BI Integration

### **Import Process**
1. **Complete analysis** in the web app
2. **Click "Export to Power BI"**
3. **Download CSV files** from exports folder
4. **Open Power BI Desktop**
5. **Import CSV data** using "Get Data" → "Text/CSV"

### **Recommended Visualizations**
- **Tree Map**: Email count by sender
- **Bar Chart**: Storage usage by account
- **Line Chart**: Email volume timeline  
- **Pie Chart**: Provider distribution
- **Table**: Top space-consuming senders

### **Power BI Tips**
- **Separate files**: Import provider-specific CSVs for focused analysis
- **Date formatting**: Convert receivedDateTime to proper Date type
- **Size formatting**: Convert size_bytes to MB/GB for readability
- **Filters**: Add slicers for provider, account, and date ranges

## 🔒 Privacy & Security

### **Data Protection**
- **Local Processing**: All data stays on your computer
- **No Cloud Storage**: Nothing uploaded to external servers
- **Secure Authentication**: Uses official OAuth2 flows
- **Encrypted Storage**: Tokens stored securely by OS

### **What We Access**
- **Email Metadata**: Sender, date, size, subject, attachments
- **NO Email Content**: Never read or store email body text
- **Account Information**: Email address and display name only
- **NO Passwords**: Never store or see your passwords

### **Data Retention**
- **Temporary Processing**: Analysis data kept only during session
- **Export Files**: Saved locally in your data/exports folder
- **Token Storage**: Cached locally for convenience
- **Full Control**: Delete data folder to remove all traces

## 📋 Requirements

### **System Requirements**
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum (4GB+ for large mailboxes)
- **Storage**: 500MB for application + space for exports
- **Browser**: Chrome, Firefox, Safari, Edge (latest versions)
- **Internet**: Required for email API access

### **Python Dependencies**
All automatically installed via requirements.txt:
- flask>=2.3.0 (web framework)
- flask-cors>=4.0.0 (cross-origin requests)
- pandas>=1.5.0 (data processing)
- msal>=1.24.0 (Microsoft authentication)
- requests>=2.31.0 (HTTP requests)
- google-auth>=2.23.0 (Google authentication)
- google-api-python-client>=2.100.0 (Gmail API)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### **MIT License Summary**
- ✅ **Commercial use** allowed
- ✅ **Modification** allowed  
- ✅ **Distribution** allowed
- ✅ **Private use** allowed
- ❓ **Liability**: No warranty provided
- ❓ **Attribution**: Must include license notice

## 🙏 Acknowledgments

- **Microsoft Graph API** for Outlook integration
- **Google Gmail API** for Gmail integration
- **Chart.js** for beautiful visualizations
- **Flask** for the web framework
- **Pandas** for data processing
- **MSAL** for Microsoft authentication
- **Community contributors** for improvements and feedback

---

## 🎯 Version 2.0 Highlights

### **What's New**
- ✅ **Real authentication flows** (no more fake accounts)
- ✅ **Multi-account support** (multiple accounts per provider)
- ✅ **Enhanced setup guides** (step-by-step with screenshots)
- ✅ **Configurable analysis** (email limits, resume mode)
- ✅ **Better size detection** (improved Outlook accuracy)
- ✅ **Account identification** (track data by source account)
- ✅ **Improved UI/UX** (modals, progress indicators, error handling)

### **Migration from v1.0**
- **New file structure**: Save all files in same folder
- **Updated dependencies**: Run `pip install -r requirements.txt`
- **Re-connect accounts**: Previous connections won't work
- **New data format**: Includes account_id and account_email columns

**Ready to reclaim your email space? Let's get started! 🚀**

*Helping people organize their digital lives, one inbox at a time.*

## ✨ Features

### 🎯 **Core Analysis**
- **Multi-Provider Support**: Analyze both Outlook and Gmail accounts
- **Space Usage Insights**: Identify which senders consume the most storage
- **Volume Analysis**: See who sends you the most emails
- **Timeline Trends**: Understand your email patterns over time
- **Smart Detection**: Automatic attachment and large email identification

### 🎨 **Modern Interface**
- **Dark Professional Theme**: Easy on the eyes, modern design
- **Responsive Dashboard**: Works on desktop, tablet, and mobile
- **Interactive Charts**: Beautiful, interactive visualizations
- **Real-time Progress**: Live updates during analysis
- **One-Click Export**: Ready for Power BI integration

### 🔧 **Developer Features**
- **Open Source**: MIT licensed, contribution-friendly
- **Modular Architecture**: Easy to extend and customize
- **RESTful API**: Backend can be used independently
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### **Option 1: Double-Click Launch (Easiest)**

1. **Download** the project files to a folder
2. **Double-click** `start.bat` (Windows) or `start.sh` (Mac/Linux)
3. **Wait** for automatic setup and browser opening
4. **Connect** your email accounts and start analyzing!

### **Option 2: Manual Setup**

```bash
# Clone or download the project
git clone https://github.com/your-username/email-space-analyzer.git
cd email-space-analyzer

# Install dependencies
pip install flask flask-cors pandas msal requests google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Start the application
python email_analyzer_backend.py
```

## 📁 Project Structure

```
email-space-analyzer/
├── 📄 index.html                 # Web interface (frontend)
├── 🐍 email_analyzer_backend.py  # Python API server (backend)
├── 🚀 start.bat                  # Windows launcher
├── 🚀 start.sh                   # Linux/Mac launcher
├── 📖 README.md                  # This file
├── 📄 requirements.txt           # Python dependencies
├── 📊 data/                      # Data directory (auto-created)
│   ├── cache/                    # Authentication tokens
│   └── exports/                  # Analysis results & exports
└── 🔧 gmail_credentials.json     # Gmail API credentials (you provide)
```

## 🔑 Setup Guide

### **Outlook Setup** ✅ *Ready to Use*
Outlook works out of the box! Just click "Connect" and follow the authentication flow.

### **Gmail Setup** 📧 *Requires Google Cloud Setup*

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project** (or select existing)
3. **Enable Gmail API**:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Gmail API" and enable it
4. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Desktop application"
   - Download the JSON file
5. **Save as `gmail_credentials.json`** in the project folder
6. **Connect Gmail** in the app interface

## 📊 Using the Dashboard

### **Connection Status**
- **Green indicators**: Successfully connected
- **Red indicators**: Not connected or authentication expired
- **Account info**: Shows connected email address

### **Analysis Process**
1. **Connect Providers**: At least one email account required
2. **Start Analysis**: Click "Analyze My Emails"
3. **Monitor Progress**: Real-time progress bar and status updates
4. **View Results**: Automatic dashboard generation

### **Dashboard Insights**

#### **📈 Key Statistics**
- **Total Emails**: Complete count across all accounts
- **Storage Used**: Total space consumed by emails
- **Average Size**: Mean email size for optimization insights
- **Largest Email**: Biggest space consumer for cleanup

#### **📊 Visual Analytics**
- **Top Senders (Volume)**: Who emails you most frequently
- **Top Senders (Space)**: Who consumes most storage
- **Provider Distribution**: Outlook vs Gmail usage
- **Timeline Trends**: Email activity over past 12 months

## 💾 Power BI Integration

### **Export Process**
1. **Complete Analysis** in the web interface
2. **Click "Export to Power BI"** button
3. **Find CSV files** in `data/exports/` folder
4. **Import into Power BI** for advanced analytics

### **Data Structure**
```csv
from_name,from_email,receivedDateTime,hasAttachments,size_bytes,subject,provider
John Doe,john@company.com,2024-01-15T09:30:00Z,true,1024576,Project Update,outlook
Jane Smith,jane@gmail.com,2024-01-15T10:15:00Z,false,2048,Meeting Notes,gmail
```

### **Power BI Dashboard Ideas**
- **Space Usage by Sender**: Identify cleanup targets
- **Email Volume Trends**: Understand communication patterns  
- **Provider Comparison**: Outlook vs Gmail usage
- **Attachment Analysis**: Large file identification
- **Time-based Insights**: Peak email hours/days

## 🛠️ Technical Details

### **Architecture**
- **Frontend**: Pure HTML5/CSS3/JavaScript with Chart.js
- **Backend**: Python Flask RESTful API
- **Authentication**: Microsoft MSAL + Google OAuth2
- **Data Processing**: Pandas for analysis
- **Storage**: CSV exports, JSON analysis cache

### **Security & Privacy**
- **Local Processing**: All data stays on your computer
- **Token Security**: Encrypted token storage
- **No Data Upload**: No data sent to external servers
- **API Compliance**: Uses official Microsoft Graph & Gmail APIs

### **Performance**
- **Optimized Fetching**: Batched API requests
- **Progressive Loading**: Real-time progress updates
- **Memory Efficient**: Streaming data processing
- **Resumable**: Can continue interrupted analyses

## 🔧 Configuration

### **Advanced Options**
```bash
# Custom server settings
python email_analyzer_backend.py --port 8080 --host 0.0.0.0

# Debug mode
python email_analyzer_backend.py --debug

# Disable auto-browser opening
python email_analyzer_backend.py --no-browser
```

### **Email Limits**
- **Default**: 1,000 emails per provider
- **Configurable**: Adjust via web interface
- **No Hard Limit**: Process as many as API allows

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### **Development Setup**
```bash
git clone https://github.com/your-username/email-space-analyzer.git
cd email-space-analyzer

# Install development dependencies
pip install -r requirements.txt

# Run in debug mode
python email_analyzer_backend.py --debug
```

### **Contribution Areas**
- 🎨 **UI/UX Improvements**: Enhance the web interface
- 📊 **New Analytics**: Add more insight types
- 🔌 **Provider Support**: Add Yahoo, iCloud, etc.
- 🤖 **Spam Detection**: ML-based spam identification
- 📱 **Mobile Support**: React Native/Flutter app
- 🏗️ **Infrastructure**: Docker, cloud deployment

### **Roadmap**
- [ ] **Phase 1**: Spam detection with ML
- [ ] **Phase 2**: Email deletion capabilities  
- [ ] **Phase 3**: Mobile app development
- [ ] **Phase 4**: Cloud-hosted version
- [ ] **Phase 5**: Enterprise features

## 📋 Requirements

### **System Requirements**
- **Python**: 3.7 or higher
- **RAM**: 1GB minimum (2GB+ for large mailboxes)
- **Storage**: 100MB for application + space for exports
- **Browser**: Chrome, Firefox, Safari, Edge (latest versions)

### **Python Dependencies**
```
flask>=2.0.0
flask-cors>=3.0.0
pandas>=1.3.0
msal>=1.15.0
requests>=2.25.0
google-auth>=2.0.0
google-auth-oauthlib>=0.4.0
google-auth-httplib2>=0.1.0
google-api-python-client>=2.0.0
```

## 🐛 Troubleshooting

### **Common Issues**

#### **"Python not found"**
- **Install Python** from [python.org](https://python.org)
- **Ensure Python is in PATH** during installation
- **Try `python3`** instead of `python` on Mac/Linux

#### **"Google libraries not available"**
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### **"Gmail credentials not found"**
- **Download credentials** from Google Cloud Console
- **Save as `gmail_credentials.json`** in project folder
- **Ensure file is valid JSON** format

#### **"Token expired" errors**
- **Disconnect and reconnect** the problematic provider
- **Check internet connection** for token refresh
- **Delete cache files** in `data/cache/` if persistent

#### **Analysis fails or stops**
- **Check API rate limits** (wait and retry)
- **Reduce email count** in analysis settings
- **Check provider status** in dashboard
- **Review logs** in terminal for detailed errors

### **Performance Optimization**
- **Close other applications** during large analyses
- **Use wired internet** for stability
- **Increase virtual memory** if processing 50k+ emails
- **Run during off-peak hours** to avoid API throttling

## 📞 Support

### **Getting Help**
- 📖 **Documentation**: Check this README first
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-username/email-space-analyzer/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/your-username/email-space-analyzer/discussions)
- 📧 **Email Support**: email-analyzer@yourdomain.com

### **Self-Help Resources**
- **Check terminal output** for detailed error messages
- **Verify internet connection** for API access
- **Restart the application** if interface becomes unresponsive
- **Clear browser cache** if web interface has issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### **MIT License Summary**
- ✅ **Commercial use** allowed
- ✅ **Modification** allowed  
- ✅ **Distribution** allowed
- ✅ **Private use** allowed
- ❓ **Liability**: No warranty provided
- ❓ **Attribution**: Must include license notice

## 🙏 Acknowledgments

- **Microsoft Graph API** for Outlook integration
- **Google Gmail API** for Gmail integration
- **Chart.js** for beautiful visualizations
- **Flask** for the web framework
- **Pandas** for data processing
- **Community contributors** for improvements and feedback

---

**Made with ❤️ for email organization enthusiasts**

*Helping people reclaim their digital space, one inbox at a time.*