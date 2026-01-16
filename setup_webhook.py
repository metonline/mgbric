#!/usr/bin/env python3
"""
Setup GitHub Webhook for automatic updates
- Generates webhook secret
- Provides GitHub setup instructions
- Tests webhook configuration
"""

import os
import secrets
import json
from datetime import datetime

def generate_webhook_secret(length=32):
    """Generate a secure webhook secret"""
    return secrets.token_hex(length // 2)

def main():
    print(f"\n{'='*70}")
    print("🔐 GitHub Webhook Setup Guide")
    print(f"{'='*70}\n")
    
    # Generate secret
    webhook_secret = generate_webhook_secret()
    
    print("📝 STEP 1: Generate Webhook Secret")
    print(f"Your webhook secret: {webhook_secret}")
    print("\n⚠️  Keep this secret safe! You'll need it in the next steps.\n")
    
    # Environment variable setup
    print("📝 STEP 2: Set Environment Variable")
    print("\nOn Windows (PowerShell):")
    print(f"  $env:GITHUB_WEBHOOK_SECRET = '{webhook_secret}'")
    print("\nOr add to your .env file:")
    print(f"  GITHUB_WEBHOOK_SECRET={webhook_secret}\n")
    
    # GitHub webhook setup
    print("📝 STEP 3: Configure GitHub Webhook")
    print("\nGo to: https://github.com/YOUR_USERNAME/BRIC/settings/hooks")
    print("\n1. Click 'Add webhook'")
    print("2. Set Payload URL to your server:")
    print("   • If local testing: Use ngrok")
    print("   •   ngrok http 5000")
    print("   •   Then use: https://your-ngrok-url/webhook")
    print("   • If production: Use your domain")
    print("   •   https://your-domain.com/webhook")
    print("\n3. Set Content type: application/json")
    print(f"\n4. Set Secret: {webhook_secret}")
    print("\n5. Select events: Push events ✓")
    print("6. Click 'Add webhook'")
    print("\n")
    
    # Test webhook
    print("📝 STEP 4: Test Webhook Locally")
    print("\nRun webhook server:")
    print("  python webhook_server.py")
    print("\nIn another terminal, test with curl:")
    print("  python test_webhook.py")
    print("\n")
    
    # Install requirements
    print("📝 STEP 5: Install Requirements")
    print("\nMake sure Flask is installed:")
    print("  pip install flask\n")
    
    # Create .env file
    env_path = '.env.webhook'
    if not os.path.exists(env_path):
        with open(env_path, 'w') as f:
            f.write(f"# GitHub Webhook Configuration\n")
            f.write(f"GITHUB_WEBHOOK_SECRET={webhook_secret}\n")
        print(f"✓ Created {env_path} with webhook secret\n")
    else:
        print(f"⚠ {env_path} already exists\n")
    
    print("📝 STEP 6: Run Webhook Server")
    print("\nStart the server:")
    print("  python webhook_server.py")
    print("\nOr with persistent logging:")
    print("  python webhook_server.py > webhook.log 2>&1 &\n")
    
    print("✓ Setup complete!")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
