#!/usr/bin/env python3
"""
Direct approach: Fetch hands from known board URLs directly.
We know the structure works, so try accessing board pages directly.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(
    service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
    options=options
)

# Try to fetch hands from one board directly
boards_found = {}

try:
    for board_num in [1, 2, 3]:  # Test first 3 boards
        print(f"\n{'='*70}")
        print(f"BOARD {board_num}: Trying different URLs")
        print(f"{'='*70}")
        
        urls_to_try = [
            f"https://clubs.vugraph.com/hosgoru/boarddetails.php?event=404377&board={board_num}",
            f"https://clubs.vugraph.com/hosgoru/boarddetails.php?event=404377&board={board_num}&pair=1",
            f"https://clubs.vugraph.com/hosgoru/boarddetails.php?event=404377&board={board_num}&pair=1&direction=NS",
            f"https://clubs.vugraph.com/hosgoru/board.php?event=404377&board={board_num}",
        ]
        
        for url in urls_to_try:
            try:
                print(f"\nTrying: {url[:70]}...")
                driver.get(url)
                time.sleep(2)
                
                page_source = driver.page_source
                page_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Check if we got actual content
                if len(page_text.strip()) < 50:
                    print("  ✗ Page empty or error")
                    continue
                
                print(f"  ✓ Page loaded ({len(page_text)} chars)")
                
                # Show first part of text
                lines = page_text.split('\n')
                print(f"\n  First 20 lines:")
                for i, line in enumerate(lines[:20]):
                    if line.strip():
                        print(f"    {i}: {line[:70]}")
                
                # Look for suit patterns
                suit_indicators = {
                    'S:': page_text.count('S:'),
                    'H:': page_text.count('H:'),
                    'D:': page_text.count('D:'),
                    'C:': page_text.count('C:'),
                    'North': page_text.count('North'),
                    'South': page_text.count('South'),
                    'East': page_text.count('East'),
                    'West': page_text.count('West'),
                }
                
                print(f"\n  Patterns found: {suit_indicators}")
                
                # Try to extract hands if we find the patterns
                if any(count > 0 for count in suit_indicators.values()):
                    # Look for hand lines
                    hands_found = False
                    for i, line in enumerate(lines):
                        if all(s in line for s in ['S:', 'H:', 'D:', 'C:']):
                            print(f"\n  Hand line found at line {i}:")
                            print(f"    {line}")
                            hands_found = True
                    
                    if not hands_found:
                        print(f"\n  Full page text (up to 2000 chars):")
                        print(page_text[:2000])
                        print("  ...\n")
                    
                    break  # Success, move to next board
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        print()

finally:
    driver.quit()

print("\n" + "="*70)
print("DIRECT URL TEST COMPLETE")
print("="*70 + "\n")
