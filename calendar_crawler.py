#!/usr/bin/env python3
"""
Comprehensive Hoşgörü vugraph crawler
Clicks through calendar days and extracts hands from player rankings
"""

import json
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Keep existing hands
try:
    with open('hands_database.json', 'r') as f:
        existing_hands = json.load(f)
    print(f"✅ Loaded {len(existing_hands)} existing hands")
except:
    existing_hands = []

all_hands = {h.get('event_id'): h for h in existing_hands}  # Track by event_id to avoid dupes

base_url = "https://clubs.vugraph.com/hosgoru/calendar.php"

# Setup Selenium
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
# Don't add headless yet - might need visible browser
# chrome_options.add_argument("--headless")

print("🚀 Starting browser...")
driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get(base_url)
    print(f"📄 Loaded calendar: {base_url}")
    time.sleep(3)
    
    # Date range: 01.01.2026 to 24.01.2026
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 24)
    
    current = start_date
    day_count = 0
    
    while current <= end_date:
        date_str = current.strftime("%d.%m.%Y")
        day_str = current.strftime("%d.%m")
        
        print(f"\n🔍 Checking {date_str}...")
        
        try:
            # Look for the day link in the calendar
            # Try different possible selectors
            day_link = None
            
            # Try to find by text or data attribute
            try:
                elements = driver.find_elements(By.TAG_NAME, "a")
                for elem in elements:
                    text = elem.text.strip()
                    if day_str in text or current.strftime("%d") == text:
                        day_link = elem
                        break
            except:
                pass
            
            if day_link:
                print(f"  📌 Found link for {day_str}")
                driver.execute_script("arguments[0].scrollIntoView();", day_link)
                time.sleep(1)
                day_link.click()
                time.sleep(3)
                
                # Now we should be on the day's page
                # Look for hand data or player rankings
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Try to find hands in various possible locations
                tables = soup.find_all('table')
                hands_found = 0
                
                for table in tables:
                    rows = table.find_all('tr')
                    # Look for hand-like data (compass positions, cards, etc.)
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 4:
                            # Might be a hand row - check for card patterns
                            cell_text = ' '.join([c.get_text() for c in cells])
                            if any(suit in cell_text for suit in ['♠', '♥', '♦', '♣', 'S', 'H', 'D', 'C']):
                                hands_found += 1
                
                if hands_found > 0:
                    print(f"  ✓ Found {hands_found} potential hands")
                else:
                    print(f"  ⏭️  No hands found on this day")
                
                # Go back to calendar
                driver.back()
                time.sleep(2)
            else:
                print(f"  ⏭️  No link found for {day_str}")
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            # Try to go back
            try:
                driver.back()
                time.sleep(2)
            except:
                pass
        
        current += timedelta(days=1)
        day_count += 1

except Exception as e:
    print(f"❌ Fatal error: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
    print(f"\n{'='*60}")
    print(f"✅ Crawl complete")
    print(f"📊 Days checked: {day_count}")
    print(f"📚 Total hands collected: {len(all_hands)}")
