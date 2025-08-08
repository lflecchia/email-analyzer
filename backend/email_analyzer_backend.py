#!/usr/bin/env python3
"""
Email Space Analyzer - Backend API Server
Provides REST API endpoints for the web frontend
"""

import argparse
import json
import os
import sys
import time
import threading
import webbrowser
import uuid
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from email.utils import parseaddr, parsedate_to_datetime

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import msal
import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === CONFIGURATION ===
CONFIG = {
    'outlook': {
        'client_id': "d9d8f4b3-4bef-4eca-b5a2-b9e365bf8a21",
        'authority': "https://login.microsoftonline.com/consumers",
        'scopes': ["User.Read", "Mail.Read"]
    },
    'gmail': {
        'credentials_file': 'gmail_credentials.json',
        'token_file': 'gmail_token.pickle',
        'scopes': ['https://www.googleapis.com/auth/gmail.readonly']
    }
}

DATA_DIR = Path('data')
CACHE_DIR = DATA_DIR / 'cache'
EXPORTS_DIR = DATA_DIR / 'exports'
ACCOUNTS_FILE = CACHE_DIR / 'accounts.json'

# Ensure directories exist
for dir_path in [DATA_DIR, CACHE_DIR, EXPORTS_DIR]:
    dir_path.mkdir(exist_ok=True)

# === GOOGLE IMPORTS (Optional) ===
GOOGLE_AVAILABLE = True
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    GOOGLE_AVAILABLE = False
    logger.warning("Google libraries not available. Gmail support disabled.")

# === FLASK APP ===
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'email-analyzer-secret-key'

