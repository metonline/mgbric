#!/usr/bin/env python3
"""
Extract all Board 1 contracts with suit symbols using Selenium
"""

import json
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Load the current results with pair info
with open("board1_final_complete.json", "r", encoding="utf-8") as f:
    results = json.load(f)

# Set up Selenium with headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)

# Suit symbols
suit_symbols = {
    'S': '♠',
    'H': '♥',
    'D': '♦',
    'C': '♣',
    'NT': 'NT'
}

# Base URL
base_url = "https://clubs.vugraph.com/hosgoru/"

contracts_map = {}

try:
    print("Extracting suit symbols for Board 1 contracts...\n")
    
    # Get unique pairs from results
    unique_pairs = {}
    for result in results:
        pair_num = result['pair_num']
        if pair_num not in unique_pairs:
            unique_pairs[pair_num] = {
                'direction': result['direction'],
                'names': result['pair_names']
            }
    
    # For each pair, fetch the boarddetails page for Board 1
    for i, (pair_num, pair_info) in enumerate(sorted(unique_pairs.items()), 1):
        direction = "NS" if pair_info['direction'] == "N-S" else "EW"
        url = f"{base_url}boarddetails.php?event=404377&section=A&pair={pair_num}&direction={direction}&board=1"
        
        try:
            print(f"[{i}/{len(unique_pairs)}] Fetching pair {pair_num}... ", end="", flush=True)
            driver.get(url)
            
            # Wait for table to load
            wait = WebDriverWait(driver, 5)
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))
            
            # Find the fantastic row (pair's result)
            rows = driver.find_elements(By.TAG_NAME, "tr")
            
            contract = None
            declarer = None
            
            for row in rows:
                try:
                    # Check if this is a fantastic or resultspecial row
                    tds = row.find_elements(By.TAG_NAME, "td")
                    if len(tds) >= 3:
                        # Check if first TD has the fantastic class
                        first_td = tds[0]
                        if "fantastic" in first_td.get_attribute("class") or "resultspecial" in first_td.get_attribute("class"):
                            # Extract contract level from text
                            text = first_td.text.strip()
                            if text and text[0].isdigit():
                                # Get the level (first char or first two for NT)
                                if text.startswith("7N"):
                                    level = "7N"
                                elif text.startswith("6N"):
                                    level = "6N"
                                elif text.startswith("5N"):
                                    level = "5N"
                                elif text.startswith("4N"):
                                    level = "4N"
                                elif text.startswith("3N"):
                                    level = "3N"
                                elif text.startswith("1N"):
                                    level = "1N"
                                else:
                                    level = text[0]
                                
                                # Try to get suit from image
                                suit = None
                                img_elem = first_td.find_element(By.TAG_NAME, "img") if len(first_td.find_elements(By.TAG_NAME, "img")) > 0 else None
                                if img_elem:
                                    alt_text = img_elem.get_attribute("alt")
                                    suit = suit_symbols.get(alt_text, alt_text)
                                
                                # Declarer from second TD
                                declarer = tds[1].text.strip()
                                
                                # Build contract
                                if suit:
                                    if suit == 'NT':
                                        contract = f"{level} ({declarer})"
                                    else:
                                        contract = f"{level}{suit} ({declarer})"
                                else:
                                    # Fallback without suit
                                    contract = f"{level} ({declarer})"
                                
                                break
                except:
                    continue
            
            if contract:
                contracts_map[pair_num] = contract
                print(f"✓ {contract}")
            else:
                print("✗ No contract found")
                
        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")
            continue
        
        time.sleep(0.3)  # Avoid rate limiting

finally:
    driver.quit()

# Update results with suit symbols
updated = 0
for result in results:
    pair_num = result['pair_num']
    if pair_num in contracts_map:
        result['contract'] = contracts_map[pair_num]
        updated += 1

# Save updated results
with open("board1_with_suit_symbols.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n✓ Updated {updated}/{len(unique_pairs)} pairs with suit symbols")
print("✓ Saved to board1_with_suit_symbols.json")

# Show sample
print("\nSample results:")
for r in results[:5]:
    print(f"  {r['pair_names'][:35]:35} | {r['contract']:15} | {r['score']:6.2f}%")
