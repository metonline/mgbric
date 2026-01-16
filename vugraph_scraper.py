#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vugraph Web Scraper
Hoşgörü Briç Kulübü - https://clubs.vugraph.com/hosgoru/
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from urllib.parse import urljoin

class VugraphScraper:
    BASE_URL = "https://clubs.vugraph.com/hosgoru"
    CALENDAR_URL = f"{BASE_URL}/calendar.php"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_calendar(self):
        """Takvim sayfasını indir ve linkleri çıkar"""
        try:
            print("📅 Takvim sayfası indiriliyor...")
            response = self.session.get(self.CALENDAR_URL, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tüm linkleri bul
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and 'results.php' in href:
                    full_url = urljoin(self.BASE_URL, href)
                    text = link.get_text(strip=True)
                    links.append({
                        'url': full_url,
                        'text': text
                    })
            
            print(f"✅ {len(links)} turnuva bulundu")
            return links
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            return []
    
    def fetch_results(self, url):
        """Turnuva sonuç sayfasını indir"""
        try:
            print(f"  📊 {url.split('=')[-1]} indiriliyor...")
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tabloları bul
            tables = soup.find_all('table')
            records = []
            
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 2:
                    continue
                
                # Başlıkları kontrol et
                headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                
                # Veri satırlarını işle
                for row in rows[1:]:
                    cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                    if len(cells) >= 5:
                        record = self.parse_record(cells, headers)
                        if record:
                            records.append(record)
            
            return records
            
        except Exception as e:
            print(f"  ❌ Hata: {e}")
            return []
    
    def parse_record(self, cells, headers):
        """Bir satırı kayda dönüştür"""
        try:
            # Tipik sütun sırası: Sıra, Tarih, Oyuncu1, Oyuncu2, Skor, Direction, Turnuva
            record = {}
            
            # Değerleri eşle
            if len(cells) >= 1:
                try:
                    record['Sıra'] = int(cells[0])
                except:
                    pass
            
            if len(cells) >= 2:
                record['Tarih'] = cells[1]  # Format: DD.MM.YYYY
            
            if len(cells) >= 3:
                record['Oyuncu 1'] = cells[2].upper()
            
            if len(cells) >= 4:
                record['Oyuncu 2'] = cells[3].upper()
            
            if len(cells) >= 5:
                try:
                    record['Skor'] = int(cells[4])
                except:
                    record['Skor'] = 0
            
            if len(cells) >= 6:
                direction = cells[5].strip().upper()
                if direction in ['NS', 'EW', 'N/S', 'E/W']:
                    record['Direction'] = direction.replace('/', '')
                else:
                    record['Direction'] = 'NS'
            
            if len(cells) >= 7:
                record['Turnuva'] = cells[6]
            else:
                record['Turnuva'] = 'Hosgoru'
            
            # Zorunlu alanları kontrol et
            if 'Tarih' in record and 'Oyuncu 1' in record and 'Oyuncu 2' in record:
                return record
            
            return None
            
        except Exception as e:
            return None
    
    def scrape_all(self):
        """Tüm turnuvaları scrape et"""
        all_records = []
        calendar_links = self.fetch_calendar()
        
        for i, link in enumerate(calendar_links, 1):
            print(f"\n[{i}/{len(calendar_links)}] {link['text']}")
            records = self.fetch_results(link['url'])
            all_records.extend(records)
            print(f"  ✅ {len(records)} kayıt eklendi (Toplam: {len(all_records)})")
        
        return all_records

if __name__ == '__main__':
    scraper = VugraphScraper()
    
    print("🔍 Vugraph Hoşgörü Briç Kulübü - Web Scraper\n")
    print("=" * 50)
    
    records = scraper.scrape_all()
    
    print("\n" + "=" * 50)
    print(f"\n✅ Toplam {len(records)} kayıt scrape edildi")
    
    if records:
        print(f"\n📋 İlk kayıt örneği:")
        print(json.dumps(records[0], ensure_ascii=False, indent=2))
