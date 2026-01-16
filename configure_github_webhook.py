#!/usr/bin/env python3
"""
GitHub Webhook Configuration - Automatically add webhook to GitHub
Requires: GitHub CLI (gh) to be installed and authenticated
"""

import os
import subprocess
import json
from datetime import datetime

def run_command(cmd, description=""):
    """Run a shell command and return output"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"[OK] {description}")
            return result.stdout.strip(), True
        else:
            print(f"[ERROR] {description} failed: {result.stderr}")
            return result.stderr, False
    except Exception as e:
        print(f"[ERROR] {description} error: {str(e)}")
        return str(e), False

def setup_github_webhook():
    """Setup GitHub webhook using GitHub CLI"""
    
    print(f"\n{'='*70}")
    print("GitHub Webhook Auto-Configuration")
    print(f"{'='*70}\n")
    
    # Check if GitHub CLI is installed
    output, success = run_command("gh --version", "Checking GitHub CLI")
    if not success:
        print("\n[FAIL] GitHub CLI is not installed!")
        print("Install it from: https://cli.github.com/")
        return False
    
    print(f"Found: {output}")
    
    # Check if authenticated
    output, success = run_command("gh auth status", "Checking GitHub authentication")
    if not success:
        print("\n[FAIL] Not authenticated with GitHub!")
        print("Run: gh auth login")
        return False
    
    print(f"[OK] Authenticated with GitHub")
    
    # Get repository info
    output, success = run_command(
        "gh repo view --json nameWithOwner -q .nameWithOwner",
        "Getting repository name"
    )
    if not success:
        print("\n[FAIL] Could not get repository info!")
        return False
    
    repo_name = output.strip()
    print(f"[OK] Repository: {repo_name}")
    
    # Read webhook secret
    try:
        with open('.env.webhook', 'r') as f:
            for line in f:
                if line.startswith('GITHUB_WEBHOOK_SECRET='):
                    webhook_secret = line.split('=')[1].strip()
                    print(f"[OK] Webhook Secret: {webhook_secret[:10]}...")
                    break
    except:
        print("\n[FAIL] Could not find .env.webhook file!")
        print("Run: python setup_webhook.py")
        return False
    
    # Ask for webhook URL
    print(f"\n{'='*70}")
    print("Webhook URL Configuration")
    print(f"{'='*70}\n")
    print("Where will your webhook server run?")
    print("Examples:")
    print("  1. Local test:  https://xxxxxxxx.ngrok.io/webhook")
    print("  2. VPS:         https://your-domain.com/webhook")
    print("  3. Cloud:       https://your-app.herokuapp.com/webhook")
    
    webhook_url = input("\nEnter webhook URL: ").strip()
    if not webhook_url.startswith('http'):
        print("[FAIL] URL must start with http:// or https://")
        return False
    
    print(f"[OK] Using webhook URL: {webhook_url}")
    
    # Create webhook via GitHub CLI
    print(f"\n{'='*70}")
    print("Creating GitHub Webhook")
    print(f"{'='*70}\n")
    
    # Check existing webhooks
    output, success = run_command(
        f"gh api repos/{repo_name}/hooks --jq '.[] | .config.url'",
        "Checking existing webhooks"
    )
    
    if webhook_url in output:
        print("[WARNING] Webhook already exists!")
        return True
    
    # Create new webhook
    webhook_payload = {
        "name": "web",
        "active": True,
        "events": ["push"],
        "config": {
            "url": webhook_url,
            "content_type": "json",
            "secret": webhook_secret,
            "insecure_ssl": "0"
        }
    }
    
    payload_json = json.dumps(webhook_payload)
    cmd = f'gh api repos/{repo_name}/hooks -f name=web -f active=true -f "events=push" -f "config[url]={webhook_url}" -f "config[content_type]=json" -f "config[secret]={webhook_secret}" -f "config[insecure_ssl]=0"'
    
    output, success = run_command(cmd, "Creating webhook in GitHub")
    
    if success:
        print(f"\n{'='*70}")
        print("[SUCCESS] Webhook created successfully!")
        print(f"{'='*70}\n")
        print(f"URL: {webhook_url}")
        print(f"Events: push")
        print(f"Secret: {webhook_secret[:10]}...\n")
        return True
    else:
        print(f"\n[FAIL] Webhook creation failed!")
        print("Try creating it manually:")
        print(f"1. Go to: https://github.com/{repo_name}/settings/hooks")
        print(f"2. Click 'Add webhook'")
        print(f"3. Set Payload URL: {webhook_url}")
        print(f"4. Set Secret: {webhook_secret}")
        print(f"5. Select: Push events\n")
        return False

if __name__ == '__main__':
    success = setup_github_webhook()
    exit(0 if success else 1)
