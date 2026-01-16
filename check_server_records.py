import ftplib
import json
import io

FTP_HOST = "ftp.mgbric.info"
FTP_USER = "mgb3dcinfo"
FTP_PASS = "34b2e-c68c17"

print("🔗 FTP bağlantısı...")
ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
ftp.cwd('/public_html/hosgoru')

print("📥 database.json indiriliyor...")
buffer = io.BytesIO()
ftp.retrbinary('RETR database.json', buffer.write)
buffer.seek(0)

data = json.loads(buffer.read().decode('utf-8-sig'))
print(f"✅ Sunucuda: {len(data)} record")

dates = sorted(set([r.get('Tarih') for r in data if r.get('Tarih')]), 
               key=lambda x: tuple(map(int, x.split('.')[::-1])))
print(f"📅 Son tarih: {dates[-1] if dates else 'N/A'}")

ftp.quit()

print(f"\n⚠️  FARK: Sunucuda {len(data) - 55329} record daha var!")
