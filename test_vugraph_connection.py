#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Vugraph connection and data fetching
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://clubs.vugraph.com/hosgoru"

print("="*60)
print("🔍 VUGRAPH BAĞLANTISI TEST")
print("="*60 + "\n")

# Test 1: Calendar
print("1️⃣  Takvim sayfası kontrol ediliyor...")
try:
    response = requests.get(f"{BASE_URL}/calendar.php", timeout=10)
    response.raise_for_status()
    print(f"   ✅ Bağlantı başarılı (Status: {response.status_code})")
    print(f"   ✅ Sayfa boyutu: {len(response.text)} bytes")
    
    # Parse for events
    soup = BeautifulSoup(response.text, 'html.parser')
    events = []
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        if 'eventresults.php?event=' in href:
            event_id = href.split('event=')[1].split('&')[0]
            text = link.get_text(strip=True)
            events.append((event_id, text))
    
    print(f"   ✅ {len(events)} etkinlik bulundu")
    if events:
        print(f"\n   📋 İlk 3 etkinlik:")
        for event_id, name in events[:3]:
            print(f"      • Event {event_id}: {name}")
except Exception as e:
    print(f"   ❌ Hata: {e}")

# Test 2: Event details
if events:
    print(f"\n2️⃣  Event detayları çekiliyor (Event {events[0][0]})...")
    try:
        event_id = events[0][0]
        url = f"{BASE_URL}/eventresults.php?event={event_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"   ✅ Event sayfası alındı (Status: {response.status_code})")
        print(f"   ✅ Sayfa boyutu: {len(response.text)} bytes")
        
        # Check for table structure
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', class_='colored')
        print(f"   ✅ {len(tables)} tablo bulundu")
        
    except Exception as e:
        print(f"   ❌ Hata: {e}")
else:
    print(f"\n2️⃣  Hiç etkinlik bulunamadı, detay çekme atlandi")

print("\n" + "="*60)
print("✅ TEST TAMAMLANDI")
print("="*60)
