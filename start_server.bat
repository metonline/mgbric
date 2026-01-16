REM --- Auto-copy temp database to main if needed ---
python startup_copy_db.py
@echo off
REM Flask sunucusunu arka planda başlat
REM Bu dosya C:\Users\metin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup dosyasına kopylanmalı

cd /d "C:\Users\metin\Desktop\BRİÇ"
start /b python scheduled_server.py

REM Alternatif: pythonw.exe kullan (pencere gösterme)
REM start pythonw.exe scheduled_server.py
