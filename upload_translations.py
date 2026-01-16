import ftplib

FTP_HOST = "ftp.mgbric.info"
FTP_USER = "mgb3dcinfo"
FTP_PASS = "34b2e-c68c17"

print("🔗 FTP bağlantısı...")
ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
ftp.cwd('/public_html/hosgoru')

files = [
    ('tr.json', r'C:\Users\metin\Desktop\BRIC\tr.json'),
    ('en.json', r'C:\Users\metin\Desktop\BRIC\en.json'),
]

for name, path in files:
    with open(path, 'rb') as f:
        ftp.storbinary(f'STOR {name}', f)
    print(f"✅ {name}: OK")

ftp.quit()
print("✨ Tamamlandı!")
