#!/usr/bin/env python3
"""
GitHub Webhook Server - Handles push events and triggers updates
- Listens for GitHub push webhooks
- Updates data from Vugraph
- Syncs design files (CSS, HTML, JS) from repository
"""

import os
import sys
import json
import hmac
import hashlib
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify, send_file, send_from_directory, Response

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vugraph_fetcher import VugraphDataFetcher

app = Flask(__name__, static_folder='.', static_url_path='')

# Configuration
WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET', 'your-webhook-secret-here')
REPO_PATH = os.path.dirname(os.path.abspath(__file__))

def verify_webhook_signature(payload_body, signature):
    """Verify GitHub webhook signature"""
    if not signature:
        return False
    
    expected_signature = 'sha256=' + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

def pull_latest_files():
    """Pull latest files from GitHub repository"""
    try:
        print(f"[{datetime.now()}] Pulling latest files from repository...")
        result = subprocess.run(
            ['git', 'pull', 'origin', 'main'],
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"[{datetime.now()}] Git pull successful")
            print(result.stdout)
            return True
        else:
            print(f"[{datetime.now()}] Git pull failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[{datetime.now()}] Error pulling files: {str(e)}")
        return False

def update_database_from_vugraph():
    """Update database from Vugraph API"""
    try:
        print(f"[{datetime.now()}] Starting Vugraph data update...")
        
        fetcher = VugraphDataFetcher()
        
        # Get dates to fetch (last 3 days + next 7 days)
        from datetime import datetime, timedelta
        today = datetime.now()
        start_date = (today - timedelta(days=3)).strftime('%Y-%m-%d')
        end_date = (today + timedelta(days=7)).strftime('%Y-%m-%d')
        
        print(f"[{datetime.now()}] Fetching tournaments from {start_date} to {end_date}")
        
        # Fetch and add data
        success = fetcher.add_date_to_database(start_date, end_date)
        
        if success:
            print(f"[{datetime.now()}] Database updated successfully")
            return True
        else:
            print(f"[{datetime.now()}] Database update failed")
            return False
            
    except Exception as e:
        print(f"[{datetime.now()}] Error updating database: {str(e)}")
        return False

