from PIL import Image
import os

# Dosyaları aç ve transparent yap
files_to_process = [
    ('TR_flag.jpeg', 'TR_flag.png'),
    ('EN_flag.png', 'EN_flag_new.png'),
]

for input_file, output_file in files_to_process:
    if not os.path.exists(input_file):
        print(f"⚠️ {input_file} bulunamadı")
        continue
    
    print(f"📝 İşleniyor: {input_file}")
    
    # Resmi aç
    img = Image.open(input_file)
    
    # RGBA'ya çevir
    img = img.convert('RGBA')
    
    # Beyaz pikselleri transparentle değiştir
    data = img.getdata()
    new_data = []
    
    for item in data:
        # Beyaz pikselleri (R>240, G>240, B>240) transparentle değiştir
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((item[0], item[1], item[2], 0))  # Transparent
        else:
            new_data.append(item)
    
    img.putdata(new_data)
    img.save(output_file)
    print(f"✅ Kaydedildi: {output_file}")

print("\n✨ Tamamlandı!")
print("Yeni dosyaları FTP'ye yükle:")
print("  - TR_flag.png (eski: TR_flag.jpeg yerine)")
print("  - EN_flag_new.png (eski: EN_flag.png yerine)")
