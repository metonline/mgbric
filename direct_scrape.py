#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class VugraphScraper:
    def __init__(self):
        self.base_url = "https://clubs.vugraph.com/hosgoru"
        self.session = requests.Session()
        
    def fetch_calendar(self):
        """Takvim sayfasından turnuva linklerini al"""
        try:
            url = f"{self.base_url}/calendar.php"
            print(f"📥 {url} açılıyor...")
            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Turnuva linklerini bul (href="/hosgoru/results.php?id=...")
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'results.php?id=' in href:
                    event_id = href.split('id=')[1].split('&')[0]
                    links.append(event_id)
            
            print(f"✅ {len(set(links))} benzersiz turnuva bulundu")
            return list(set(links))
        except Exception as e:
            print(f"❌ Takvim hatası: {e}")
            return []
    
    def fetch_results(self, event_id):
        """Turnuva sonuçlarını indir"""
        try:
            url = f"{self.base_url}/results.php?id={event_id}"
            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            print(f"❌ {event_id} indir hatası: {e}")
            return None
    
    def parse_record(self, row_html):
        """HTML satırını record'a çevir"""
        try:
            soup = BeautifulSoup(row_html, 'html.parser')
            cells = soup.find_all('td')
            
            if len(cells) < 6:
                return None
            
            # Veri çıkarma
            sira = cells[0].get_text(strip=True)
            oyuncu1 = cells[1].get_text(strip=True).upper()
            oyuncu2 = cells[2].get_text(strip=True).upper()
            skor = cells[3].get_text(strip=True)
            direction = cells[4].get_text(strip=True)  # NS or EW
            
            return {
                'Sıra': sira,
                'Oyuncu 1': oyuncu1,
                'Oyuncu 2': oyuncu2,
                'Skor': skor,
                'Direction': direction,
                'Turnuva': '',  # Placeholder
                'Tarih': '',    # Placeholder
                'Event No': ''
            }
        except:
            return None
    
    def scrape_all(self):
        """Tüm turnuvaları scrape et"""
        records = []
        event_ids = self.fetch_calendar()
        
        for i, event_id in enumerate(event_ids, 1):
            print(f"📊 [{i}/{len(event_ids)}] Event {event_id} işleniyor...")
            html = self.fetch_results(event_id)
            if not html:
                continue
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Tarih ve turnuva adı
            title = soup.find('h2')
            if title:
                title_text = title.get_text(strip=True)
                parts = title_text.rsplit(' ', 1)
                if len(parts) == 2:
                    turnuva = parts[0]
                    date_str = parts[1].strip('()')
                    try:
                        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                        tarih = date_obj.strftime('%d.%m.%Y')
                    except:
                        tarih = date_str
                else:
                    turnuva = title_text
                    tarih = ''
            else:
                continue
            
            # Sonuçları bul
            table = soup.find('table')
            if table:
                for tr in table.find_all('tr')[1:]:  # Başlık satırını atla
                    rec = self.parse_record(str(tr))
                    if rec:
                        rec['Turnuva'] = turnuva
                        rec['Tarih'] = tarih
                        rec['Event No'] = event_id
                        records.append(rec)
            
            print(f"  ✓ {len([r for r in records if r.get('Turnuva') == turnuva and r.get('Tarih') == tarih])} kayıt")
        
        return records

# Çalıştır
print('🔄 Vugraph\'tan verileri çekiliyor...')
scraper = VugraphScraper()
new_records = scraper.scrape_all()

print(f'\n✅ Toplam çekilen: {len(new_records)} kayıt')

# Database'yi yükle
with open('database.json', 'r', encoding='utf-8') as f:
    db_data = json.load(f)

initial_count = len(db_data)

# Duplikat kontrol ile ekle
added = 0
for rec in new_records:
    exists = any(
        r.get('Tarih') == rec.get('Tarih') and
        r.get('Oyuncu 1') == rec.get('Oyuncu 1') and
        r.get('Oyuncu 2') == rec.get('Oyuncu 2') and
        r.get('Skor') == rec.get('Skor')
        for r in db_data
    )
    if not exists:
        db_data.append(rec)
        added += 1

print(f'Eklenen yeni: {added}')
print(f'Toplam: {len(db_data)}')

# Kaydet
with open('database.json', 'w', encoding='utf-8') as f:
    json.dump(db_data, f, ensure_ascii=False, indent=2)

print('✅ database.json güncellendi')

# Kontrol
records_30_12 = [r for r in db_data if r.get('Tarih') == '30.12.2025']
print(f'\n30.12.2025: {len(records_30_12)} kayıt')
tournaments = set(r.get('Turnuva', '') for r in records_30_12)
for t in sorted(tournaments):
    count = len([r for r in records_30_12 if r.get('Turnuva') == t])
    print(f'  [{count}] {t}')
