#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions için otomatik Vugraph güncelleme scripti
"""

import json
import sys
import socket
import os
from datetime import datetime, timedelta

# Add current directory to path so modules can be imported
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
DB_FILE = os.path.join(SCRIPT_DIR, 'database.json')

from vugraph_fetcher import VugraphDataFetcher

# Timeout ayarları
socket.setdefaulttimeout(30)

def get_last_tournament_date():
    """Database'den en son turnuva tarihini al"""
    try:
        with open(DB_FILE, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        if data:
            # En son eklenmiş kayıttan tarihi al
            latest = sorted(data, key=lambda x: x.get('Tarih', ''), reverse=True)[0]
            return latest.get('Tarih')
    except Exception as e:
        print(f"⚠️ Database okunamadı: {e}")
    return None

def get_upcoming_dates(start_date=None, days_ahead=7, days_back=3):
    """
    Belirtilen aralıktaki turnuva tarihlerini al (geçmiş + gelecek)
    
    Parameters:
    - start_date: başlangıç tarihi (varsayılan: bugün)
    - days_ahead: kaç gün ileri bakılacak (varsayılan: 7)
    - days_back: kaç gün geriye bakılacak (varsayılan: 3)
    """
    if start_date:
        try:
            current = datetime.strptime(start_date, "%d.%m.%Y")
        except:
            current = datetime.now()
    else:
        current = datetime.now()
    
    dates = []
    
    # Geçmiş tarihleri ekle (en eski önce)
    for i in range(days_back, 0, -1):
        check_date = current - timedelta(days=i)
        dates.append(check_date.strftime("%d.%m.%Y"))
    
    # Bugün ve ileri tarihleri ekle
    for i in range(days_ahead + 1):
        check_date = current + timedelta(days=i)
        dates.append(check_date.strftime("%d.%m.%Y"))
    
    return dates

def main():
    print("="*60)
    print("🤖 GitHub Actions - Vugraph Veritabanı Güncelleme")
    print(f"⏰ Çalışma Saati: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        fetcher = VugraphDataFetcher()
    except Exception as e:
        print(f"❌ VugraphDataFetcher başlatılamadı: {e}")
        return 1
    
    # En son turnuva tarihini kontrol et
    last_date = get_last_tournament_date()
    print(f"\n📅 Son kaydedilen tarih: {last_date or 'Bulunamadı'}")
    
    # Kontrol edilecek tarihleri al (son 3 gün + sonraki 7 gün)
    upcoming_dates = get_upcoming_dates(days_back=3, days_ahead=7)
    print(f"\n🔍 Kontrol edilecek tarihler ({len(upcoming_dates)} gün):")
    for date in upcoming_dates:
        print(f"   • {date}")
    
    # Her tarih için veri çekmeyi dene
    success_count = 0
    error_count = 0
    
    for tarih in upcoming_dates:
        print(f"\n⏳ {tarih} için veri çekiliyor...")
        
        try:
            result = fetcher.add_date_to_database(tarih)
            if result:
                success_count += 1
                print(f"   ✓ {tarih} başarıyla güncellendi")
            else:
                print(f"   ℹ️ {tarih} için yeni veri yok")
        except socket.timeout:
            error_count += 1
            print(f"   ⚠️ {tarih} için timeout (30s)")
        except Exception as e:
            error_count += 1
            print(f"   ✗ {tarih} için hata: {str(e)[:100]}")
    
    # Özet
    print(f"\n{'='*60}")
    print(f"📊 Güncelleme Özeti:")
    print(f"   ✓ Başarılı: {success_count}/{len(upcoming_dates)} tarih")
    print(f"   ✗ Hatalı: {error_count}/{len(upcoming_dates)} tarih")
    
    if hasattr(fetcher, 'errors') and fetcher.errors:
        print(f"\n⚠️  Uyarılar (ilk 5):")
        for error in fetcher.errors[:5]:
            print(f"   • {str(error)[:80]}")
    
    print(f"{'='*60}\n")
    
    # Başarı durumunu döndür
    if success_count > 0:
        print("✅ Güncelleme başarılı!")
        return 0
    else:
        print("⚠️ Hiçbir yeni veri bulunamadı")
        return 0  # Veri yok da hata sayılmaz

if __name__ == "__main__":
    sys.exit(main())
