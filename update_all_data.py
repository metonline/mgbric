#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🃏 BRIC - Unified Data Update Pipeline
======================================

Bu script tüm veri güncelleme işlemlerini tek komutla yapar:
1. Vugraph takviminden yeni turnuvaları bul
2. Turnuva sonuçlarını (oyuncu skorları) database.json'a ekle
3. El verilerini (kartları) hands_database.json'a ekle
4. Eksik DD verilerini hesapla ve dd_results.json'a ekle

Kullanım:
    python update_all_data.py              # Tüm adımları çalıştır
    python update_all_data.py --check      # Sadece durumu kontrol et
    python update_all_data.py --dd-only    # Sadece eksik DD'leri hesapla
    python update_all_data.py --hands-only # Sadece eksik el verilerini al
    python update_all_data.py --scores-only # Sadece turnuva sonuçlarını al

Gereksinimler:
    - Python 3.12 (endplay için): .venv312/Scripts/python.exe
    - requests, beautifulsoup4, endplay
"""

import json
import sys
import os
import argparse
import requests
import re
import time
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime

# Dosya yolları
BASE_DIR = Path(__file__).parent
HANDS_DB_PATH = BASE_DIR / "hands_database.json"
DD_RESULTS_PATH = BASE_DIR / "double_dummy" / "dd_results.json"
DATABASE_PATH = BASE_DIR / "database.json"

VUGRAPH_BASE_URL = "https://clubs.vugraph.com/hosgoru"

def print_header(text):
    print()
    print("=" * 60)
    print(f"🃏 {text}")
    print("=" * 60)

def print_status(label, value, ok=True):
    icon = "✅" if ok else "⚠️"
    print(f"  {icon} {label}: {value}")

def load_json(path):
    """JSON dosyasını yükle"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return None

def save_json(path, data):
    """JSON dosyasını kaydet"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_hands_dates():
    """hands_database.json'daki tarihleri ve event_id'leri al"""
    data = load_json(HANDS_DB_PATH)
    if not data:
        return {}, set()
    
    # event_id -> tarih mapping
    event_map = {}
    dates = set()
    for h in data:
        tarih = h.get('Tarih', '')
        event_id = h.get('event_id', '')
        if tarih:
            dates.add(tarih)
        if event_id and tarih:
            event_map[event_id] = tarih
    
    return event_map, dates

def get_dd_dates():
    """dd_results.json'daki tarihleri al"""
    data = load_json(DD_RESULTS_PATH)
    if not data:
        return set()
    return set(r.get('date', '') for r in data if r.get('date'))

def get_vugraph_calendar_events():
    """Vugraph takviminden tüm eventleri al"""
    try:
        response = requests.get(f"{VUGRAPH_BASE_URL}/calendar.php", timeout=30)
        response.encoding = 'iso-8859-9'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        events = []
        
        # Ay ve yılı bul
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        header = soup.find('th', colspan=True) or soup.find('td', class_='banner')
        if header:
            header_text = header.get_text(strip=True).lower()
            months_tr = {'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4, 'mayıs': 5, 'haziran': 6,
                        'temmuz': 7, 'ağustos': 8, 'eylül': 9, 'ekim': 10, 'kasım': 11, 'aralık': 12}
            for month_name, month_num in months_tr.items():
                if month_name in header_text:
                    current_month = month_num
                    break
            year_match = re.search(r'20\d{2}', header_text)
            if year_match:
                current_year = int(year_match.group())
        
        # Event linklerini bul
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'eventresults.php?event=' in href:
                event_id = href.split('event=')[1].split('&')[0]
                
                # Tarihi bul - parent cell'den
                parent_td = link.find_parent('td', class_='days')
                if parent_td:
                    day_cell = parent_td.find('td', class_='days2')
                    if day_cell:
                        try:
                            day = int(day_cell.get_text(strip=True))
                            tarih = f"{day:02d}.{current_month:02d}.{current_year}"
                            events.append({
                                'event_id': event_id,
                                'tarih': tarih,
                                'name': link.get_text(strip=True)
                            })
                        except:
                            pass
        
        return events
    except Exception as e:
        print(f"  ❌ Takvim alınamadı: {e}")
        return []

