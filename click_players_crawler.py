#!/usr/bin/env python3
"""
Vugraph crawler - click event -> click players -> extract hands
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re

# Keep existing hands
try:
    with open('hands_database.json', 'r') as f:
        existing_hands = json.load(f)
    existing_event_ids = {h.get('event_id') for h in existing_hands}
    print(f"✅ Loaded {len(existing_hands)} existing hands from {len(existing_event_ids)} events")
except:
    existing_hands = []
    existing_event_ids = set()

all_hands = existing_hands.copy()

base_url = "https://clubs.vugraph.com/hosgoru"

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

print("🚀 Starting browser...")
driver = webdriver.Chrome(options=chrome_options)

try:
    # Go to calendar
    calendar_url = f"{base_url}/calendar.php?month=1&year=2026"
    driver.get(calendar_url)
    print(f"📄 Loaded calendar")
    time.sleep(3)
    
    # Parse calendar
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    event_links = soup.find_all('a', href=re.compile(r'eventresults\.php\?event=\d+'))
    
    events = []
    seen = set()
    for link in event_links:
        match = re.search(r'event=(\d+)', link.get('href', ''))
        if match:
            event_id = match.group(1)
            if event_id not in seen:
                events.append(event_id)
                seen.add(event_id)
    
    print(f"🔍 Found {len(events)} events\n")
    
    total_new_hands = 0
    
    # Process each event
    for i, event_id in enumerate(events, 1):
        print(f"[{i}/{len(events)}] Event {event_id}...")
        
        try:
            # Go to event results page
            event_url = f"{base_url}/eventresults.php?event={event_id}"
            driver.get(event_url)
            time.sleep(1)
            
            page_src = driver.page_source
            soup_event = BeautifulSoup(page_src, 'html.parser')
            
            # Look for players link
            players_link = None
            for link in soup_event.find_all('a'):
                href = link.get('href', '')
                text = link.get_text().lower()
                
                # Look for "oyuncu" (player in Turkish) or players-related links
                if any(word in text for word in ['oyuncu', 'player', 'puanlar', 'ranking']) or 'oyuncu' in href:
                    players_link = link.get('href')
                    print(f"  📌 Found players link: {text[:30]}")
                    break
            
            if players_link:
                # Click/navigate to players page
                if players_link.startswith('http'):
                    players_url = players_link
                elif players_link.startswith('/'):
                    players_url = f"https://clubs.vugraph.com{players_link}"
                else:
                    players_url = f"{base_url}/{players_link}"
                
                driver.get(players_url)
                time.sleep(2)
                
                # Now we're on players page - look for hands
                page_src_players = driver.page_source
                soup_players = BeautifulSoup(page_src_players, 'html.parser')
                
                # Save this page to inspect
                with open(f'event_{event_id}_players.html', 'w', encoding='utf-8') as f:
                    f.write(page_src_players)
                
                # Look for hand data in tables
                tables = soup_players.find_all('table')
                hands_in_event = 0
                
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        row_text = ' '.join([c.get_text() for c in cells])
                        
                        # Look for hand patterns
                        if any(suit in row_text for suit in ['♠', '♥', '♦', '♣']):
                            hands_in_event += 1
                
                if hands_in_event > 0:
                    print(f"    ✅ Found {hands_in_event} hand entries")
                    total_new_hands += hands_in_event
                else:
                    print(f"    ⏭️  No hand data found")
            else:
                print(f"  ⏭️  No players link found")
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Crawl complete")
    print(f"📊 Events processed: {len(events)}")
    print(f"🃏 Total hands found: {total_new_hands}")

except Exception as e:
    print(f"❌ Fatal error: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
    print("\n🔌 Browser closed")
