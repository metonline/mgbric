#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FTP üzerinden database.json'ı sunucuya yükle - Detaylı hata ayıklama
"""

from ftplib import FTP, all_errors
import os

# FTP Bilgileri
FTP_HOST = "mgbric.info"  # Veya ftp.mgbric.info
FTP_USER = "mgb3dcinfo"
FTP_PASS = "Amanos31!"
FTP_PATH = "/public_html/hosgoru/"
DB_FILE = r"C:\Users\metin\Desktop\BRIC\database.json"

print("📋 FTP Upload Script")
print(f"Host: {FTP_HOST}")
print(f"User: {FTP_USER}")
print(f"Path: {FTP_PATH}")
print(f"File: {DB_FILE}")
print(f"File size: {os.path.getsize(DB_FILE) / 1024 / 1024:.1f} MB")
print("-" * 60)

try:
    print("\n⏳ FTP'ye bağlanılıyor...")
    ftp = FTP()
    ftp.set_debuglevel(2)  # Detaylı log
    ftp.connect(FTP_HOST, 21, timeout=30)
    print("✅ Bağlantı başarılı")
    
    print("\n⏳ Giriş yapılıyor...")
    ftp.login(FTP_USER, FTP_PASS)
    print("✅ Giriş başarılı")
    
    print(f"\n⏳ {FTP_PATH} dizinine gidiliyor...")
    ftp.cwd(FTP_PATH)
    print("✅ Dizin değiştirildi")
    
    print("\n⏳ Dosya yükleniyor...")
    with open(DB_FILE, 'rb') as f:
        ftp.storbinary(f'STOR database.json', f, 8192)
    print("✅ Dosya yüklendi")
    
    print("\n⏳ Dosya doğrulanıyor...")
    remote_size = ftp.size('database.json')
    local_size = os.path.getsize(DB_FILE)
    print(f"Local: {local_size} bytes")
    print(f"Remote: {remote_size} bytes")
    
    if local_size == remote_size:
        print("✅ Dosyalar eşleşti!")
    else:
        print("⚠️ Dosya boyutları farklı!")
    
    ftp.quit()
    print("\n✅ İşlem başarılı!")
    
except all_errors as e:
    print(f"\n❌ FTP Hatası: {e}")
    print(f"   Tip: {type(e).__name__}")
except Exception as e:
    print(f"\n❌ Genel Hata: {e}")
    print(f"   Tip: {type(e).__name__}")
