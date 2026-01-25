#!/usr/bin/env python3
"""
Fetch all hands from all 23 January 2026 events
Uses boarddetails.php endpoint with Selenium
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re

# Keep existing hands
try:
    with open('hands_database.json', 'r') as f:
        existing_hands = json.load(f)
    existing_ids = {f"{h.get('event_id')}_{h.get('board')}" for h in existing_hands}
    print(f"✅ Loaded {len(existing_hands)} existing hands")
except:
    existing_hands = []
    existing_ids = set()

all_hands = existing_hands.copy()

base_url = "https://clubs.vugraph.com/hosgoru"

# Events from January 2026 calendar (event_id, date)
events = [
    ('404155', '01.01.2026'),
    ('404197', '02.01.2026'),
    ('404275', '03.01.2026'),
    ('404377', '04.01.2026'),
    ('404426', '05.01.2026'),
    ('404498', '06.01.2026'),
    ('404562', '07.01.2026'),
    ('404628', '08.01.2026'),
    ('404691', '09.01.2026'),
    ('404854', '10.01.2026'),
    ('404821', '11.01.2026'),
    ('404876', '12.01.2026'),
    ('405128', '13.01.2026'),
    ('405007', '14.01.2026'),
    ('405061', '15.01.2026'),
    ('405123', '16.01.2026'),
    ('405204', '17.01.2026'),
    ('405278', '18.01.2026'),
    ('405315', '19.01.2026'),
    ('405376', '20.01.2026'),
    ('405445', '21.01.2026'),
    ('405535', '22.01.2026'),
    ('405596', '23.01.2026'),
]

print(f"🚀 Will fetch from {len(events)} events\n")

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')

total_new_hands = 0

for evt_idx, (event_id, event_date) in enumerate(events, 1):
    print(f"[{evt_idx}/{len(events)}] Event {event_id} ({event_date})...", end='', flush=True)
    
    hands_in_event = 0
    driver = None
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Try boards 1-32 (standard is 30, but some have more)
        for board_num in range(1, 33):
            board_id = f"{event_id}_{board_num}"
            
            # Skip if already have this board
            if board_id in existing_ids:
                continue
            
            try:
                url = f'{base_url}/boarddetails.php?event={event_id}&section=A&pair=1&direction=NS&board={board_num}'
                
                driver.get(url)
                time.sleep(0.5)
                
                page_html = driver.page_source
                
                # Check if page exists
                if 'not found' in page_html.lower() or len(page_html) < 500:
                    continue
                
                soup = BeautifulSoup(page_html, 'html.parser')
                
                # Look for bridgetable with oyuncu class
                bridge_table = soup.find('table', class_='bridgetable')
                
                if bridge_table:
                    player_cells = bridge_table.find_all('td', class_='oyuncu')
                    
                    if len(player_cells) >= 4:
                        # Found a valid hand! Parse it
                        hands = {'N': '', 'E': '', 'S': '', 'W': ''}
                        
                        # Map positions
                        visual_to_compass = {0: 'N', 1: 'W', 2: 'E', 3: 'S'}
                        
                        for idx, cell in enumerate(player_cells[:4]):
                            compass_pos = visual_to_compass[idx]
                            
                            # Extract cards
                            cell_text = cell.get_text()
                            # Simple extraction: look for card patterns
                            cards_match = re.search(r'([AKQJT98765432]*)\s+([AKQJT98765432]*)\s+([AKQJT98765432]*)\s+([AKQJT98765432]*)', cell_text)
                            
                            if cards_match:
                                s_cards = cards_match.group(1) or ''
                                h_cards = cards_match.group(2) or ''
                                d_cards = cards_match.group(3) or ''
                                c_cards = cards_match.group(4) or ''
                                hands[compass_pos] = f"{s_cards}.{h_cards}.{d_cards}.{c_cards}"
                        
                        # Create hand object
                        hand_obj = {
                            'N': hands['N'],
                            'E': hands['E'],
                            'S': hands['S'],
                            'W': hands['W'],
                            'event_id': event_id,
                            'date': event_date,
                            'board': board_num,
                            'dealer': ['N', 'E', 'S', 'W'][(board_num - 1) % 4]
                        }
                        
                        all_hands.append(hand_obj)
                        hands_in_event += 1
                        total_new_hands += 1
            
            except Exception as e:
                continue
        
        if hands_in_event > 0:
            print(f" ✅ {hands_in_event} hands")
        else:
            print(f" ⏭️")
    
    except Exception as e:
        print(f" ❌ {str(e)[:30]}")
    
    finally:
        if driver:
            driver.quit()

print(f"\n{'='*60}")
print(f"✅ Fetch complete")
print(f"📊 New hands found: {total_new_hands}")
print(f"📚 Total hands: {len(all_hands)}")

# Save all hands
with open('hands_database.json', 'w') as f:
    json.dump(all_hands, f, indent=2)

print(f"💾 Saved to hands_database.json")
