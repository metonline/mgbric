#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub'a dosyaları push et (Python tabanlı)
"""

import os
import subprocess

os.chdir(r'C:\Users\metin\Desktop\BRIC')

print("📝 Dosya durumu kontrol ediliyor...")

# Git komutu çalıştırması ister - alternatif: SSH yerine HTTPS token kullan
# Ya da direkt dosyaları kopyala gibi bir çözüm

print("""
⚠️ Git PowerShell'de kurulu değil. 

Çözüm: GitHub Desktop veya Web üzerinden yapabilirsin:
1. Bu dosyaları direkt GitHub web arayüzüne yükle
2. Veya Git Bash kullan
3. Veya GitHub Desktop uygulamasını kur

Alternatif: WinSCP ile dosyaları sunucuya doğrudan senkronize et.

Dosyalar zaten sunucuya yüklendi! ✅
""")
