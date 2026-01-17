#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cron for automatic Vugraph data fetching and Fly.io deployment
"""

import os
import sys
import json
from datetime import datetime

# Add to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# Import fetcher
from vugraph_fetcher import VugraphDataFetcher
import subprocess

LOG_FILE = os.path.join(SCRIPT_DIR, 'cron_auto_fetch.log')

def log_message(msg):
    """Log message to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(full_msg + "\n")
    except:
        pass

def fetch_vugraph_data():
    """Fetch fresh data from Vugraph"""
    try:
        log_message("🔄 Vugraph'tan veri çekiliyor...")
        
        fetcher = VugraphDataFetcher()
        
        # Fetch from last 3 days + next 7 days
        from datetime import timedelta
        today = datetime.now()
        start_date = today - timedelta(days=3)
        end_date = today + timedelta(days=7)
        
        all_success = True
        total_records = 0
        
        # Loop through date range
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%d.%m.%Y')
            log_message(f"   📅 {date_str} çekiliyor...")
            
            try:
                success = fetcher.add_date_to_database(date_str)
                if success:
                    total_records += len(fetcher.records_added)
                    log_message(f"      ✅ {len(fetcher.records_added)} kayıt")
                else:
                    log_message(f"      ⚠️  Veri bulunamadı")
            except Exception as e:
                log_message(f"      ❌ Hata: {e}")
                all_success = False
            
            current_date += timedelta(days=1)
        
        if total_records > 0:
            log_message(f"   ✅ Toplam {total_records} kayıt çekildi")
            return True
        else:
            log_message(f"   ⚠️  Hiç veri çekilemedi")
            return False
            
    except Exception as e:
        log_message(f"   ❌ Hata: {e}")
        return False

def deploy_to_fly():
    """Deploy to Fly.io"""
    try:
        log_message("📤 Fly.io'ya deployment başlanıyor...")
        
        # Change to script directory
        os.chdir(SCRIPT_DIR)
        
        # Git operations
        subprocess.run(['git', 'config', 'user.email', 'cron@hosgoru.local'], 
                      capture_output=True, timeout=10)
        subprocess.run(['git', 'config', 'user.name', 'CronBot'], 
                      capture_output=True, timeout=10)
        
        # Add and commit
        subprocess.run(['git', 'add', 'database.json'], 
                      capture_output=True, timeout=10)
        
        commit_result = subprocess.run(
            ['git', 'commit', '-m', f'🤖 Cron auto-update {datetime.now().isoformat()}'],
            capture_output=True, text=True, timeout=10
        )
        
        if commit_result.returncode != 0:
            log_message("   ⚠️  Hiç değişiklik yok")
            return True
        
        # Push
        push_result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            capture_output=True, text=True, timeout=30
        )
        
        if push_result.returncode == 0:
            log_message("   ✅ Fly.io'ya gönderildi (redeploy aktif)")
            return True
        else:
            log_message(f"   ❌ Push hatası")
            return False
            
    except Exception as e:
        log_message(f"   ❌ Deployment hatası: {e}")
        return False

def main():
    """Main cron function"""
    log_message("=" * 60)
    log_message("🤖 CRON: OTOMATİK VUGRAPH VERİ GÜNCELLEME BAŞLADI")
    log_message("=" * 60)
    
    # Step 1: Fetch Vugraph data
    if not fetch_vugraph_data():
        log_message("❌ CRON BAŞARISIZ: Veri çekme hatası")
        log_message("=" * 60 + "\n")
        return False
    
    # Step 2: Deploy to Fly.io
    if not deploy_to_fly():
        log_message("❌ CRON BAŞARISIZ: Deployment hatası")
        log_message("=" * 60 + "\n")
        return False
    
    log_message("✅ CRON BAŞARILI: Veri güncellendi ve Fly.io'ya gönderildi")
    log_message("=" * 60 + "\n")
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        log_message(f"❌ KRITIK HATA: {e}")
        sys.exit(1)
