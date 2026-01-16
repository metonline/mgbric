#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper to fetch all Board 1 results for all 30 pairs (15 NS, 15 EW)
from Vugraph Hoşgörü tournament
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import sys
import io

# Set stdout encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

EVENT_ID = "404377"
SECTION = "A"
BOARD_NUM = 1
BASE_URL = "https://clubs.vugraph.com/hosgoru/"
DB_FILE = "hands_database.json"

# All pairs from the tournament
NS_PAIRS = [
    ("EMİNE BİLLUR ARAZ", "RABİA YEŞİM SOMER", 1),
    ("METE KUTLAY", "OYA ZEYNEP DEMİREL", 2),
    ("PELİN ÜLGER", "HAMİT NACİ DEMİRBAŞ", 3),
    ("PINAR ERGİN", "SABRİ BURAK EROL", 4),
    ("YILMAZ TURTURA", "SERDAR ŞERİF KURŞUN", 5),
    ("AYŞE SEVDA KALE", "MUSTAFA ARİF ALTUNDAĞ", 6),
    ("CÜNEYT ÇAĞIRKAN", "SAİME ÇAĞIRKAN", 7),
    ("MEHMET CEMAL DİYARBAKIRLI", "KAMİL SEZAİ ATAV", 8),
    ("NERMİN TAŞLITARLA", "MELİHA BURCU KİNEŞ", 9),
    ("EKREM SERDAR", "HALİME CAN", 10),
    ("YAHYA KÜÇÜKKILIÇ", "CEMAL ERDOĞAN", 11),
    ("GÜLCE ŞUKAL", "ZEYNEP DENİZLİ", 12),
    ("Cemal ÜÇÜNCÜ", "ERDOĞAN ELÇİN", 13),
    ("Salim ÇOPUR", "ŞÜKRÜ AZMİ ARNA", 14),
    ("BERK BAŞARAN", "ALİCAN DEMİRDEN", 15),
]

EW_PAIRS = [
    ("ZAFER ŞENGÜL", "SADIK KORKMAZ", 1),
    ("KADİR ŞAHİN", "TUBA BAĞDAT", 2),
    ("OJENİ TÜRÜSEL", "MURAT DEMİRSAN", 3),
    ("MEHMET SEDAT CENGİZ", "MEHMET ALİ KORDÖV", 4),
    ("VOLKAN DENİZCİ", "HAYATİ ERGÜR", 5),
    ("Handan UZUNER", "ÖZLEM AYDIN", 6),
    ("KEMAL BAKIMCI", "Polat TAŞCIOĞLU", 7),
    ("ÖMER GÜNEŞ", "ALİ KÜÇÜKÇAĞLAYAN", 8),
    ("CİHAN VATANSEVER", "ERTUĞRUL YAVUZ", 9),
    ("OKTAY UYAV", "MUSTAFA FARUK BENGİSU", 10),
    ("MEHMET ARDA DAĞCIOĞLU", "ESRA ÖZTEMİR", 11),
    ("BAYRAM ÇETİNKAYA", "İLYAS FATİH COŞKUN", 12),
    ("ONUR ŞENOCAK", "A.UĞUR GÖNEL", 13),
    ("NAHİDE BERKİZ ARKUN", "TALHA ÜNSAL", 14),
    ("Nadir İsmet HERGÜNŞER", "FİKRET GÜNEŞ", 15),
]

def extract_board_result_from_page(html_content, pair_num, direction):
    """Extract Board 1 result from pair's result page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for the board table that shows individual board results
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                # First cell should contain board number
                board_cell = cells[0].get_text(strip=True)
                if board_cell == '1':
                    # Found board 1
                    contract = cells[1].get_text(strip=True) if len(cells) > 1 else '-'
                    result = cells[2].get_text(strip=True) if len(cells) > 2 else '-'
                    score = cells[3].get_text(strip=True) if len(cells) > 3 else '0'
                    
                    # Clean up score (remove % if present)
                    score = score.replace('%', '').strip()
                    try:
                        score = float(score)
                    except:
                        score = 0
                    
                    return {
                        'contract': contract,
                        'result': result,
                        'score': score
                    }
    
    return None

def fetch_pair_results(pair_num, direction):
    """Fetch results page for a specific pair"""
    # Determine PAIR parameter based on pair number
    # For NS, pair_num is the pair number
    # For EW, need to adjust
    
    dir_code = "NS" if direction == "N-S" else "EW"
    url = f"{BASE_URL}pairresults.php?event={EVENT_ID}&pair={pair_num}&direction={dir_code}"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            return extract_board_result_from_page(response.content, 1, direction)
        else:
            print(f"Pair {pair_num} ({direction}): HTTP {response.status_code}")
            return None
    
    except Exception as e:
        print(f"Pair {pair_num} ({direction}): Error - {e}")
        return None

def load_database():
    """Load existing database"""
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading database: {e}")
        return None

def save_database(db):
    """Save updated database"""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"\n[SAVED] Database saved to {DB_FILE}")
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False

def main():
    print("=" * 70)
    print("Fetching all Board 1 results for all pairs...")
    print("=" * 70)
    
    # Load database
    db = load_database()
    if not db:
        print("Failed to load database")
        return
    
    event_key = "hosgoru_04_01_2026"
    if event_key not in db["events"]:
        print(f"Event {event_key} not found in database")
        return
    
    board_data = db["events"][event_key]["boards"]["1"]
    
    # Clear existing results
    board_data["results"] = []
    
    print("\nFetching N-S pairs results...")
    for player1, player2, pair_num in NS_PAIRS:
        pair_name = f"{player1} - {player2}"
        result_data = fetch_pair_results(pair_num, "N-S")
        
        if result_data:
            result_entry = {
                "pair_names": pair_name,
                "pair_num": str(pair_num),
                "direction": "N-S",
                "contract": result_data['contract'],
                "result": result_data['result'],
                "score": result_data['score']
            }
            board_data["results"].append(result_entry)
            print(f"  {pair_num}. {pair_name}: {result_data['contract']} {result_data['result']} - {result_data['score']}%")
        else:
            print(f"  {pair_num}. {pair_name}: FAILED")
        
        time.sleep(0.5)  # Be nice to the server
    
    print("\nFetching E-W pairs results...")
    for player1, player2, pair_num in EW_PAIRS:
        pair_name = f"{player1} - {player2}"
        result_data = fetch_pair_results(pair_num, "E-W")
        
        if result_data:
            result_entry = {
                "pair_names": pair_name,
                "pair_num": str(pair_num),
                "direction": "E-W",
                "contract": result_data['contract'],
                "result": result_data['result'],
                "score": result_data['score']
            }
            board_data["results"].append(result_entry)
            print(f"  {pair_num}. {pair_name}: {result_data['contract']} {result_data['result']} - {result_data['score']}%")
        else:
            print(f"  {pair_num}. {pair_name}: FAILED")
        
        time.sleep(0.5)  # Be nice to the server
    
    # Save database
    if save_database(db):
        print(f"\n✅ Board 1 updated with {len(board_data['results'])} pair results")
    else:
        print("\n❌ Failed to save database")

if __name__ == "__main__":
    main()
