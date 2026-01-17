#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch database from GitHub and push to Fly.io
"""

import subprocess
import os
import json
import requests
from datetime import datetime

REPO_PATH = os.path.dirname(os.path.abspath(__file__))
GITHUB_REPO = "metonline/hosgoru-pwa"  # GitHub repo
GITHUB_BRANCH = "main"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/database.json"

def fetch_from_github():
    """Fetch database.json from GitHub"""
    try:
        print("📥 GitHub'dan database.json çekiliyor...")
        response = requests.get(GITHUB_RAW_URL, timeout=30)
        response.raise_for_status()
        
        raw_data = response.json()
        
        # GitHub'daki eski format (array) ise yeni formata çevir
        if isinstance(raw_data, list):
            print("   ⚠️  Eski format (array) tespit edildi, yeni formata dönüştürülüyor...")
            data = {
                "version": "2.0",
                "last_updated": datetime.now().isoformat(),
                "events": {},
                "metadata": {
                    "total_tournaments": 0,
                    "total_boards": 0
                }
            }
        else:
            data = raw_data
        
        print(f"   ✅ GitHub'dan alındı")
        if isinstance(data, dict):
            print(f"   📊 Events: {len(data.get('events', {}))}")
            print(f"   ⏰ Son güncelleme: {data.get('last_updated', 'UNKNOWN')}")
        else:
            print(f"   📊 Records: {len(data)}")
        
        return data
    except Exception as e:
        print(f"   ❌ GitHub çekme hatası: {e}")
        return None

def save_database(data):
    """Save database locally"""
    try:
        db_path = os.path.join(REPO_PATH, 'database.json')
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"   ✅ Yerel olarak kaydedildi")
        return True
    except Exception as e:
        print(f"   ❌ Kayıt hatası: {e}")
        return False

def push_to_fly():
    """Push to Fly.io via GitHub"""
    try:
        os.chdir(REPO_PATH)
        
        print("\n📤 Fly.io'ya gönderiliyor...")
        print("   📝 Git konfigürasyonu...")
        subprocess.run(['git', 'config', 'user.email', 'bot@hosgoru.local'], 
                      capture_output=True, timeout=10)
        subprocess.run(['git', 'config', 'user.name', 'UpdateBot'], 
                      capture_output=True, timeout=10)
        
        print("   ➕ Dosya staging...")
        subprocess.run(['git', 'add', 'database.json'], 
                      capture_output=True, timeout=10)
        
        print("   💾 Commit...")
        commit_result = subprocess.run(
            ['git', 'commit', '-m', f'🤖 Sync from GitHub - {datetime.now().strftime("%Y-%m-%d %H:%M")}'],
            capture_output=True, text=True, timeout=10
        )
        
        if commit_result.returncode != 0:
            print("   ⚠️  Hiç değişiklik yok")
            return True
        
        print("   🚀 GitHub'a push...")
        push_result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            capture_output=True, text=True, timeout=30
        )
        
        if push_result.returncode == 0:
            print("   ✅ Push başarılı!")
            print("\n" + "="*60)
            print("⏳ Fly.io otomatik redeploy yapılıyor...")
            print("   Site: https://mgbric.fly.dev")
            print("   Bekleme süresi: ~1-2 dakika")
            print("="*60)
            return True
        else:
            print(f"   ❌ Push hatası: {push_result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Hata: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("🔄 GITHUB → FLY.IO SİNK")
    print("="*60 + "\n")
    
    # Step 1: Fetch from GitHub
    data = fetch_from_github()
    if not data:
        print("\n❌ İşlem başarısız!")
        exit(1)
    
    # Step 2: Save locally
    print("\n💾 Yerel olarak kaydediliyor...")
    if not save_database(data):
        print("\n❌ İşlem başarısız!")
        exit(1)
    
    # Step 3: Push to Fly.io
    if not push_to_fly():
        print("\n❌ İşlem başarısız!")
        exit(1)
    
    print("\n✅ TÜM İŞLEMLER TAMAMLANDI!")
