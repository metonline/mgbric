#!/usr/bin/env python3
"""
Render Deployment Preparation Script
Prepares your BRIC project for deployment on Render
"""

import os
import subprocess
import sys

def check_git():
    """Check if git repository is initialized"""
    if not os.path.exists('.git'):
        print("❌ Git not initialized")
        print("   Run: git init")
        return False
    print("✅ Git repository found")
    return True

def check_files():
    """Check if all deployment files exist"""
    required_files = [
        'requirements.txt',
        'Procfile',
        'index.html',
        'script.js',
        'webhook_server.py'
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False
    
    print("✅ All required deployment files present")
    return True

def check_git_config():
    """Check if git is configured"""
    try:
        user_name = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        user_email = subprocess.run(
            ['git', 'config', 'user.email'],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        if user_name and user_email:
            print(f"✅ Git configured: {user_name} <{user_email}>")
            return True
        else:
            print("❌ Git not configured")
            print("   Run: git config --global user.name 'Your Name'")
            print("   Run: git config --global user.email 'your@email.com'")
            return False
    except Exception as e:
        print(f"❌ Git check failed: {e}")
        return False

def suggest_next_steps():
    """Print deployment steps"""
    print("\n" + "="*60)
    print("🚀 DEPLOYMENT STEPS")
    print("="*60)
    
    steps = [
        "1. Commit deployment files to Git:",
        "   git add requirements.txt Procfile RENDER_DEPLOY.md render.yaml build.sh",
        "   git commit -m 'Add Render deployment configuration'",
        "   git push origin main",
        "",
        "2. Visit https://render.com and sign up",
        "",
        "3. Choose deployment option:",
        "   • STATIC SITE (fastest):",
        "     - New → Static Site",
        "     - Publish Directory: .",
        "",
        "   • WEB SERVICE (with backend):",
        "     - New → Web Service",
        "     - Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT webhook_server:app",
        "",
        "4. Set environment variables (for Web Service):",
        "   - GITHUB_WEBHOOK_SECRET: <your-webhook-secret>",
        "   - FLASK_ENV: production",
        "",
        "5. Deploy and monitor in Render dashboard",
        "",
        "📖 Detailed guide: RENDER_DEPLOY.md"
    ]
    
    for step in steps:
        print(step)
    print("="*60)

def main():
    print("\n🔍 Checking Render deployment readiness...\n")
    
    checks = [
        ("Git Repository", check_git),
        ("Required Files", check_files),
        ("Git Configuration", check_git_config),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"Checking {name}...", end=" ")
        result = check_func()
        results.append(result)
        print()
    
    if all(results):
        print("\n✅ All checks passed! Ready to deploy!")
        suggest_next_steps()
    else:
        print("\n⚠️  Please fix the issues above before deploying")
        sys.exit(1)

if __name__ == '__main__':
    main()
