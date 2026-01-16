#!/usr/bin/env python3
"""
Update contracts with suit symbols by parsing the HTML structure directly.
"""

import json
import re

# Read the current final data
with open("board1_final_complete.json", "r", encoding="utf-8") as f:
    results = json.load(f)

# Suit symbols
SUITS = {
    'S': '♠',
    'H': '♥',
    'D': '♦',
    'C': '♣',
    'NT': 'NT'
}

# Mapping of contracts to likely suits based on common bridge patterns
# This is a heuristic - we need to extract from the actual HTML
# For now, we'll enhance this with HTML parsing

# Read boarddetails page and extract suit info
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

BASE_URL = "https://clubs.vugraph.com/hosgoru/"
EVENT_ID = 404377
SECTION = "A"

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Map to store contracts with suits
contracts_with_suits = {}

try:
    # For each pair, fetch boarddetails and extract suit
    for result in results[:3]:  # Test with first 3
        pair_num = result['pair_num']
        direction = result['direction']
        board_num = 1
        
        url = f"{BASE_URL}boarddetails.php?event={EVENT_ID}&section={SECTION}&pair={pair_num}&direction={direction}&board={board_num}"
        print(f"Fetching {pair_num} ({direction})...", end=" ")
        
        driver.get(url)
        time.sleep(1)
        
        try:
            # Find the fantastic/resultspecial row (pair's result)
            fantastic_rows = driver.find_elements(By.XPATH, "//tr[./td[@class='fantastic'] or ./td[@class='resultspecial']]")
            
            if fantastic_rows:
                cells = fantastic_rows[0].find_elements(By.TAG_NAME, "td")
                
                if len(cells) >= 3:
                    contract_cell = cells[0]
                    declarer = cells[1].text.strip()
                    
                    # Get text from cell
                    contract_text = contract_cell.text.strip()
                    
                    # Get suit from img alt
                    suit_imgs = contract_cell.find_elements(By.TAG_NAME, "img")
                    suit = ""
                    
                    if suit_imgs:
                        for img in suit_imgs:
                            alt = img.get_attribute("alt").strip().upper()
                            if alt in SUITS:
                                suit = SUITS[alt]
                                break
                    
                    # Build contract with suit
                    if suit and contract_text:
                        full_contract = f"{contract_text}{suit} ({declarer})"
                    elif contract_text:
                        full_contract = f"{contract_text} ({declarer})"
                    else:
                        full_contract = "?"
                    
                    contracts_with_suits[f"{pair_num}_{direction}"] = full_contract
                    print(f"✓ {full_contract}")
                else:
                    print("✗ (not enough cells)")
            else:
                print("✗ (no fantastic row)")
        except Exception as e:
            print(f"✗ ({e})")

finally:
    driver.quit()

print("\nExtracted contracts:")
for key, contract in contracts_with_suits.items():
    print(f"  {key}: {contract}")

# Update results with suit symbols
updated_count = 0
for result in results:
    key = f"{result['pair_num']}_{result['direction']}"
    if key in contracts_with_suits:
        result['contract'] = contracts_with_suits[key]
        updated_count += 1

print(f"\n✓ Updated {updated_count} contracts with suit symbols")

# Save updated results
with open("board1_with_suit_symbols.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("✓ Saved to board1_with_suit_symbols.json")
