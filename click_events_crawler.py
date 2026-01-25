#!/usr/bin/env python3
"""
Proper vugraph crawler - clicks on each event to extract hands
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
    print(f"✅ Loaded {len(existing_hands)} existing hands")
except:
    existing_hands = []

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
    print(f"📄 Loaded calendar: {calendar_url}")
    time.sleep(3)
    
    # Get the page source
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find all event links
    event_links = soup.find_all('a', href=re.compile(r'eventresults\.php\?event=\d+'))
    
    print(f"\n🔍 Found {len(event_links)} event links")
    
    event_data = []
    for link in event_links:
        match = re.search(r'event=(\d+)', link.get('href', ''))
        if match:
            event_id = match.group(1)
            event_name = link.get_text(strip=True)
            event_data.append({'id': event_id, 'name': event_name, 'href': link.get('href')})
    
    # Remove duplicates
    seen = set()
    unique_events = []
    for e in event_data:
        if e['id'] not in seen:
            unique_events.append(e)
            seen.add(e['id'])
    
    print(f"📊 {len(unique_events)} unique events")
    
    total_hands_found = 0
    
    # Click on each event
    for i, event in enumerate(unique_events, 1):
        event_id = event['id']
        event_name = event['name']
        
        print(f"\n[{i}/{len(unique_events)}] Clicking event {event_id} ({event_name})...")
        
        try:
            # Go to event page
            event_url = f"{base_url}/eventresults.php?event={event_id}"
            driver.get(event_url)
            time.sleep(2)
            
            # Get page source
            page_src = driver.page_source
            soup_event = BeautifulSoup(page_src, 'html.parser')
            
            # Look for hand/board data
            # Look for links with hand/board info
            hand_pattern = re.compile(r'hand|board|el', re.I)
            all_links = soup_event.find_all('a')
            hand_links = [l for l in all_links if hand_pattern.search(l.get('href', '') + l.get_text())]
            
            if hand_links:
                print(f"  ✓ Found {len(hand_links)} potential hand links")
                for link in hand_links[:3]:
                    print(f"    - {link.get_text()[:40]}")
                total_hands_found += len(hand_links)
            else:
                # Check if page contains hand data in tables
                tables = soup_event.find_all('table')
                
                if tables:
                    print(f"  ✓ Found {len(tables)} tables - checking for hand data...")
                    
                    hand_found_in_tables = False
                    for table in tables:
                        rows = table.find_all('tr')
                        for row in rows:
                            cells = row.find_all(['td', 'th'])
                            row_text = ' '.join([c.get_text() for c in cells])
                            
                            # Look for suit symbols or compass positions
                            if any(suit in row_text for suit in ['♠', '♥', '♦', '♣', ' N ', ' E ', ' S ', ' W ']):
                                print(f"    Found hand data in table!")
                                hand_found_in_tables = True
                                total_hands_found += 1
                                break
                        
                        if hand_found_in_tables:
                            break
                    
                    if not hand_found_in_tables:
                        print(f"  ⏭️  No hand data found")
                else:
                    print(f"  ⏭️  No tables found")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Crawl complete")
    print(f"📊 Events scanned: {len(unique_events)}")
    print(f"🃏 Potential hands found: {total_hands_found}")

except Exception as e:
    print(f"❌ Fatal error: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
    print("\n🔌 Browser closed")
