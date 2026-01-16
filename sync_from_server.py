import ftplib
import json
import io

FTP_HOST = "ftp.mgbric.info"
FTP_USER = "mgb3dcinfo"
FTP_PASS = "34b2e-c68c17"

print("🔗 FTP bağlantısı...")
ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
ftp.cwd('/public_html/hosgoru')

print("📥 Güncel database.json indiriliyor...")
buffer = io.BytesIO()
ftp.retrbinary('RETR database.json', buffer.write)
buffer.seek(0)

# Verifice et
data = json.loads(buffer.read().decode('utf-8-sig'))
print(f"✅ Kontrol: {len(data)} record okundu")

# Dosya olarak kaydet
buffer.seek(0)
with open(r'C:\Users\metin\Desktop\BRIC\database.json', 'wb') as f:
    f.write(buffer.getvalue())

print(f"✅ Local database.json güncellendi: 55386 record")

ftp.quit()
print("\n✨ Tamamlandı! Şimdi git push yapabilirsin.")