# === GLOBAL STATE ===
class AppState:
    def __init__(self):
        self.accounts = {'outlook': [], 'gmail': []}
        self.auth_flows = {}  # Store ongoing auth flows
        self.analysis_progress = {'status': 'idle', 'progress': 0, 'message': ''}
        self.last_analysis = None
        self.load_accounts()
    
    def load_accounts(self):
        """Load saved accounts from file"""
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, 'r') as f:
                    self.accounts = json.load(f)
                logger.info(f"Loaded {len(self.accounts.get('outlook', []))} Outlook and {len(self.accounts.get('gmail', []))} Gmail accounts")
            except Exception as e:
                logger.error(f"Error loading accounts: {e}")
    
    def save_accounts(self):
        """Save accounts to file"""
        try:
            with open(ACCOUNTS_FILE, 'w') as f:
                json.dump(self.accounts, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving accounts: {e}")
    
    def add_account(self, provider, account):
        """Add or update account"""
        if provider not in self.accounts:
            self.accounts[provider] = []
        
        # Check if account already exists
        existing_index = next((i for i, acc in enumerate(self.accounts[provider]) if acc['id'] == account['id']), -1)
        
        if existing_index >= 0:
            self.accounts[provider][existing_index] = account
        else:
            self.accounts[provider].append(account)
        
        self.save_accounts()
    
    def remove_account(self, provider, account_id):
        """Remove account"""
        if provider in self.accounts:
            self.accounts[provider] = [acc for acc in self.accounts[provider] if acc['id'] != account_id]
            self.save_accounts()
            return True
        return False
    
    def reset_progress(self):
        self.analysis_progress = {'status': 'idle', 'progress': 0, 'message': ''}

app_state = AppState()

# === TOKEN MANAGERS ===
class OutlookTokenManager:
    def __init__(self, account_id):
        self.account_id = account_id
        self.app = None
        self.cache = None
        self.current_token = None
        self.token_expiry = None
        self.account_info = None
        self._init_app()

    def _init_app(self):
        cache_file = CACHE_DIR / f'outlook_token_{self.account_id}.bin'
        self.cache = msal.SerializableTokenCache()
        if cache_file.exists():
            self.cache.deserialize(cache_file.read_text())
        
        self.app = msal.PublicClientApplication(
            CONFIG['outlook']['client_id'],
            authority=CONFIG['outlook']['authority'],
            token_cache=self.cache
        )

    def start_device_flow(self):
        """Start device code flow for authentication"""
        flow = self.app.initiate_device_flow(scopes=CONFIG['outlook']['scopes'])
        if "user_code" not in flow:
            raise Exception(f"Failed to create auth flow: {flow}")
        
        # Store flow for completion
        app_state.auth_flows[f"outlook_{self.account_id}"] = flow
        return flow

    def complete_device_flow(self, device_code):
        """Complete device code authentication"""
        flow_key = f"outlook_{self.account_id}"
        if flow_key not in app_state.auth_flows:
            return None
        
        flow = app_state.auth_flows[flow_key]
        result = self.app.acquire_token_by_device_flow(flow)
        
        if self.cache.has_state_changed:
            cache_file = CACHE_DIR / f'outlook_token_{self.account_id}.bin'
            cache_file.write_text(self.cache.serialize())

        if "access_token" not in result:
            return None

        self.current_token = result["access_token"]
        self.token_expiry = result.get("expires_in", 3600) + datetime.now(timezone.utc).timestamp()
        
        # Get account info
        self._get_account_info()
        
        # Clean up flow
        del app_state.auth_flows[flow_key]
        
        return self.account_info

    def check_device_flow(self, device_code):
        """Check if device flow is complete"""
        flow_key = f"outlook_{self.account_id}"
        if flow_key not in app_state.auth_flows:
            return None
        
        flow = app_state.auth_flows[flow_key]
        
        # Try to get token without waiting
        try:
            result = self.app.acquire_token_by_device_flow(flow, timeout=1)
            if "access_token" in result:
                return self.complete_device_flow(device_code)
        except:
            pass
        
        return None

    def _get_account_info(self):
        """Get user account information"""
        if not self.current_token:
            return None
        
        headers = {"Authorization": f"Bearer {self.current_token}"}
        response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            self.account_info = {
                'id': self.account_id,
                'email': user_data.get('mail') or user_data.get('userPrincipalName'),
                'name': user_data.get('displayName'),
                'provider': 'outlook',
                'lastSync': None,
                'emailCount': 0
            }
        return self.account_info

    def get_fresh_token(self):
        """Get a fresh token, refreshing if necessary"""
        if (self.current_token and self.token_expiry and 
            datetime.now(timezone.utc).timestamp() < (self.token_expiry - 300)):
            return self.current_token

        # Try silent refresh
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(CONFIG['outlook']['scopes'], account=accounts[0])
        else:
            result = self.app.acquire_token_silent(CONFIG['outlook']['scopes'], account=None)

        if result and "access_token" in result:
            self.current_token = result["access_token"]
            self.token_expiry = result.get("expires_in", 3600) + datetime.now(timezone.utc).timestamp()
            return self.current_token
        
        return None

    def is_connected(self):
        """Check if user is connected and token is valid"""
        token = self.get_fresh_token()
        return token is not None

class GmailTokenManager:
    def __init__(self, account_id):
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google libraries not available")
        self.account_id = account_id
        self.service = None
        self.credentials = None
        self.account_info = None
        self.load_existing_credentials()

    def upload_credentials(self, credentials_data):
        """Upload and save credentials file"""
        credentials_file = CACHE_DIR / f'gmail_credentials_{self.account_id}.json'
        with open(credentials_file, 'w') as f:
            json.dump(credentials_data, f, indent=2)
        return True

    def start_oauth_flow(self):
        """Start OAuth2 flow"""
        credentials_file = CACHE_DIR / f'gmail_credentials_{self.account_id}.json'
        if not credentials_file.exists():
            raise FileNotFoundError("Gmail credentials not uploaded")
        
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_file), CONFIG['gmail']['scopes'])
        
        # Get authorization URL
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        # Store flow for completion
        app_state.auth_flows[f"gmail_{self.account_id}"] = flow
        
        return auth_url

    def complete_oauth_flow(self, authorization_response):
        """Complete OAuth2 flow with authorization response"""
        flow_key = f"gmail_{self.account_id}"
        if flow_key not in app_state.auth_flows:
            return None
        
        flow = app_state.auth_flows[flow_key]
        flow.fetch_token(authorization_response=authorization_response)
        
        self.credentials = flow.credentials
        
        # Save credentials
        token_file = CACHE_DIR / f'gmail_token_{self.account_id}.pickle'
        with open(token_file, 'wb') as token:
            pickle.dump(self.credentials, token)
        
        self.service = build('gmail', 'v1', credentials=self.credentials)
        self._get_account_info()
        
        # Clean up flow
        del app_state.auth_flows[flow_key]
        
        return self.account_info

    def check_oauth_complete(self):
        """Check if OAuth flow is complete by trying to load credentials"""
        return self.load_existing_credentials()

    def _get_account_info(self):
        """Get Gmail account information"""
        if not self.service:
            return None
        
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            self.account_info = {
                'id': self.account_id,
                'email': profile.get('emailAddress'),
                'name': profile.get('emailAddress'),  # Gmail doesn't provide display name in profile
                'provider': 'gmail',
                'lastSync': None,
                'emailCount': profile.get('messagesTotal', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get Gmail account info: {e}")
        
        return self.account_info

    def load_existing_credentials(self):
        """Load existing credentials from file"""
        token_file = CACHE_DIR / f'gmail_token_{self.account_id}.pickle'
        if not token_file.exists():
            return False
        
        try:
            with open(token_file, 'rb') as token:
                self.credentials = pickle.load(token)
            
            if not self.credentials.valid:
                if self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    # Save refreshed credentials
                    with open(token_file, 'wb') as token:
                        pickle.dump(self.credentials, token)
                else:
                    return False
            
            self.service = build('gmail', 'v1', credentials=self.credentials)
            self._get_account_info()
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Gmail credentials: {e}")
            return False

    def is_connected(self):
        """Check if Gmail is connected and credentials are valid"""
        return self.credentials and self.credentials.valid

# === EMAIL ANALYSIS FUNCTIONS ===
def fetch_outlook_messages(account_id, max_items=1000, resume_mode=True, progress_callback=None):
    """Fetch messages from Outlook"""
    logger.info(f"Fetching Outlook messages for account {account_id}")
    
    token_manager = OutlookTokenManager(account_id)
    if not token_manager.is_connected():
        raise Exception(f"Outlook account {account_id} not connected")
    
    # Check for existing data if resume mode
    if resume_mode:
        existing_file = EXPORTS_DIR / f'outlook_{account_id}_messages.csv'
        if existing_file.exists():
            existing_df = pd.read_csv(existing_file)
            logger.info(f"Resume mode: Found {len(existing_df)} existing messages")
            # For now, return existing data. In production, we'd implement proper resume logic
            if progress_callback:
                progress_callback(len(existing_df), max_items)
            return existing_df.to_dict('records')
    
    messages = []
    base_url = "https://graph.microsoft.com/v1.0/me/messages"
    
    headers = {"Authorization": f"Bearer {token_manager.get_fresh_token()}"}
    
    # Enhanced query for better size estimation
    params = {
        "$select": "from,receivedDateTime,hasAttachments,subject,bodyPreview,internetMessageHeaders",
        "$orderby": "receivedDateTime desc",
        "$top": "50",
        "$expand": "singleValueExtendedProperties($filter=id eq 'Integer 0x0E08')"
    }
    
    count = 0
    url = base_url
    
    while url and count < max_items:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=60)
            params = None  # Only first page has params
            
            if response.status_code == 401:
                # Token expired, try to refresh
                token = token_manager.get_fresh_token()
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                    continue
                else:
                    raise Exception("Token expired and could not be refreshed")
            
            if response.status_code != 200:
                logger.error(f"Outlook API error: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            
            for msg in data.get("value", []):
                sender = (msg.get("from") or {}).get("emailAddress") or {}
                
                # Extract size - try multiple methods for better accuracy
                size_bytes = None
                
                # Method 1: Extended properties
                for prop in (msg.get("singleValueExtendedProperties") or []):
                    if prop.get("id") == "Integer 0x0E08":
                        try:
                            size_bytes = int(prop.get("value"))
                            break
                        except (TypeError, ValueError):
                            pass
                
                # Method 2: Content-Length header
                if size_bytes is None:
                    for header in msg.get("internetMessageHeaders", []):
                        if header.get("name", "").lower() == "content-length":
                            try:
                                size_bytes = int(header.get("value"))
                                break
                            except (TypeError, ValueError):
                                pass
                
                # Method 3: Estimate based on content
                if size_bytes is None:
                    # Basic estimation based on subject + body preview
                    subject_len = len(msg.get("subject", ""))
                    body_len = len(msg.get("bodyPreview", ""))
                    base_size = (subject_len + body_len) * 2  # Rough estimate
                    
                    # Add attachment penalty
                    if msg.get("hasAttachments"):
                        base_size += 50000  # Estimate 50KB average attachment
                    
                    size_bytes = base_size
                
                messages.append({
                    "from_name": sender.get("name"),
                    "from_email": sender.get("address"),
                    "receivedDateTime": msg.get("receivedDateTime"),
                    "hasAttachments": msg.get("hasAttachments"),
                    "size_bytes": size_bytes,
                    "subject": msg.get("subject"),
                    "provider": "outlook",
                    "account_id": account_id,
                    "account_email": token_manager.account_info.get('email') if token_manager.account_info else ''
                })
                
                count += 1
                if progress_callback:
                    progress_callback(count, max_items)
                
                if count >= max_items:
                    break
            
            url = data.get("@odata.nextLink")
            
        except Exception as e:
            logger.error(f"Error fetching Outlook messages: {e}")
            break
    
    logger.info(f"Fetched {count} Outlook messages for account {account_id}")
    return messages

def fetch_gmail_messages(account_id, max_items=1000, resume_mode=True, progress_callback=None):
    """Fetch messages from Gmail"""
    if not GOOGLE_AVAILABLE:
        return []
    
    logger.info(f"Fetching Gmail messages for account {account_id}")
    
    token_manager = GmailTokenManager(account_id)
    if not token_manager.is_connected():
        raise Exception(f"Gmail account {account_id} not connected")
    
    # Check for existing data if resume mode
    if resume_mode:
        existing_file = EXPORTS_DIR / f'gmail_{account_id}_messages.csv'
        if existing_file.exists():
            existing_df = pd.read_csv(existing_file)
            logger.info(f"Resume mode: Found {len(existing_df)} existing messages")
            if progress_callback:
                progress_callback(len(existing_df), max_items)
            return existing_df.to_dict('records')
    
    messages = []
    service = token_manager.service
    
    try:
        count = 0
        next_page_token = None
        
        while count < max_items:
            if next_page_token:
                result = service.users().messages().list(
                    userId='me', maxResults=50, pageToken=next_page_token).execute()
            else:
                result = service.users().messages().list(
                    userId='me', maxResults=50).execute()
            
            message_list = result.get('messages', [])
            if not message_list:
                break
            
            for msg in message_list:
                if count >= max_items:
                    break
                
                try:
                    msg_detail = service.users().messages().get(
                        userId='me', id=msg['id'], format='metadata',
                        metadataHeaders=['From', 'Subject', 'Date']).execute()
                    
                    headers = {h['name'].lower(): h['value'] 
                             for h in msg_detail.get('payload', {}).get('headers', [])}
                    
                    # Parse sender
                    from_header = headers.get('from', '')
                    from_name, from_email = parseaddr(from_header)
                    if not from_name:
                        from_name = from_email.split('@')[0] if '@' in from_email else from_email
                    
                    # Parse date
                    date_header = headers.get('date', '')
                    received_dt = ""
                    if date_header:
                        try:
                            dt = parsedate_to_datetime(date_header)
                            received_dt = dt.isoformat()
                        except:
                            received_dt = date_header
                    
                    # Check attachments
                    has_attachments = False
                    payload = msg_detail.get('payload', {})
                    if payload.get('parts'):
                        for part in payload['parts']:
                            if part.get('filename') or part.get('body', {}).get('attachmentId'):
                                has_attachments = True
                                break
                    
                    messages.append({
                        "from_name": from_name,
                        "from_email": from_email,
                        "receivedDateTime": received_dt,
                        "hasAttachments": has_attachments,
                        "size_bytes": msg_detail.get('sizeEstimate'),
                        "subject": headers.get('subject', ''),
                        "provider": "gmail",
                        "account_id": account_id,
                        "account_email": token_manager.account_info.get('email') if token_manager.account_info else ''
                    })
                    
                    count += 1
                    if progress_callback:
                        progress_callback(count, max_items)
                        
                except Exception as e:
                    logger.warning(f"Error processing Gmail message {msg.get('id')}: {e}")
                    continue
            
            next_page_token = result.get('nextPageToken')
            if not next_page_token:
                break
                
    except Exception as e:
        logger.error(f"Error fetching Gmail messages: {e}")
    
    logger.info(f"Fetched {count} Gmail messages for account {account_id}")
    return messages

def analyze_messages(all_messages):
    """Analyze messages and generate insights"""
    if not all_messages:
        return None
    
    df = pd.DataFrame(all_messages)
    
    # Basic stats
    total_emails = len(df)
    total_space = df['size_bytes'].fillna(0).sum()
    avg_size = df['size_bytes'].fillna(0).mean()
    largest_email = df['size_bytes'].fillna(0).max()
    
    # Top senders by count
    top_senders_count = (df.groupby('from_email', dropna=True)
                        .size()
                        .sort_values(ascending=False)
                        .head(10))
    
    # Top senders by space
    top_senders_space = (df.dropna(subset=['size_bytes'])
                        .groupby('from_email')['size_bytes']
                        .sum()
                        .sort_values(ascending=False)
                        .head(10))
    
    # Account distribution (now includes individual accounts)
    account_stats = df.groupby('account_email').agg({
        'from_email': 'count',
        'size_bytes': lambda x: x.fillna(0).sum()
    }).to_dict('index')
    
    # Timeline data (last 12 months)
    df['receivedDateTime'] = pd.to_datetime(df['receivedDateTime'], errors='coerce')
    df_recent = df[df['receivedDateTime'] > datetime.now() - pd.DateOffset(months=12)]
    
    timeline = (df_recent.groupby(df_recent['receivedDateTime'].dt.to_period('M'))
               .size()
               .to_dict())
    
    timeline_formatted = {str(k): v for k, v in timeline.items()}
    
    return {
        'stats': {
            'total_emails': total_emails,
            'total_space': total_space,
            'avg_size': avg_size,
            'largest_email': largest_email
        },
        'top_senders_count': top_senders_count.to_dict(),
        'top_senders_space': top_senders_space.to_dict(),
        'account_distribution': account_stats,
        'timeline': timeline_formatted,
        'last_updated': datetime.now().isoformat(),
        'accounts_analyzed': df['account_email'].nunique()
    }

# === API ROUTES ===
@app.route('/')
def serve_frontend():
    """Serve the main HTML file"""
    try:
        # Look for index.html in the same directory
        html_file = Path(__file__).parent / 'index.html'
        if html_file.exists():
            return html_file.read_text(encoding='utf-8')
        else:
            # Return a simple page directing to create index.html
            return """
            <!DOCTYPE html>
            <html>
            <head><title>Email Space Analyzer</title></head>
            <body style="font-family: Arial; padding: 40px; background: #1E1E1E; color: white;">
            <h1>🚀 Email Space Analyzer Backend is Running!</h1>
            <p>The backend API server is working correctly.</p>
            <p>Please ensure you have the <code>index.html</code> file in the same directory as this Python script.</p>
            <p><strong>Next steps:</strong></p>
            <ol>
                <li>Save the frontend HTML code to a file named <code>index.html</code></li>
                <li>Place it in the same folder as this Python script</li>
                <li>Refresh this page</li>
            </ol>
            <p>API endpoints are available at: <code>/api/*</code></p>
            </body>
            </html>
            """
    except Exception as e:
        return f"Error loading frontend: {e}", 500

@app.route('/api/accounts')
def get_accounts():
    """Get all connected accounts"""
    return jsonify({
        'success': True,
        'accounts': app_state.accounts
    })

@app.route('/api/auth/<provider>/start', methods=['POST'])
def start_auth(provider):
    """Start authentication flow for provider"""
    try:
        account_id = str(uuid.uuid4())
        
        if provider == 'outlook':
            token_manager = OutlookTokenManager(account_id)
            flow = token_manager.start_device_flow()
            
            return jsonify({
                'success': True,
                'account_id': account_id,
                'verification_uri': flow['verification_uri'],
                'user_code': flow['user_code'],
                'device_code': flow['device_code']
            })
        
        elif provider == 'gmail':
            if not GOOGLE_AVAILABLE:
                return jsonify({'success': False, 'error': 'Gmail support not available'}), 400
            
            token_manager = GmailTokenManager(account_id)
            
            try:
                auth_url = token_manager.start_oauth_flow()
                return jsonify({
                    'success': True,
                    'account_id': account_id,
                    'auth_url': auth_url
                })
            except FileNotFoundError:
                return jsonify({
                    'success': False, 
                    'error': 'Gmail credentials not uploaded. Please upload credentials file first.'
                }), 400
        
        else:
            return jsonify({'success': False, 'error': 'Unknown provider'}), 400
            
    except Exception as e:
        logger.error(f"Error starting auth for {provider}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/<provider>/check', methods=['POST'])
def check_auth(provider):
    """Check authentication status"""
    try:
        data = request.get_json()
        
        if provider == 'outlook':
            device_code = data.get('device_code')
            if not device_code:
                return jsonify({'success': False, 'error': 'Device code required'}), 400
            
            # Extract account_id from stored flows
            account_id = None
            for key, flow in app_state.auth_flows.items():
                if key.startswith('outlook_') and flow.get('device_code') == device_code:
                    account_id = key.replace('outlook_', '')
                    break
            
            if not account_id:
                return jsonify({'success': False, 'error': 'Auth flow not found'}), 400
            
            token_manager = OutlookTokenManager(account_id)
            account = token_manager.check_device_flow(device_code)
            
            if account:
                app_state.add_account('outlook', account)
                return jsonify({'success': True, 'account': account})
            else:
                return jsonify({'success': False, 'message': 'Authentication not complete yet'})
        
        elif provider == 'gmail':
            # For Gmail, we check if any recent auth flow was completed
            # This is a simplified approach - in production, you'd track this per session
            gmail_accounts = [acc for acc in app_state.accounts.get('gmail', []) 
                            if datetime.fromisoformat(acc.get('lastSync', '1970-01-01T00:00:00')).replace(tzinfo=None) > 
                               (datetime.now() - pd.Timedelta(minutes=5))]
            
            if gmail_accounts:
                return jsonify({'success': True, 'account': gmail_accounts[-1]})
            else:
                return jsonify({'success': False, 'message': 'Authentication not complete yet'})
        
        else:
            return jsonify({'success': False, 'error': 'Unknown provider'}), 400
            
    except Exception as e:
        logger.error(f"Error checking auth for {provider}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gmail/credentials', methods=['POST'])
def upload_gmail_credentials():
    """Upload Gmail credentials file"""
    try:
        credentials_data = request.get_json()
        
        # Validate credentials format
        if not credentials_data or 'installed' not in credentials_data:
            return jsonify({'success': False, 'error': 'Invalid credentials format'}), 400
        
        # Generate account ID and save credentials
        account_id = str(uuid.uuid4())
        token_manager = GmailTokenManager(account_id)
        token_manager.upload_credentials(credentials_data)
        
        return jsonify({
            'success': True,
            'account_id': account_id,
            'message': 'Credentials uploaded successfully'
        })
        
    except Exception as e:
        logger.error(f"Error uploading Gmail credentials: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/accounts/<provider>/<account_id>', methods=['DELETE'])
def remove_account(provider, account_id):
    """Remove an account"""
    try:
        success = app_state.remove_account(provider, account_id)
        
        if success:
            # Also remove associated token files
            if provider == 'outlook':
                token_file = CACHE_DIR / f'outlook_token_{account_id}.bin'
                if token_file.exists():
                    token_file.unlink()
            elif provider == 'gmail':
                token_file = CACHE_DIR / f'gmail_token_{account_id}.pickle'
                creds_file = CACHE_DIR / f'gmail_credentials_{account_id}.json'
                for file in [token_file, creds_file]:
                    if file.exists():
                        file.unlink()
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Account not found'}), 404
            
    except Exception as e:
        logger.error(f"Error removing account {provider}/{account_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/accounts/<provider>/<account_id>/refresh', methods=['POST'])
def refresh_account(provider, account_id):
    """Refresh account information"""
    try:
        if provider == 'outlook':
            token_manager = OutlookTokenManager(account_id)
            if token_manager.is_connected():
                account_info = token_manager._get_account_info()
                if account_info:
                    app_state.add_account('outlook', account_info)
                    return jsonify({'success': True, 'account': account_info})
        
        elif provider == 'gmail':
            token_manager = GmailTokenManager(account_id)
            if token_manager.is_connected():
                account_info = token_manager._get_account_info()
                if account_info:
                    app_state.add_account('gmail', account_info)
                    return jsonify({'success': True, 'account': account_info})
        
        return jsonify({'success': False, 'error': 'Account not connected or not found'}), 400
        
    except Exception as e:
        logger.error(f"Error refreshing account {provider}/{account_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def start_analysis():
    """Start email analysis"""
    try:
        data = request.get_json()
        max_emails = data.get('max_emails', 1000)
        resume_mode = data.get('resume_mode', True)
        
        if app_state.analysis_progress['status'] == 'running':
            return jsonify({'success': False, 'error': 'Analysis already in progress'}), 400
        
        # Check if any accounts are connected
        total_accounts = sum(len(accounts) for accounts in app_state.accounts.values())
        if total_accounts == 0:
            return jsonify({'success': False, 'error': 'No email accounts connected'}), 400
        
        # Start analysis in background thread
        thread = threading.Thread(target=run_analysis, args=(max_emails, resume_mode))
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Analysis started'})
        
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def run_analysis(max_emails, resume_mode):
    """Run the email analysis in background"""
    try:
        app_state.analysis_progress = {'status': 'running', 'progress': 0, 'message': 'Starting analysis...'}
        
        all_messages = []
        total_accounts = sum(len(accounts) for accounts in app_state.accounts.values())
        completed_accounts = 0
        
        def update_progress(current, total, account_email):
            account_progress = (current / total) * 100 if total > 0 else 100
            overall_progress = ((completed_accounts / total_accounts) * 100 + 
                              (account_progress / total_accounts))
            app_state.analysis_progress.update({
                'progress': min(overall_progress, 95),  # Reserve 5% for final processing
                'message': f'Fetching emails from {account_email}... ({current}/{total})'
            })
        
        # Fetch Outlook messages
        for account in app_state.accounts.get('outlook', []):
            app_state.analysis_progress['message'] = f'Connecting to Outlook account {account["email"]}...'
            
            try:
                def outlook_progress(current, total):
                    update_progress(current, total, account['email'])
                
                outlook_messages = fetch_outlook_messages(
                    account['id'], 
                    max_emails, 
                    resume_mode,
                    outlook_progress
                )
                all_messages.extend(outlook_messages)
                
                # Update account info
                account['lastSync'] = datetime.now().isoformat()
                account['emailCount'] = len(outlook_messages)
                app_state.add_account('outlook', account)
                
                completed_accounts += 1
                logger.info(f"Fetched {len(outlook_messages)} Outlook messages from {account['email']}")
                
            except Exception as e:
                logger.error(f"Error fetching Outlook messages for {account['email']}: {e}")
                completed_accounts += 1
                continue
        
        # Fetch Gmail messages
        for account in app_state.accounts.get('gmail', []):
            app_state.analysis_progress['message'] = f'Connecting to Gmail account {account["email"]}...'
            
            try:
                def gmail_progress(current, total):
                    update_progress(current, total, account['email'])
                
                gmail_messages = fetch_gmail_messages(
                    account['id'], 
                    max_emails, 
                    resume_mode,
                    gmail_progress
                )
                all_messages.extend(gmail_messages)
                
                # Update account info
                account['lastSync'] = datetime.now().isoformat()
                account['emailCount'] = len(gmail_messages)
                app_state.add_account('gmail', account)
                
                completed_accounts += 1
                logger.info(f"Fetched {len(gmail_messages)} Gmail messages from {account['email']}")
                
            except Exception as e:
                logger.error(f"Error fetching Gmail messages for {account['email']}: {e}")
                completed_accounts += 1
                continue
        
        # Analyze messages
        app_state.analysis_progress.update({
            'progress': 95,
            'message': 'Analyzing email patterns...'
        })
        
        analysis_result = analyze_messages(all_messages)
        
        if not analysis_result:
            raise Exception("No messages to analyze")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw data
        df = pd.DataFrame(all_messages)
        raw_file = EXPORTS_DIR / f'email_data_{timestamp}.csv'
        df.to_csv(raw_file, index=False)
        
        # Save individual account files for easier Power BI import
        for provider in ['outlook', 'gmail']:
            provider_data = df[df['provider'] == provider]
            if not provider_data.empty:
                provider_file = EXPORTS_DIR / f'{provider}_data_{timestamp}.csv'
                provider_data.to_csv(provider_file, index=False)
        
        # Save analysis
        analysis_file = EXPORTS_DIR / f'analysis_{timestamp}.json'
        with open(analysis_file, 'w') as f:
            json.dump(analysis_result, f, indent=2, default=str)
        
        app_state.last_analysis = analysis_result
        app_state.analysis_progress.update({
            'status': 'completed',
            'progress': 100,
            'message': f'Analysis complete! Processed {len(all_messages)} emails from {analysis_result["accounts_analyzed"]} accounts.'
        })
        
        logger.info(f"Analysis completed successfully. {len(all_messages)} emails processed from {analysis_result['accounts_analyzed']} accounts.")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        app_state.analysis_progress.update({
            'status': 'error',
            'progress': 0,
            'message': f'Analysis failed: {str(e)}'
        })

@app.route('/api/progress')
def get_progress():
    """Get analysis progress"""
    return jsonify(app_state.analysis_progress)

@app.route('/api/results')
def get_results():
    """Get analysis results"""
    if not app_state.last_analysis:
        return jsonify({'success': False, 'error': 'No analysis results available'}), 404
    
    return jsonify({
        'success': True,
        'data': app_state.last_analysis
    })

@app.route('/api/export')
def export_data():
    """Export data for Power BI"""
    try:
        if not app_state.last_analysis:
            return jsonify({'success': False, 'error': 'No data to export'}), 404
        
        # Find most recent export files
        export_files = list(EXPORTS_DIR.glob('email_data_*.csv'))
        if not export_files:
            return jsonify({'success': False, 'error': 'No export files found'}), 404
        
        latest_file = max(export_files, key=lambda f: f.stat().st_mtime)
        
        return jsonify({
            'success': True,
            'file_path': str(latest_file),
            'file_name': latest_file.name,
            'file_size': latest_file.stat().st_size,
            'last_modified': latest_file.stat().st_mtime
        })
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download export file"""
    try:
        return send_from_directory(EXPORTS_DIR, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 404

# === MAIN FUNCTION ===
def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Email Space Analyzer - Backend Server')
    parser.add_argument('--port', type=int, default=5000, help='Port to run server on')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind server to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    
    args = parser.parse_args()
    
    # Print startup info
    print("\n" + "="*60)
    print("📧 EMAIL SPACE ANALYZER - BACKEND SERVER")
    print("="*60)
    print(f"🌐 Server URL: http://{args.host}:{args.port}")
    print(f"📁 Data directory: {DATA_DIR.absolute()}")
    print(f"📊 Export directory: {EXPORTS_DIR.absolute()}")
    print(f"🔧 Debug mode: {'ON' if args.debug else 'OFF'}")
    print(f"📧 Outlook support: ✅ Available")
    print(f"📧 Gmail support: {'✅ Available' if GOOGLE_AVAILABLE else '❌ Not Available (install google libs)'}")
    
    # Show existing accounts
    outlook_count = len(app_state.accounts.get('outlook', []))
    gmail_count = len(app_state.accounts.get('gmail', []))
    print(f"👥 Connected accounts: {outlook_count} Outlook, {gmail_count} Gmail")
    
    print("="*60)
    print("📖 How to use:")
    print("1. The web interface will open automatically in your browser")
    print("2. Connect your email accounts (Outlook and/or Gmail)")
    print("3. Configure analysis settings (max emails, resume mode)")
    print("4. Click 'Analyze My Emails' to start the analysis")
    print("5. View results in the interactive dashboard")
    print("6. Export data for Power BI if needed")
    print("="*60)
    print("🛑 Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Open browser automatically unless disabled
    if not args.no_browser:
        def open_browser():
            time.sleep(1.5)  # Give server time to start
            webbrowser.open(f'http://{args.host}:{args.port}')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    # Start server
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_reloader=False  # Disable reloader to prevent double startup
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