def extract_hands_from_vugraph(event_id, board_num):
    """Vugraph'tan belirli bir board'un el verilerini al"""
    url = f"{VUGRAPH_BASE_URL}/boarddetails.php?event={event_id}&section=A&pair=1&direction=NS&board={board_num}"
    
    try:
        response = requests.get(url, timeout=15)
        response.encoding = 'iso-8859-9'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        bridge_table = soup.find('table', class_='bridgetable')
        if not bridge_table:
            return None
        
        player_cells = bridge_table.find_all('td', class_='oyuncu')
        if len(player_cells) < 4:
            return None
        
        hands = {}
        directions = ['W', 'N', 'E', 'S']  # Vugraph cell order
        
        for idx, cell in enumerate(player_cells[:4]):
            direction = directions[idx]
            suits = {'S': '', 'H': '', 'D': '', 'C': ''}
            
            for img in cell.find_all('img'):
                alt = img.get('alt', '').lower()
                suit = None
                if 'spade' in alt: suit = 'S'
                elif 'heart' in alt: suit = 'H'
                elif 'diamond' in alt: suit = 'D'
                elif 'club' in alt: suit = 'C'
                
                if suit:
                    next_elem = img.next_sibling
                    cards = ''
                    while next_elem:
                        if isinstance(next_elem, str):
                            text = next_elem.strip()
                            if text and not text.startswith('<'):
                                cards = text.replace(' ', '')
                                break
                        elif hasattr(next_elem, 'name') and next_elem.name == 'img':
                            break
                        next_elem = next_elem.next_sibling if hasattr(next_elem, 'next_sibling') else None
                    suits[suit] = cards.replace('-', '')
            
            # BBO format: S.H.D.C
            hands[direction] = f"{suits['S']}.{suits['H']}.{suits['D']}.{suits['C']}"
        
        return hands
    except Exception as e:
        return None

def fetch_missing_hands(missing_events):
    """Eksik el verilerini Vugraph'tan al"""
    print_header("Eksik El Verilerini Al")
    
    if not missing_events:
        print("  ✅ Tüm el verileri mevcut")
        return True
    
    print(f"  📅 {len(missing_events)} yeni event bulundu")
    
    # Mevcut hands database'i yükle
    hands_db = load_json(HANDS_DB_PATH) or []
    existing_keys = set(f"{h.get('event_id')}_{h.get('Board')}" for h in hands_db)
    
    total_added = 0
    
    for event in missing_events:
        event_id = event['event_id']
        tarih = event['tarih']
        print(f"\n  📆 {tarih} (Event: {event_id})")
        
        for board_num in range(1, 31):
            key = f"{event_id}_{board_num}"
            if key in existing_keys:
                continue
            
            print(f"    Board {board_num}...", end=' ')
            hands = extract_hands_from_vugraph(event_id, board_num)
            
            if hands:
                new_record = {
                    'event_id': event_id,
                    'Tarih': tarih,
                    'Board': board_num,
                    'N': hands.get('N', ''),
                    'S': hands.get('S', ''),
                    'E': hands.get('E', ''),
                    'W': hands.get('W', ''),
                    'Dealer': '',
                    'Vuln': ''
                }
                hands_db.append(new_record)
                existing_keys.add(key)
                print("✅")
                total_added += 1
            else:
                print("❌")
            
            time.sleep(0.1)
    
    if total_added > 0:
        # Tarihe ve board'a göre sırala
        def sort_key(h):
            tarih = h.get('Tarih', '01.01.2000')
            parts = tarih.split('.')
            if len(parts) == 3:
                return (int(parts[2]), int(parts[1]), int(parts[0]), h.get('Board', 0))
            return (0, 0, 0, 0)
        
        hands_db.sort(key=sort_key)
        save_json(HANDS_DB_PATH, hands_db)
        print(f"\n  ✅ {total_added} yeni el eklendi (Toplam: {len(hands_db)})")
    
    return True

