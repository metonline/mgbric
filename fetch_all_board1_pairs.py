#!/usr/bin/env python3
"""
Production scraper: Extract Board 1 results for all 30 pairs from Vugraph.
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import re

EVENT_ID = 404377
SECTION = "A"
BOARD_NUM = 1
BASE_URL = "https://clubs.vugraph.com/hosgoru/"

def setup_driver():
    """Initialize Chrome driver in headless mode."""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.add_argument("--headless")  # Run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def extract_pairs_from_event_page(driver):
    """Extract all pair info from event results page."""
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, "//tr[@onclick]")
    pairs = []
    
    for row in rows:
        try:
            onclick = row.get_attribute("onclick")
            match = re.search(r"pair=(\d+)&direction=(\w+)", onclick)
            if not match:
                continue
            
            pair_num = match.group(1)
            direction = match.group(2)
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 2:
                continue
            
            names = cells[1].text.strip()
            score = None
            if len(cells) > 2:
                try:
                    score = float(cells[2].text.strip())
                except:
                    pass
            
            pairs.append({
                "pair_num": pair_num,
                "direction": direction,
                "names": names,
                "score": score
            })
        except:
            continue
    
    return pairs

def extract_board_result(driver, pair_num, direction, board_num):
    """Extract board result from pair summary page."""
    try:
        time.sleep(0.5)
        rows = driver.find_elements(By.XPATH, f"//tr[@onclick]")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if not cells:
                continue
            
            try:
                board_text = cells[0].text.strip()
                if board_text == str(board_num):
                    result_text = cells[2].text.strip() if len(cells) > 2 else None
                    return result_text
            except:
                continue
        
        return None
    except:
        return None

def main():
    driver = None
    
    try:
        print(f"Scraping Vugraph Event {EVENT_ID} - Board {BOARD_NUM}")
        driver = setup_driver()
        
        # Load event page
        event_url = f"{BASE_URL}eventresults.php?event={EVENT_ID}"
        print(f"Loading event results...")
        driver.get(event_url)
        time.sleep(3)
        
        # Get all pairs
        print("Extracting pair information...")
        pairs = extract_pairs_from_event_page(driver)
        
        ns_pairs = sorted([p for p in pairs if p['direction'] == 'NS'], 
                         key=lambda x: float(x['score']) if x['score'] else 0, reverse=True)
        ew_pairs = sorted([p for p in pairs if p['direction'] == 'EW'], 
                         key=lambda x: float(x['score']) if x['score'] else 0, reverse=True)
        
        all_results = []
        total = len(ns_pairs) + len(ew_pairs)
        
        print(f"Fetching Board {BOARD_NUM} results for {total} pairs...")
        
        # Process N-S pairs
        for i, pair in enumerate(ns_pairs):
            pair_url = f"{BASE_URL}pairsummary.php?event={EVENT_ID}&section={SECTION}&pair={pair['pair_num']}&direction={pair['direction']}"
            driver.get(pair_url)
            
            result_text = extract_board_result(driver, pair['pair_num'], pair['direction'], BOARD_NUM)
            
            if result_text:
                all_results.append({
                    "pair_names": pair['names'],
                    "pair_num": pair['pair_num'],
                    "direction": "N-S",
                    "result": result_text,
                    "score": pair['score']
                })
                status = "✓"
            else:
                status = "?"
            
            print(f"  [{i+1}/{len(ns_pairs)}] Pair {pair['pair_num']:2} (N-S) {status}")
            time.sleep(0.3)
        
        # Process E-W pairs
        for i, pair in enumerate(ew_pairs):
            pair_url = f"{BASE_URL}pairsummary.php?event={EVENT_ID}&section={SECTION}&pair={pair['pair_num']}&direction={pair['direction']}"
            driver.get(pair_url)
            
            result_text = extract_board_result(driver, pair['pair_num'], pair['direction'], BOARD_NUM)
            
            if result_text:
                all_results.append({
                    "pair_names": pair['names'],
                    "pair_num": pair['pair_num'],
                    "direction": "E-W",
                    "result": result_text,
                    "score": pair['score']
                })
                status = "✓"
            else:
                status = "?"
            
            print(f"  [{len(ns_pairs)+i+1}/{total}] Pair {pair['pair_num']:2} (E-W) {status}")
            time.sleep(0.3)
        
        # Save results
        output_file = "board1_all_pairs.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved {len(all_results)}/{total} results to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
