#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Push database to GitHub and trigger Fly.io redeployment
"""

import subprocess
import os
import json
from datetime import datetime

REPO_PATH = os.path.dirname(os.path.abspath(__file__))

def git_commit_push():
    """Commit and push database to GitHub"""
    try:
        os.chdir(REPO_PATH)
        
        print("📝 Git konfigürasyonu...")
        subprocess.run(['git', 'config', 'user.email', 'bot@hosgoru.local'], 
                      capture_output=True, timeout=10)
        subprocess.run(['git', 'config', 'user.name', 'UpdateBot'], 
                      capture_output=True, timeout=10)
        
        print("➕ Dosyalar staging'e alınıyor...")
        result = subprocess.run(['git', 'add', 'database.json'], 
                               capture_output=True, text=True, timeout=10)
        
        print("💾 Commit yapılıyor...")
        commit_result = subprocess.run(
            ['git', 'commit', '-m', f'🤖 Database auto-update from Vugraph - {datetime.now().strftime("%Y-%m-%d %H:%M")}'],
            capture_output=True, text=True, timeout=10
        )
        
        if commit_result.returncode == 0:
            print("✅ Commit başarılı")
        else:
            print("⚠️  Hiç değişiklik yok")
            return False
        
        print("🚀 GitHub'a push yapılıyor...")
        push_result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            capture_output=True, text=True, timeout=30
        )
        
        if push_result.returncode == 0:
            print("✅ GitHub push başarılı!")
            print("\n" + "="*60)
            print("⏳ Fly.io otomatik redeploy yapılıyor...")
            print("   Site: https://mgbric.fly.dev")
            print("   Bekleme süresi: ~1-2 dakika")
            print("="*60)
            return True
        else:
            print(f"❌ Push hatası: {push_result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("📤 VERILERI SITENIN SUNUCUSUNA GÖNDER")
    print("="*60 + "\n")
    
    git_commit_push()
