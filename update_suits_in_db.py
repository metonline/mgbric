#!/usr/bin/env python3
"""
Extract suit symbols from Vugraph and update database with red coloring for H and D
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Suit mapping
suit_map = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}

# Load database
with open("app/www/hands_database.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Get all results from board 1
results = db['events']['hosgoru_04_01_2026']['boards']['1']['results']

# Set up headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
base_url = "https://clubs.vugraph.com/hosgoru/"

contracts_map = {}
updated = 0

try:
    print("Extracting suit symbols from Vugraph...\n")
    
    for i, result in enumerate(results, 1):
        pair_num = result['pair_num']
        direction = "NS" if result['direction'] == "N-S" else "EW"
        
        url = f"{base_url}boarddetails.php?event=404377&section=A&pair={pair_num}&direction={direction}&board=1"
        
        try:
            print(f"[{i}/{len(results)}] Pair {pair_num}...", end="", flush=True)
            driver.get(url)
            time.sleep(0.15)
            
            # Find the fantastic row (pair's highlighted result)
            rows = driver.find_elements(By.TAG_NAME, "tr")
            
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 3:
                    first_td = tds[0]
                    css_class = first_td.get_attribute("class") or ""
                    
                    if "fantastic" in css_class or "resultspecial" in css_class:
                        # Get contract level (first 1-2 chars)
                        text = first_td.text.strip()
                        if text and text[0].isdigit():
                            # Extract level
                            if "NT" in text or "N" in text:
                                level = text[:2]  # e.g., "3N"
                            else:
                                level = text[0]   # e.g., "4"
                            
                            # Get suit from image alt text
                            suit_symbol = ""
                            imgs = first_td.find_elements(By.TAG_NAME, "img")
                            if imgs:
                                alt = imgs[0].get_attribute("alt")
                                suit_symbol = suit_map.get(alt, alt)
                            
                            # Get declarer (E or W)
                            declarer = tds[1].text.strip()
                            
                            # Build contract
                            if suit_symbol:
                                contract = f"{level}{suit_symbol} ({declarer})"
                            else:
                                contract = f"{level} ({declarer})"
                            
                            contracts_map[pair_num] = contract
                            print(f" ✓ {contract}")
                            break
            
            if pair_num not in contracts_map:
                print(" ✗ Not found")
                
        except Exception as e:
            print(f" ✗ Error: {str(e)[:30]}")
        
        time.sleep(0.1)

finally:
    driver.quit()

# Update database contracts
for result in results:
    pair_num = result['pair_num']
    if pair_num in contracts_map:
        result['contract'] = contracts_map[pair_num]
        updated += 1

# Save updated database
with open("app/www/hands_database.json", "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"\n✓ Updated {updated}/{len(results)} contracts with suit symbols")
print("✓ Saved to hands_database.json")

# Show sample
print("\nSample results:")
for r in results[:5]:
    print(f"  {r['pair_names'][:40]:40} | {r['contract']:15} | {r['score']:6.2f}%")
