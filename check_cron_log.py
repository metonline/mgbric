#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FTP'den cron.log dosyasını indir ve göster
"""

from ftplib import FTP
import io

FTP_HOST = "ftp.mgbric.info"
FTP_USER = "mgb3dcinfo"
FTP_PASS = "34b2e-c68c17"
FTP_PATH = "/public_html/hosgoru/"

try:
    print("⏳ FTP'ye bağlanılıyor...")
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    print("✅ FTP bağlantısı başarılı\n")
    
    print(f"📁 {FTP_PATH} dizinine gidiliyor...")
    ftp.cwd(FTP_PATH)
    
    print("⏳ cron.log dosyası indirilyor...\n")
    
    # Dosyayı BytesIO'ye indir
    log_content = io.BytesIO()
    ftp.retrbinary('RETR cron.log', log_content.write)
    
    ftp.quit()
    
    # İçeriği göster
    log_text = log_content.getvalue().decode('utf-8', errors='ignore')
    
    # Son 50 satırı göster
    lines = log_text.split('\n')
    print(f"📋 Toplam satır: {len(lines)}\n")
    print("=" * 80)
    print("Son 50 satır:")
    print("=" * 80 + "\n")
    
    for line in lines[-50:]:
        if line.strip():
            print(line)
    
except Exception as e:
    print(f"❌ Hata: {e}")
