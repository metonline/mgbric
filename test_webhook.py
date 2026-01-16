#!/usr/bin/env python3
"""
Test GitHub Webhook locally
- Simulates GitHub webhook push event
- Tests webhook signature verification
- Tests database update and file sync
"""

import os
import sys
import json
import hmac
import hashlib
import requests
from datetime import datetime

def test_webhook(webhook_url='http://localhost:5000/webhook', webhook_secret='your-webhook-secret-here'):
    """Test webhook with simulated GitHub push event"""
    
    print(f"\n{'='*70}")
    print("Testing GitHub Webhook")
    print(f"{'='*70}\n")
    
    # Create sample GitHub webhook payload
    payload = {
        "ref": "refs/heads/main",
        "before": "abc123",
        "after": "def456",
        "repository": {
            "id": 123456,
            "name": "BRIC",
            "full_name": "username/BRIC",
            "private": False,
            "owner": {
                "name": "username"
            }
        },
        "pusher": {
            "name": "username",
            "email": "user@example.com"
        },
        "sender": {
            "login": "username",
            "type": "User"
        },
        "created": False,
        "deleted": False,
        "forced": False,
        "compare": "https://github.com/username/BRIC/compare/abc123...def456",
        "commits": [
            {
                "id": "def456",
                "message": "Update from webhook test",
                "author": {
                    "name": "username",
                    "email": "user@example.com"
                }
            }
        ],
        "head_commit": {
            "id": "def456",
            "message": "Update from webhook test",
            "author": {
                "name": "username",
                "email": "user@example.com"
            }
        }
    }
    
    # Convert to JSON bytes
    payload_json = json.dumps(payload)
    payload_bytes = payload_json.encode('utf-8')
    
    # Generate signature
    signature = 'sha256=' + hmac.new(
        webhook_secret.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    print(f"Webhook URL: {webhook_url}")
    print(f"Webhook Secret: {webhook_secret}")
    print(f"Signature: {signature}\n")
    
    # Send request
    print("Sending webhook request...")
    headers = {
        'Content-Type': 'application/json',
        'X-Hub-Signature-256': signature,
        'X-GitHub-Event': 'push',
        'X-GitHub-Delivery': 'test-delivery-id'
    }
    
    try:
        response = requests.post(
            webhook_url,
            data=payload_json,
            headers=headers,
            timeout=60
        )
        
        print(f"\n[OK] Request sent!")
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}\n")
        
        if response.status_code == 200:
            print("[OK] Webhook test successful!\n")
            return True
        else:
            print(f"[FAIL] Webhook returned unexpected status: {response.status_code}\n")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n[FAIL] Could not connect to webhook server at {webhook_url}")
        print("Make sure the webhook server is running:")
        print("  python webhook_server.py\n")
        return False
    except Exception as e:
        print(f"\n[FAIL] Error testing webhook: {str(e)}\n")
        return False

def test_health_check(health_url='http://localhost:5000/health'):
    """Test health check endpoint"""
    print(f"Testing health check endpoint: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print("[OK] Server is healthy")
            print(f"Response: {json.dumps(response.json(), indent=2)}\n")
            return True
        else:
            print(f"[FAIL] Server returned status {response.status_code}\n")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] Could not connect to server at {health_url}\n")
        print("Make sure webhook_server.py is running:\n")
        print("  python webhook_server.py\n")
        return False

if __name__ == '__main__':
    # Get webhook secret from environment or use default
    webhook_secret = os.environ.get('GITHUB_WEBHOOK_SECRET', 'test-secret')
    webhook_url = 'http://localhost:5000/webhook'
    
    print("\n[INFO] Pre-test checks...\n")
    
    # Test health check first
    if not test_health_check():
        print("[FAIL] Webhook server is not running!")
        print("\nStart the server with:")
        print("  python webhook_server.py")
        sys.exit(1)
    
    # Test webhook
    test_webhook(webhook_url, webhook_secret)
    
    print(f"{'='*70}\n")
