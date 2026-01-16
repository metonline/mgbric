#!/usr/bin/env python3
"""
Debug: Inspect actual Vugraph pages to see where hands data is.
No complex parsing - just show raw page structure.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
    options=options
)

try:
    # Test 1: Event overview
    print("\n" + "="*70)
    print("TEST 1: Event Overview Page")
    print("="*70)
    
    event_url = "https://clubs.vugraph.com/hosgoru/eventresults.php?event=404377"
    print(f"\nOpening: {event_url}\n")
    driver.get(event_url)
    time.sleep(2)
    
    # Get page source
    page_source = driver.page_source
    
    # Look for links
    from selenium.webdriver.common.by import By
    links = driver.find_elements(By.TAG_NAME, "a")
    
    pair_links = []
    for link in links:
        href = link.get_attribute("href") or ""
        text = link.text.strip()
        if "pairsummary" in href:
            pair_links.append((text, href))
    
    print(f"Found {len(pair_links)} pair links")
    if pair_links:
        print("\nFirst 3 pair links:")
        for text, href in pair_links[:3]:
            print(f"  Text: {text}")
            print(f"  URL:  {href[:80]}...\n")
    
    # Test 2: A pair summary page
    if pair_links:
        print("\n" + "="*70)
        print("TEST 2: Pair Summary Page")
        print("="*70)
        
        pair_url = pair_links[0][1]
        print(f"\nOpening: {pair_url[:80]}...\n")
        driver.get(pair_url)
        time.sleep(2)
        
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        print("Page text (first 1500 chars):")
        print(page_text[:1500])
        print("\n...")
        
        # Look for board details links
        board_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'boarddetails')]")
        print(f"\n\nFound {len(board_links)} board details links")
        
        if board_links:
            # Test 3: A board details page
            print("\n" + "="*70)
            print("TEST 3: Board Details Page")
            print("="*70)
            
            board_url = board_links[0].get_attribute("href")
            print(f"\nOpening: {board_url[:80]}...\n")
            driver.get(board_url)
            time.sleep(2)
            
            page_text = driver.find_element(By.TAG_NAME, "body").text
            page_source = driver.page_source
            
            print("Page text (full - up to 3000 chars):")
            print(page_text[:3000])
            
            # Look for specific patterns
            print("\n" + "="*70)
            print("PATTERN SEARCH IN BOARD DETAILS PAGE")
            print("="*70)
            
            # Search for suit indicators
            patterns = {
                "Has 'Dealer'": "Dealer" in page_text,
                "Has 'North'": "North" in page_text,
                "Has 'South'": "South" in page_text,
                "Has 'East'": "East" in page_text,
                "Has 'West'": "West" in page_text,
                "Has 'S:'": "S:" in page_text,
                "Has 'H:'": "H:" in page_text,
                "Has 'D:'": "D:" in page_text,
                "Has 'C:'": "C:" in page_text,
                "Has suit symbols": any(s in page_text for s in ['♠', '♥', '♦', '♣']),
                "Has 'contract'": "contract" in page_text.lower(),
                "Has 'result'": "result" in page_text.lower(),
            }
            
            for pattern, found in patterns.items():
                status = "✓" if found else "✗"
                print(f"{status} {pattern}")
            
            # Show all tables
            print("\n" + "-"*70)
            print("TABLES ON BOARD DETAILS PAGE")
            print("-"*70)
            
            tables = driver.find_elements(By.TAG_NAME, "table")
            print(f"\nFound {len(tables)} tables\n")
            
            for table_idx, table in enumerate(tables):
                rows = table.find_elements(By.TAG_NAME, "tr")
                cols = table.find_elements(By.TAG_NAME, "td")
                
                print(f"Table {table_idx + 1}: {len(rows)} rows, ~{len(cols)} cells")
                
                # Print first few rows
                for row_idx, row in enumerate(rows[:3]):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    cell_texts = [c.text.strip()[:20] for c in cells]
                    print(f"  Row {row_idx}: {cell_texts}")
                
                if len(rows) > 3:
                    print(f"  ... ({len(rows)-3} more rows)")
                print()
            
            # Show divs with hand-like content
            print("\n" + "-"*70)
            print("DIVS/ELEMENTS WITH CARD CONTENT")
            print("-"*70)
            
            all_elements = driver.find_elements(By.TAG_NAME, "*")
            
            card_elements = []
            for elem in all_elements:
                text = elem.text.strip()
                
                # Look for elements containing suit names
                if any(suit in text for suit in ['S:', 'H:', 'D:', 'C:', 'North', 'South', 'East', 'West']):
                    if len(text) < 300:  # Avoid huge elements
                        card_elements.append({
                            'tag': elem.tag_name,
                            'text': text[:100],
                            'class': elem.get_attribute('class')
                        })
            
            print(f"\nFound {len(card_elements)} elements with card/player content")
            for i, elem in enumerate(card_elements[:10]):
                print(f"\n  {i+1}. <{elem['tag']}> class='{elem['class']}'")
                print(f"     Text: {elem['text']}")

finally:
    driver.quit()

print("\n" + "="*70)
print("INSPECTION COMPLETE")
print("="*70 + "\n")