def check_status():
    """Mevcut durumu kontrol et ve eksik verileri bul"""
    print_header("Mevcut Durum")
    
    # database.json (turnuva sonuçları)
    db_data = load_json(DATABASE_PATH)
    db_dates = set()
    if db_data and isinstance(db_data, dict):
        legacy = db_data.get('legacy_records', [])
        if legacy:
            db_dates = set(r.get('Tarih', '') for r in legacy if r.get('Tarih'))
            print_status("database.json", f"{len(legacy)} skor kaydı, {len(db_dates)} tarih")
            if db_dates:
                print(f"      Tarihler: {min(db_dates)} - {max(db_dates)}")
    else:
        print_status("database.json", "Boş veya bulunamadı", False)
    
    # hands_database.json
    hands_data = load_json(HANDS_DB_PATH)
    if hands_data:
        hands_dates = set(h.get('Tarih', '') for h in hands_data if h.get('Tarih'))
        hands_events = set(h.get('event_id', '') for h in hands_data if h.get('event_id'))
        print_status("hands_database.json", f"{len(hands_data)} el, {len(hands_dates)} tarih")
        print(f"      Tarihler: {min(hands_dates)} - {max(hands_dates)}")
    else:
        print_status("hands_database.json", "Bulunamadı!", False)
        hands_dates = set()
        hands_events = set()
    
    # dd_results.json
    dd_data = load_json(DD_RESULTS_PATH)
    if dd_data:
        dd_dates = set(r.get('date', '') for r in dd_data if r.get('date'))
        print_status("dd_results.json", f"{len(dd_data)} kayıt, {len(dd_dates)} tarih")
        print(f"      Tarihler: {min(dd_dates)} - {max(dd_dates)}")
    else:
        print_status("dd_results.json", "Bulunamadı!", False)
        dd_dates = set()
    
    # Vugraph takviminden yeni eventleri kontrol et
    print("\n  🔍 Vugraph takvimi kontrol ediliyor...")
    calendar_events = get_vugraph_calendar_events()
    
    # Eksik tarihleri bul (aynı tarihte birden fazla event olabilir, tarih bazlı kontrol)
    calendar_dates = set(e['tarih'] for e in calendar_events)
    
    # Eksik turnuva sonuçları
    missing_scores = calendar_dates - db_dates
    if missing_scores:
        print_status("Eksik turnuva sonuçları", f"{len(missing_scores)} tarih", False)
    else:
        print_status("Turnuva sonuçları", "Tüm tarihler mevcut")
    
    # Eksik el verileri
    missing_dates_for_hands = calendar_dates - hands_dates
    missing_events = [e for e in calendar_events if e['tarih'] in missing_dates_for_hands]
    
    if missing_events:
        print_status("Eksik el verileri", f"{len(missing_dates_for_hands)} tarih", False)
        for e in missing_events[:3]:
            print(f"      - {e['tarih']}: Event {e['event_id']}")
        if len(missing_events) > 3:
            print(f"      ... ve {len(missing_events) - 3} tane daha")
    else:
        print_status("El verileri", "Tüm tarihler mevcut")
    
    # Eksik DD tarihleri
    missing_dd = hands_dates - dd_dates
    if missing_dd:
        print_status("Eksik DD verileri", f"{len(missing_dd)} tarih", False)
    else:
        print_status("DD verileri", "Tüm tarihler mevcut")
    
    return hands_dates, dd_dates, missing_dd, missing_events, missing_scores, calendar_events

def fetch_tournament_scores(missing_dates, calendar_events):
    """Eksik turnuva sonuçlarını Vugraph'tan al"""
    print_header("Turnuva Sonuçlarını Al")
    
    if not missing_dates:
        print("  ✅ Tüm turnuva sonuçları mevcut")
        return True
    
    print(f"  📅 {len(missing_dates)} yeni tarih için sonuçlar alınacak")
    
    try:
        from auto_fetch_tournaments import AutoTournamentFetcher
        fetcher = AutoTournamentFetcher()
        
        success_count = 0
        for tarih in sorted(missing_dates):
            print(f"    {tarih}...", end=' ')
            if fetcher.fetcher.add_date_to_database(tarih):
                print("✅")
                success_count += 1
            else:
                print("❌")
        
        print(f"\n  ✅ {success_count}/{len(missing_dates)} tarih için sonuçlar alındı")
        return True
    except Exception as e:
        print(f"  ❌ Hata: {e}")
        return False

