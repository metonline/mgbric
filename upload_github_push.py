import ftplib

FTP_HOST = "ftp.mgbric.info"
FTP_USER = "mgb3dcinfo"
FTP_PASS = "34b2e-c68c17"

print("🔗 FTP bağlantısı...")
ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
ftp.cwd('/public_html/hosgoru')

files_to_upload = [
    ('auto_update_vugraph.py', r'C:\Users\metin\Desktop\BRIC\auto_update_vugraph.py'),
    ('.env.github', r'C:\Users\metin\Desktop\BRIC\.env.github'),
]

print("\n📤 Dosyalar yükleniyor...")
for remote_name, local_path in files_to_upload:
    try:
        with open(local_path, 'rb') as f:
            ftp.storbinary(f'STOR {remote_name}', f)
        print(f"✅ {remote_name}: OK")
    except Exception as e:
        print(f"❌ {remote_name}: {e}")

ftp.quit()
print("\n✨ Tamamlandı!")
print("⏰ 5 dakika sonra Cron yeniden çalışacak ve GitHub'a push yapacak")
