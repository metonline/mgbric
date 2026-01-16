"""
Modül: Hoşgörü Briç Kulübü Takvim Tarayıcı

TR (Türkçe):
- Amaç: Hoşgörü Briç Kulübü takviminden turnuva sonuçlarını çekmek ve mevcut veritabanı ile birleştirmek.
- Kullanım:
    1) Komut satırı: `python run_bot.py` (önerilir)
    2) Programatik: `hosgoru_takvim_tara()` fonksiyonunu çağırın.
- Çıktı: Çalışma dizininde `database.xlsx` dosyası güncellenir/oluşturulur (sayfa adı: `Sonuçlar`).
- Gereksinimler: `pandas`, `requests`, `beautifulsoup4`.

EN (English):
- Purpose: Fetch tournament results from the Hoşgörü Bridge Club calendar and merge with the existing database.
- Usage:
    1) CLI: `python run_bot.py` (recommended)
    2) Programmatic: call `hosgoru_takvim_tara()`.
- Output: Updates/creates `database.xlsx` in the working directory (sheet name: `Sonuçlar`).
- Requirements: `pandas`, `requests`, `beautifulsoup4`.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import os
from datetime import datetime
import urllib3

# SSL uyarılarını bastır
# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def hosgoru_takvim_tara():
    """
    Hoşgörü Briç Kulübü takviminden turnuva sonuçlarını çeker
    Kullanıcının seçtiği yıllar için mevcut verilerle birleştir
    
    Fetches tournament results from Hoşgörü Bridge Club calendar
    Merges with existing data for user-selected years
    """
    lang = os.getenv('HOSGORU_LANG', 'tr').lower()
    def L(tr, en):
        return tr if lang == 'tr' else en

    print("=" * 60)
    print(L("HOŞGÖRÜ BRİÇ KULÜBÜ - TAKVİM TARAYICI", "HOSGORU BRIDGE CLUB - CALENDAR SCRAPER"))
    print("=" * 60)
    
    # Sadece mevcut yılı (2025) tarayarak yeni verileri ekle
    # Auto-process current year (2025) to add new data only
    baslangic_yili = 2025
    bitis_yili = 2025
    
    print(L(f"\n✓ Seçilen aralık: {baslangic_yili} - {bitis_yili}", f"\n✓ Selected range: {baslangic_yili} - {bitis_yili}"))
    print("=" * 60)
    
    base_url = "https://clubs.vugraph.com/hosgoru/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    tum_kayitlar = []
    mevcut_record_ids = set()  # Mevcut kaydı takip et (Link+Sıra kombinasyonu)
    # Track existing records (Link+Rank combination)
    
    # Mevcut database.xlsx'i oku (varsa)
    # Read existing database.xlsx if present
    dosya_adi = "database.xlsx"
    if os.path.exists(dosya_adi):
        print(f"\n[0] Mevcut database yükleniyor: {dosya_adi}")
        try:
            df_mevcut = pd.read_excel(dosya_adi)
            tum_kayitlar = df_mevcut.to_dict('records')
            # Link + Sıra + Direction kombinasyonuna göre benzersiz kimlikleri oluştur
            # Create unique IDs based on Link + Rank + Direction combination
            if 'Link' in df_mevcut.columns and 'Sıra' in df_mevcut.columns and 'Direction' in df_mevcut.columns:
                mevcut_record_ids = set(
                    f"{row['Link']}|{row['Sıra']}|{row['Direction']}" 
                    for _, row in df_mevcut.iterrows()
                )
            elif 'Link' in df_mevcut.columns and 'Sıra' in df_mevcut.columns:
                # Fallback eski database'ler için (Direction sütunu yoksa)
                # Fallback for old databases (if Direction column doesn't exist)
                mevcut_record_ids = set(
                    f"{row['Link']}|{row['Sıra']}" 
                    for _, row in df_mevcut.iterrows()
                )
            print(f"    ✓ {len(tum_kayitlar)} mevcut kayıt yüklendi")
        except Exception as e:
            print(f"    X Hata: {e}")
            tum_kayitlar = []
            mevcut_record_ids = set()
    
    try:
        # Kullanıcının seçtiği yılları tara
        # Crawl calendar pages for selected years
        print(f"\n[1] Takvim sayfaları taranıyor...\n")
        
        benzersiz_linkler = {}
        
        # Dinamik yıl aralığı
        # Dynamic year range
        yillar = list(range(baslangic_yili, bitis_yili + 1))
        
        for yil in yillar:
            for ay in range(1, 13):
                # Takvim URL'si - ay parametresiyle
                # Calendar URL with month parameter
                takvim_url = f"https://clubs.vugraph.com/hosgoru/calendar.php?year={yil}&month={ay}"
                
                print(L(f"   Ay {ay:02d}/{yil} taranıyor...", f"   Scanning month {ay:02d}/{yil}..."))
                
                try:
                    try:
                        response = requests.get(takvim_url, headers=headers, timeout=30, verify=False)
                    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.SSLError) as e:
                        print(L("      X Bağlantı hatası, atlanıyor...", "      X Connection error, skipping..."))
                        time.sleep(3)
                        continue
                    
                    if response.status_code != 200:
                        print(L(f"      X Sayfa yüklenemedi (Status: {response.status_code})", f"      X Page failed to load (Status: {response.status_code})"))
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Bu aydaki turnuva linklerini bul
                    # Find tournament links in this month
                    ay_link_sayisi = 0
                    
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if 'results.php' in href and 'event=' in href:
                            if not href.startswith('http'):
                                href = base_url + href
                            
                            # Link metninden tarihi ve günü almaya çalış
                            # Try to derive date and day from link text
                            link_text = link.get_text(strip=True)
                            
                            if href not in benzersiz_linkler:
                                benzersiz_linkler[href] = link_text
                                ay_link_sayisi += 1
                    
                    print(L(f"      ✓ {ay_link_sayisi} turnuva bulundu", f"      ✓ {ay_link_sayisi} tournaments found"))
                    time.sleep(0.3)  # Sunucuya yük bindirmemek için
                    # Be gentle with the server
                    
                except Exception as e:
                    print(L(f"      X Hata: {str(e)[:40]}", f"      X Error: {str(e)[:40]}"))
                    continue
        
        print(L(f"\n[2] TOPLAM BULUNAN TURNUVA: {len(benzersiz_linkler)}", f"\n[2] TOTAL TOURNAMENTS FOUND: {len(benzersiz_linkler)}"))
        
        if len(benzersiz_linkler) == 0:
            print(L("\nUYARI: Hiç turnuva linki bulunamadı!", "\nWARNING: No tournament links found!"))
            print(L("Sayfanın yapısı değişmiş olabilir veya 2025 verisi yok.", "The page structure may have changed or there is no 2025 data."))
            return
        
        print(L("\n[3] Turnuvalar taranıyor...\n", "\n[3] Crawling tournaments...\n"))
        
        sayac = 0
        toplam = len(benzersiz_linkler)
        
        for turnuva_url, turnuva_adi in benzersiz_linkler.items():
            sayac += 1
            print(L(f"   [{sayac}/{toplam}] {turnuva_adi[:50]}...", f"   [{sayac}/{toplam}] {turnuva_adi[:50]}..."))
            
            try:
                time.sleep(0.5)  # Sunucuya yük bindirmemek için
                
                resp = None
                try:
                    resp = requests.get(turnuva_url, headers=headers, timeout=30, stream=False, verify=False)
                    # İçeriği hemen oku
                    # Read content immediately
                    content = resp.content
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, 
                        requests.exceptions.SSLError, requests.exceptions.RequestException,
                        KeyboardInterrupt) as e:
                    # Bağlantı hatası, timeout, SSL hatası vs.
                    # Connection error, timeout, SSL error, etc.
                    print(L("      X Hata çekme: atlanıyor...", "      X Fetch error: skipping..."))
                    time.sleep(3)  # Biraz bekle / Wait a bit
                    continue
                except Exception as e:
                    # Diğer hatalar
                    # Other exceptions
                    print(L("      X Bilinmeyen hata: atlanıyor...", "      X Unknown error: skipping..."))
                    time.sleep(2)
                    continue
                
                if resp is None or resp.status_code != 200:
                    print(L("      X Sayfa yüklenemedi", "      X Page failed to load"))
                    continue
                
                try:
                    soup_turnuva = BeautifulSoup(content, 'html.parser')
                except Exception as e:
                    print(L("      X Parse hatası: atlanıyor...", "      X Parse error: skipping..."))
                    continue
                
                # Turnuva adı ve tarih - ÖNCE H3'ten dene
                # Tournament title and date — try H3 first
                tarih = "Tarih Yok"
                baslik_text = turnuva_adi
                
                # H3 etiketini bul (BİNZET Anma Turnuvası Sonuçları (19-12-2025 14:00))
                # Find H3 tag (e.g., BINZET Memorial Tournament Results (19-12-2025 14:00))
                h3 = soup_turnuva.find('h3')
                if h3:
                    h3_text = h3.get_text(strip=True)
                    baslik_text = h3_text
                    
                    # Parantez içindeki tarih ve saati bul (19-12-2025 14:00) - SADECE TARİH AL
                    # Find date/time inside parentheses — take only the date
                    tarih_match = re.search(r'\((\d{2}-\d{2}-\d{4})', h3_text)
                    if tarih_match:
                        tarih = tarih_match.group(1).replace('-', '.')
                
                # H3'te bulunamadıysa başka yerlere bak
                # If not found in H3, check other elements
                if tarih == "Tarih Yok":
                    baslik = soup_turnuva.find('div', class_='event-title')
                    if not baslik:
                        baslik = soup_turnuva.find('h1') or soup_turnuva.find('title')
                    
                    if baslik:
                        baslik_text = baslik.get_text(strip=True)
                    
                    # GG-AA-YYYY veya GG.AA.YYYY formatı
                    # DD-MM-YYYY or DD.MM.YYYY format
                    tarih_match = re.search(r'(\d{2}[-.]\d{2}[-.]\d{4})', baslik_text)
                    if tarih_match:
                        tarih = tarih_match.group(1).replace('-', '.')
                
                # Tüm satırları bul (tr etiketleri)
                # Find all rows (tr tags)
                satirlar = soup_turnuva.find_all('tr')
                
                bulunan_kayit = 0
                
                for tr in satirlar:
                    onclick = tr.get('onclick', '')
                    
                    # onclick içinde direction= olanları bul
                    # Find rows with "direction=" in onclick
                    if 'direction=' in onclick:
                        # Direction'ı çıkar (NS veya EW)
                        # Extract direction (NS or EW)
                        direction_match = re.search(r'direction=([A-Z]+)', onclick)
                        direction = direction_match.group(1) if direction_match else "UNKNOWN"
                        
                        # Hücreleri al
                        # Get cells
                        cells = tr.find_all('td')
                        
                        if len(cells) >= 3:
                            try:
                                # Sıra
                                # Rank
                                sira_text = cells[0].get_text(strip=True)
                                sira = sira_text.replace('.', '')
                                if not sira.isdigit():
                                    continue
                                
                                # İsimler
                                # Names
                                isimler = cells[1].get_text(strip=True)
                                
                                # Oyuncu 1 ve 2'yi ayır
                                # Split Player 1 and Player 2
                                if ' - ' in isimler:
                                    oyuncu1, oyuncu2 = isimler.split(' - ', 1)
                                else:
                                    oyuncu1 = isimler
                                    oyuncu2 = ""
                                
                                # Skor
                                # Score
                                skor = cells[2].get_text(strip=True)
                                
                                # Duplicate check - Link + Sıra kombinasyonuna göre kontrol et
                                # Duplicate check — check by Link + Rank combination
                                kayit = {
                                    'Sıra': int(sira),
                                    'Tarih': tarih,
                                    'Oyuncu 1': oyuncu1.strip(),
                                    'Oyuncu 2': oyuncu2.strip(),
                                    'Skor': skor,
                                    'Direction': direction,
                                    'Turnuva': baslik_text,
                                    'Link': turnuva_url
                                }
                                
                                # Link+Sıra+Direction kombinasyonuna göre kontrol et
                                # Check by Link+Rank+Direction combination
                                record_id = f"{turnuva_url}|{sira}|{direction}"
                                if record_id not in mevcut_record_ids:
                                    tum_kayitlar.append(kayit)
                                    mevcut_record_ids.add(record_id)
                                    bulunan_kayit += 1
                                
                            except Exception as e:
                                continue
                
                if bulunan_kayit > 0:
                    print(L(f"      ✓ {bulunan_kayit} kayıt eklendi", f"      ✓ {bulunan_kayit} records added"))
                else:
                    print(L("      - Kayıt bulunamadı", "      - No records found"))
                    
            except Exception as e:
                print(L(f"      X Hata: {str(e)[:50]}", f"      X Error: {str(e)[:50]}"))
                continue
        
        # Excel'e kaydet
        # Save to Excel
        if len(tum_kayitlar) == 0:
            print("\n" + "=" * 60)
            print(L("UYARI: Hiç kayıt bulunamadı!", "WARNING: No records found!"))
            print("=" * 60)
            return
        
        print("\n" + "=" * 60)
        print(L("[4] EXCEL DOSYASI OLUŞTURULUYOR...", "[4] CREATING EXCEL FILE..."))
        print(L(f"    Toplam kayıt sayısı: {len(tum_kayitlar)}", f"    Total records: {len(tum_kayitlar)}"))
        
        df = pd.DataFrame(tum_kayitlar)
        
        # Sütun sırası
        # Column order
        sutunlar = ['Sıra', 'Tarih', 'Oyuncu 1', 'Oyuncu 2', 'Skor', 'Direction', 'Turnuva', 'Link']
        df = df[sutunlar]
        
        # Dosya adı - SABİT (database)
        # File name — fixed (database)
        dosya_adi = "database.xlsx"
        
        # Excel'e kaydet
        df.to_excel(dosya_adi, index=False, sheet_name='Sonuçlar')
        
        print(L(f"    ✓ Dosya kaydedildi: {dosya_adi}", f"    ✓ File saved: {dosya_adi}"))
        print("=" * 60)
        print(L("İŞLEM TAMAMLANDI!", "PROCESS COMPLETED!"))
        print("=" * 60)
        
    except Exception as e:
        print(L(f"\nKRİTİK HATA: {e}", f"\nCRITICAL ERROR: {e}"))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    hosgoru_takvim_tara()
