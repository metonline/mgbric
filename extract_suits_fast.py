#!/usr/bin/env python3
"""
Fast suit symbol extraction using Selenium
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Load current database
with open("app/www/hands_database.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Get Board 1 results
board1_results = db['404377']['boards']['1']['results']

# Suit symbols
suit_map = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}

# Set up headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
base_url = "https://clubs.vugraph.com/hosgoru/"

contracts_with_suits = {}
updated = 0

try:
    print("Extracting suit symbols...\n")
    
    for i, result in enumerate(board1_results, 1):
        pair_num = result['pair_num']
        direction = "NS" if result['direction'] == "N-S" else "EW"
        
        url = f"{base_url}boarddetails.php?event=404377&section=A&pair={pair_num}&direction={direction}&board=1"
        
        try:
            print(f"[{i}/{len(board1_results)}] Pair {pair_num}... ", end="", flush=True)
            driver.get(url)
            time.sleep(0.2)
            
            # Find the fantastic row
            rows = driver.find_elements(By.TAG_NAME, "tr")
            
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 3:
                    first_td = tds[0]
                    if "fantastic" in first_td.get_attribute("class") or "resultspecial" in first_td.get_attribute("class"):
                        # Extract level
                        text = first_td.text.strip()
                        if text and text[0].isdigit():
                            level = text.split()[0] if ' ' in text else text[0:2]
                            
                            # Get suit from image
                            imgs = first_td.find_elements(By.TAG_NAME, "img")
                            suit_symbol = ""
                            if imgs:
                                alt = imgs[0].get_attribute("alt")
                                suit_symbol = suit_map.get(alt, alt)
                            
                            # Get declarer
                            declarer = tds[1].text.strip()
                            
                            # Build contract
                            if suit_symbol:
                                contract = f"{level}{suit_symbol} ({declarer})"
                            else:
                                contract = f"{level} ({declarer})"
                            
                            contracts_with_suits[pair_num] = contract
                            print(f"✓ {contract}")
                            break
            
            if pair_num not in contracts_with_suits:
                print("✗ Not found")
                
        except Exception as e:
            print(f"✗ Error")
        
        time.sleep(0.1)

finally:
    driver.quit()

# Update database
for result in board1_results:
    pair_num = result['pair_num']
    if pair_num in contracts_with_suits:
        old_contract = result['contract']
        result['contract'] = contracts_with_suits[pair_num]
        updated += 1

# Save updated database
with open("app/www/hands_database.json", "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"\n✓ Updated {updated} contracts with suit symbols")
print("✓ Saved to hands_database.json")

# Show sample
print("\nSample:")
for r in board1_results[:5]:
    print(f"  {r['pair_names'][:40]:40} | {r['contract']:15} | {r['score']:6.2f}%")
