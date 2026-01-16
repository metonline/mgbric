import ftplib

FTP_HOST = "ftp.mgbric.info"
FTP_USER = "mgb3dcinfo"
FTP_PASS = "34b2e-c68c17"

print("🔗 FTP bağlantısı...")
ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
ftp.cwd('/public_html/hosgoru')

files_to_upload = [
    ('sync_design_from_github.py', r'C:\Users\metin\Desktop\BRIC\sync_design_from_github.py'),
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
