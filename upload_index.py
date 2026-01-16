import ftplib

FTP_HOST = "ftp.mgbric.info"
FTP_USER = "mgb3dcinfo"
FTP_PASS = "34b2e-c68c17"

print("🔗 FTP bağlantısı...")
ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
ftp.cwd('/public_html/hosgoru')

with open(r'C:\Users\metin\Desktop\BRIC\index.html', 'rb') as f:
    ftp.storbinary('STOR index.html', f)

print("✅ index.html: OK")
ftp.quit()
print("✨ Bayraklar sola kaydırıldı!")
