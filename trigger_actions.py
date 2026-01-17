#!/usr/bin/env python3
"""Trigger GitHub Actions workflow to deploy to Fly.io"""

import os
import sys
import subprocess
import requests
import json

def get_github_token():
    """Get GitHub token from environment or git config"""
    # Try environment variable
    if 'GITHUB_TOKEN' in os.environ:
        return os.environ['GITHUB_TOKEN']
    
    # Try git config
    try:
        result = subprocess.run(['git', 'config', '--global', 'github.token'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    
    return None

def trigger_workflow():
    """Trigger GitHub Actions workflow"""
    token = get_github_token()
    
    if not token:
        print("❌ GitHub token bulunamadı!")
        print("\nToken'i şu şekilde set edebilirsin:")
        print("  git config --global github.token YOUR_GITHUB_TOKEN")
        print("\nVeya environment variable:")
        print("  $env:GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN'")
        return False
    
    owner = 'metonline'
    repo = 'mgbric'
    workflow = 'deploy-fly.yml'
    branch = 'main'
    
    url = f'https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow}/dispatches'
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    payload = {
        'ref': branch
    }
    
    print(f"🔄 GitHub Actions workflow trigger ediliyor...")
    print(f"   Owner: {owner}")
    print(f"   Repo: {repo}")
    print(f"   Workflow: {workflow}")
    print(f"   Branch: {branch}")
    print()
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 204:
            print("✅ Workflow trigger başarılı!")
            print("⏳ GitHub Actions çalışıyor... (1-2 dakika bekle)")
            print("\n📊 Status kontrol et:")
            print(f"   https://github.com/{owner}/{repo}/actions")
            return True
        else:
            print(f"❌ Hata: HTTP {response.status_code}")
            print(f"   Mesaj: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Request hatası: {str(e)}")
        return False

if __name__ == '__main__':
    success = trigger_workflow()
    sys.exit(0 if success else 1)
