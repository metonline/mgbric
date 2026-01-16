#!/usr/bin/env python3
"""
Simpler approach: Inspect one pair page to understand the data structure,
then build fetcher based on actual available data.
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

EVENT_ID = 404377
SECTION = "A"

def inspect_page():
    """Inspect a pair summary page to see available data."""
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(
        service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        # Open a sample pair page
        url = f"https://clubs.vugraph.com/hosgoru/pairsummary.php?event={EVENT_ID}&section={SECTION}&pair=1&direction=NS"
        print(f"Opening: {url}\n")
        driver.get(url)
        
        time.sleep(3)
        
        print("="*70)
        print("PAGE CONTENT ANALYSIS")
        print("="*70)
        
        # Get page source
        page_source = driver.page_source
        
        # Print available links
        print("\n1. AVAILABLE LINKS:")
        print("-" * 70)
        links = driver.find_elements(By.TAG_NAME, "a")
        link_types = {}
        
        for link in links:
            href = link.get_attribute("href")
            text = link.text.strip()
            
            if href:
                # Categorize links
                if "boarddetails.php" in href:
                    if "boarddetails" not in link_types:
                        link_types["boarddetails"] = []
                    link_types["boarddetails"].append((text, href))
                elif "pairdetail.php" in href:
                    if "pairdetail" not in link_types:
                        link_types["pairdetail"] = []
                    link_types["pairdetail"].append((text, href))
        
        for link_type, links_list in link_types.items():
            print(f"\n{link_type}.php: {len(links_list)} links")
            for text, href in links_list[:3]:
                print(f"  Text: '{text}'")
                print(f"  URL:  {href[:90]}...")
        
        # Look for tables with data
        print("\n2. TABLE ANALYSIS:")
        print("-" * 70)
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"Found {len(tables)} tables on page")
        
        for i, table in enumerate(tables[:3]):
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"\nTable {i+1}: {len(rows)} rows")
            
            # Print first few rows
            for j, row in enumerate(rows[:3]):
                cells = row.find_elements(By.TAG_NAME, "td")
                cell_texts = [cell.text.strip()[:30] for cell in cells]
                print(f"  Row {j}: {cell_texts}")
        
        # Look for specific content
        print("\n3. CONTENT SEARCH:")
        print("-" * 70)
        
        # Search for board numbers
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        if "Board" in page_text:
            print("✓ 'Board' keyword found in content")
        if "contract" in page_text.lower():
            print("✓ 'contract' keyword found")
        if "result" in page_text.lower():
            print("✓ 'result' keyword found")
        if "score" in page_text.lower():
            print("✓ 'score' keyword found")
        
        # Check for specific hand format
        if any(s in page_text for s in ['S:', 'H:', 'D:', 'C:', '♠', '♥', '♦', '♣']):
            print("✓ Card suit symbols/abbreviations found in page")
        
        print("\n4. SAMPLE BOARDDETAILS PAGE:")
        print("-" * 70)
        
        # Find and inspect a board details page
        board_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'boarddetails.php')]")
        if board_links:
            board_url = board_links[0].get_attribute("href")
            print(f"Opening sample board details: {board_url[:80]}...")
            
            driver.get(board_url)
            time.sleep(2)
            
            board_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Look for hand information
            lines = board_text.split('\n')
            for i, line in enumerate(lines):
                if any(s in line for s in ['S:', 'H:', 'D:', 'C:', 'Dealer', 'Board']):
                    # Print context
                    start = max(0, i-1)
                    end = min(len(lines), i+4)
                    print(f"\n  Context around line {i}:")
                    for j in range(start, end):
                        print(f"    {lines[j][:70]}")
        
        print("\n" + "="*70)
        print("INSPECTION COMPLETE")
        print("="*70)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    inspect_page()