def calculate_missing_dd(missing_dates):
    """Eksik tarihlerdeki DD'leri hesapla"""
    print_header("Eksik DD Verilerini Hesapla")
    
    if not missing_dates:
        print("  ✅ Tüm DD verileri mevcut, hesaplama gerekmiyor")
        return True
    
    print(f"  📅 Hesaplanacak tarihler: {sorted(missing_dates)}")
    
    # endplay kontrolü
    try:
        from endplay.types import Deal, Player, Vul
        from endplay.dds import calc_dd_table, par
        print("  ✅ endplay kütüphanesi mevcut")
    except ImportError:
        print("  ❌ endplay kütüphanesi bulunamadı!")
        print("  💡 Kurulum: pip install endplay")
        print("  💡 Veya Python 3.12 ile: .venv312\\Scripts\\python.exe update_all_data.py --dd-only")
        return False
    
    # dd_solver'ı import et
    sys.path.insert(0, str(BASE_DIR / "double_dummy"))
    try:
        from dd_solver import (
            load_hands_database, calculate_dd_for_hand, 
            save_dd_results
        )
    except ImportError as e:
        print(f"  ❌ dd_solver modülü yüklenemedi: {e}")
        return False
    
    # Her eksik tarih için DD hesapla
    hands = load_hands_database()
    if not hands:
        print("  ❌ hands_database.json yüklenemedi")
        return False
    
    results = []
    total_success = 0
    
    for date in sorted(missing_dates):
        date_hands = [h for h in hands if h.get('Tarih') == date]
        print(f"\n  📆 {date}: {len(date_hands)} el")
        
        for i, hand in enumerate(date_hands):
            board_num = hand.get('Board', i+1)
            print(f"    [{i+1}/{len(date_hands)}] Board {board_num}...", end=' ')
            
            dd_result, optimum, lott = calculate_dd_for_hand(hand)
            
            if dd_result:
                print("✅", end='')
                if optimum:
                    print(f" {optimum.get('text', '')}", end='')
                print()
                total_success += 1
                
                results.append({
                    'id': hand.get('id'),
                    'board': board_num,
                    'date': date,
                    'dealer': hand.get('Dealer'),
                    'vulnerability': hand.get('Vuln'),
                    'N': hand.get('N'),
                    'S': hand.get('S'),
                    'E': hand.get('E'),
                    'W': hand.get('W'),
                    'dd_result': dd_result,
                    'optimum': optimum,
                    'lott': lott
                })
            else:
                print("❌")
    
    # Sonuçları kaydet
    if results:
        save_dd_results(results)
        print(f"\n  ✅ {total_success} el için DD hesaplandı ve kaydedildi")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='BRIC - Unified Data Update Pipeline')
    parser.add_argument('--check', action='store_true', help='Sadece durumu kontrol et')
    parser.add_argument('--dd-only', action='store_true', help='Sadece eksik DD\'leri hesapla')
    parser.add_argument('--hands-only', action='store_true', help='Sadece eksik el verilerini al')
    parser.add_argument('--scores-only', action='store_true', help='Sadece turnuva sonuçlarını al')
    args = parser.parse_args()
    
    print()
    print("🃏" + "=" * 58)
    print("   BRIC - Birleşik Veri Güncelleme Pipeline'ı")
    print("=" * 60)
    print(f"   Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Durum kontrolü
    hands_dates, dd_dates, missing_dd, missing_events, missing_scores, calendar_events = check_status()
    
    if args.check:
        print("\n💡 Tam güncelleme için: python update_all_data.py")
        print("💡 Sadece DD için: python update_all_data.py --dd-only")
        print("💡 Sadece el verileri için: python update_all_data.py --hands-only")
        print("💡 Sadece turnuva sonuçları için: python update_all_data.py --scores-only")
        return 0
    
    if args.dd_only:
        calculate_missing_dd(missing_dd)
        return 0
    
    if args.hands_only:
        fetch_missing_hands(missing_events)
        return 0
    
    if args.scores_only:
        fetch_tournament_scores(missing_scores, calendar_events)
        return 0
    
    # Tam güncelleme
    print_header("TAM GÜNCELLEME BAŞLIYOR")
    
    # 1. Turnuva sonuçlarını al
    if missing_scores:
        fetch_tournament_scores(missing_scores, calendar_events)
    
    # 2. Eksik el verilerini al
    if missing_events:
        fetch_missing_hands(missing_events)
    
    # 3. Güncel durumu kontrol et (DD için güncel tarihler lazım)
    hands_dates, dd_dates, missing_dd, missing_events, missing_scores, calendar_events = check_status()
    
    # 4. Eksik DD'leri hesapla
    if missing_dd:
        calculate_missing_dd(missing_dd)
    
    # Final durum
    print_header("TAMAMLANDI")
    hands_dates, dd_dates, missing_dd, missing_events, missing_scores, calendar_events = check_status()
    
    if not missing_dd and not missing_events and not missing_scores:
        print("\n  🎉 Tüm veriler güncel!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