def commit_and_push_changes():
    """Commit database changes and push to GitHub"""
    try:
        print(f"[{datetime.now()}] Checking for changes...")
        
        # Check if there are changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if not result.stdout.strip():
            print(f"[{datetime.now()}] No changes to commit")
            return True
        
        print(f"[{datetime.now()}] Changes detected:\n{result.stdout}")
        
        # Add changes
        subprocess.run(
            ['git', 'add', 'database.json'],
            cwd=REPO_PATH,
            timeout=10
        )
        
        # Commit
        commit_result = subprocess.run(
            ['git', 'commit', '-m', f'🤖 Webhook auto-update database from Vugraph ({datetime.now().isoformat()})'],
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if commit_result.returncode == 0:
            print(f"[{datetime.now()}] Changes committed")
            
            # Push to GitHub
            push_result = subprocess.run(
                ['git', 'push', 'origin', 'main'],
                cwd=REPO_PATH,
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
            )
            
            if push_result.returncode == 0:
                print(f"[{datetime.now()}] Changes pushed to GitHub")
                return True
            else:
                print(f"[{datetime.now()}] Push failed: {push_result.stderr}")
                return False
        else:
            print(f"[{datetime.now()}] No new changes to commit (database already up-to-date)")
            return True
            
    except Exception as e:
        print(f"[{datetime.now()}] Error committing/pushing: {str(e)}")
        return False

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle GitHub webhook push events"""
    
    # Get signature from headers
    signature = request.headers.get('X-Hub-Signature-256', '')
    payload_body = request.get_data()
    
    # Verify signature
    if not verify_webhook_signature(payload_body, signature):
        print(f"[{datetime.now()}] ✗ Invalid webhook signature")
        return jsonify({'error': 'Invalid signature'}), 401
    
    try:
        payload = json.loads(payload_body)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # Only handle push events
    if request.headers.get('X-GitHub-Event') != 'push':
        print(f"[{datetime.now()}] Ignoring non-push webhook event")
        return jsonify({'message': 'Not a push event'}), 200
    
    print(f"\n{'='*60}")
    print(f"[{datetime.now()}] GitHub Webhook Received!")
    print(f"Repository: {payload.get('repository', {}).get('full_name')}")
    print(f"Branch: {payload.get('ref')}")
    print(f"{'='*60}")
    
    # Check if it's the main branch
    if payload.get('ref') != 'refs/heads/main':
        print(f"[{datetime.now()}] Ignoring push to non-main branch")
        return jsonify({'message': 'Not main branch'}), 200
    
    # Execute update pipeline
    print(f"\n[{datetime.now()}] Starting update pipeline...")
    print(f"Step 1: Pull latest files from GitHub")
    if not pull_latest_files():
        print(f"[{datetime.now()}] ⚠ Warning: Git pull failed, continuing anyway...")
    
    print(f"\nStep 2: Update database from Vugraph")
    db_updated = update_database_from_vugraph()
    
    print(f"\nStep 3: Commit and push changes")
    if db_updated:
        commit_and_push_changes()
    
    print(f"[{datetime.now()}] Webhook processing completed!")
    print(f"{'='*60}\n")
    
    return jsonify({
        'status': 'success',
        'message': 'Webhook processed successfully',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    # Force reload database.json to ensure latest data is served
    import importlib
    try:
        db_path = os.path.join(REPO_PATH, 'database.json')
        with open(db_path, 'r', encoding='utf-8') as f:
            json.load(f)
    except Exception as e:
        print(f"[{datetime.now()}] Warning: Could not load database: {e}")
    
    return jsonify({
        'status': 'healthy',
        'service': 'GitHub Webhook Server',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Serve index.html"""
    try:
        return send_file('index.html')
    except:
        return send_from_directory('.', 'index.html')

@app.route('/database.json', methods=['GET'])
def serve_database():
    """Serve database.json with no-cache headers to ensure fresh data"""
    try:
        db_path = os.path.join(REPO_PATH, 'database.json')
        
        def generate():
            """Stream file in chunks"""
            with open(db_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    yield chunk
        
        response = Response(generate(), mimetype='application/json')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['ETag'] = None
        response.headers['Last-Modified'] = datetime.now().isoformat()
        return response
    except Exception as e:
        print(f"[{datetime.now()}] Error serving database.json: {e}")
        return jsonify({'error': f'Could not load database: {str(e)}'}), 500

@app.route('/api/data', methods=['GET'])
def serve_database_api():
    """API endpoint - serve database without loading to memory"""
    try:
        db_path = os.path.join(REPO_PATH, 'database.json')
        
        # Stream file directly - don't parse in memory to avoid OOM
        def generate():
            """Stream file in chunks"""
            with open(db_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    yield chunk
        
        response = Response(generate(), mimetype='application/json')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        print(f"[{datetime.now()}] Error serving API: {e}")
        return jsonify([]), 500

@app.route('/<path:filename>', methods=['GET'])
def serve_static(filename):
    """Serve static files"""
    try:
        return send_from_directory('.', filename)
    except:
        # If file not found, return 404
        return jsonify({'error': 'Not found'}), 404

@app.route('/status', methods=['GET'])
def status():
    """Get server status"""
    return jsonify({
        'status': 'running',
        'repository_path': REPO_PATH,
        'webhook_configured': bool(WEBHOOK_SECRET != 'your-webhook-secret-here'),
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    print(f"\n{'='*60}")
    print("GitHub Webhook Server Starting...")
    print(f"{'='*60}")
    print(f"Repository Path: {REPO_PATH}")
    print(f"Webhook Secret Configured: {bool(WEBHOOK_SECRET != 'your-webhook-secret-here')}")
    print(f"Server Address: http://0.0.0.0:5000")
    print(f"{'='*60}\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
