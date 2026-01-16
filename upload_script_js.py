import ftplib
import os

FTP_HOST = 'ftp.mgbric.info'
FTP_USER = 'mgb3dcinfo'
FTP_PASS = '34b2e-c68c17'
FTP_PATH = '/public_html/hosgoru/'

try:
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    print(f"🔗 FTP bağlantısı: {FTP_HOST}")
    
    ftp.cwd(FTP_PATH)
    
    with open('script.js', 'rb') as f:
        ftp.storbinary('STOR script.js', f)
    print(f"✅ script.js: OK")
    
    ftp.quit()
    print("\n✨ Tarih seçici güncellendi!")
    
except Exception as e:
    print(f"❌ FTP hatası: {e}")
