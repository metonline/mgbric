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
    
    # Yeni dosyaları yükle
    files = [
        ('TR_flag.png', 'TR_flag.png'),  # Eski: TR_flag.jpeg
        ('EN_flag_new.png', 'EN_flag.png'),  # EN_flag.png üzerine yaz
    ]
    
    ftp.cwd(FTP_PATH)
    
    for local_file, remote_file in files:
        if os.path.exists(local_file):
            with open(local_file, 'rb') as f:
                ftp.storbinary(f'STOR {remote_file}', f)
            print(f"✅ {remote_file}: OK")
        else:
            print(f"⚠️ {local_file} bulunamadı")
    
    ftp.quit()
    print("\n✨ Flag dosyaları güncellendi!")
    
except Exception as e:
    print(f"❌ FTP hatası: {e}")
