#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FTP üzerinden düzeltilmiş dosyaları sunucuya yükle
"""

from ftplib import FTP
import os

# FTP Bilgileri
FTP_HOST = "ftp.mgbric.info"
FTP_USER = "mgb3dcinfo"
FTP_PASS = "34b2e-c68c17"
FTP_PATH = "/public_html/hosgoru/"

# Yüklenecek dosyalar
FILES_TO_UPLOAD = [
    'auto_update_vugraph.py',
    'vugraph_fetcher.py',
    'script.js',
    'tr.json',
    'en.json',
]

def upload_files():
    """FTP üzerinden dosyaları yükle"""
    try:
        # FTP bağlantısı
        ftp = FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print(f"✅ FTP bağlantısı başarılı: {FTP_HOST}")
        
        # Dizine git
        ftp.cwd(FTP_PATH)
        print(f"📁 Çalışma dizini: {FTP_PATH}")
        
        # Dosyaları yükle
        for filename in FILES_TO_UPLOAD:
            filepath = os.path.join(os.path.dirname(__file__), filename)
            
            if not os.path.exists(filepath):
                print(f"❌ Dosya bulunamadı: {filepath}")
                continue
            
            print(f"\n⏳ Yükleniyor: {filename}...", end=" ")
            with open(filepath, 'rb') as f:
                ftp.storbinary(f'STOR {filename}', f)
            print("✅ Tamamlandı")
        
        # Bağlantıyı kapat
        ftp.quit()
        print("\n✅ Tüm dosyalar başarıyla yüklendi!")
        return True
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        return False

if __name__ == "__main__":
    upload_files()
