#!/usr/bin/env python3
"""
Enhanced scraper: Extract complete Board 1 data including contracts and verified scores.
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
    """Initialize Chrome driver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    
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

def extract_board_details(driver, pair_num, direction, board_num):
    """Extract complete board details including contract from boarddetails page."""
    try:
        time.sleep(0.5)
        
        # Find the board row in pair summary page
        rows = driver.find_elements(By.XPATH, "//tr[@onclick]")
        board_row = None
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if not cells:
                continue
            
            try:
                board_text = cells[0].text.strip()
                if board_text == str(board_num):
                    board_row = row
                    break
            except:
                continue
        
        if not board_row:
            return None
        
        # Navigate to board details page
        onclick = board_row.get_attribute("onclick")
        board_url = None
        
        match = re.search(r"location\.href='([^']*)'", onclick)
        if match:
            board_url = match.group(1)
        
        if not board_url:
            return None
        
        # Full URL
        if not board_url.startswith("http"):
            board_url = BASE_URL + board_url
        
        driver.get(board_url)
        time.sleep(1)
        
        # Extract contract and result from boarddetails page
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Look for contract: patterns like "4S", "3NT", "7C", etc.
        contract = None
        result = None
        
        # Contract pattern: digit followed by suit/NT
        match = re.search(r'\b([1-7][CDHSNTcdhnstnt]+(?:\*)?)\b', page_text)
        if match:
            contract = match.group(1).upper()
        
        # Result pattern: tricks over/under (e.g., +1, -2, =)
        match = re.search(r'([-+]\d+|=|PASS)', page_text)
        if match:
            result = match.group(1)
        
        return {
            "contract": contract,
            "result": result,
            "url": board_url
        }
        
    except Exception as e:
        return None

def main():
    driver = None
    
    try:
        print(f"Enhanced scraper: Event {EVENT_ID}, Board {BOARD_NUM}")
        print(f"Collecting: Pair names, directions, scores, contracts, and results\n")
        
        driver = setup_driver()
        
        # Load event page
        event_url = f"{BASE_URL}eventresults.php?event={EVENT_ID}"
        print("Loading event results...")
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
        
        print(f"\nFetching Board {BOARD_NUM} complete details for {total} pairs...")
        print("=" * 80)
        
        # Process N-S pairs
        for i, pair in enumerate(ns_pairs):
            pair_url = f"{BASE_URL}pairsummary.php?event={EVENT_ID}&section={SECTION}&pair={pair['pair_num']}&direction={pair['direction']}"
            driver.get(pair_url)
            
            # Extract board details
            details = extract_board_details(driver, pair['pair_num'], pair['direction'], BOARD_NUM)
            
            result_entry = {
                "pair_names": pair['names'],
                "pair_num": pair['pair_num'],
                "direction": "N-S",
                "contract": details['contract'] if details and details['contract'] else "?",
                "result": details['result'] if details and details['result'] else "?",
                "score": pair['score']
            }
            
            all_results.append(result_entry)
            
            status = "✓" if details else "?"
            print(f"[{i+1:2}/{len(ns_pairs):2}] Pair {pair['pair_num']:2} | {pair['names'][:35]:35} | {status}")
            
            time.sleep(0.3)
        
        # Process E-W pairs
        for i, pair in enumerate(ew_pairs):
            pair_url = f"{BASE_URL}pairsummary.php?event={EVENT_ID}&section={SECTION}&pair={pair['pair_num']}&direction={pair['direction']}"
            driver.get(pair_url)
            
            details = extract_board_details(driver, pair['pair_num'], pair['direction'], BOARD_NUM)
            
            result_entry = {
                "pair_names": pair['names'],
                "pair_num": pair['pair_num'],
                "direction": "E-W",
                "contract": details['contract'] if details and details['contract'] else "?",
                "result": details['result'] if details and details['result'] else "?",
                "score": pair['score']
            }
            
            all_results.append(result_entry)
            
            status = "✓" if details else "?"
            print(f"[{len(ns_pairs)+i+1:2}/{total:2}] Pair {pair['pair_num']:2} | {pair['names'][:35]:35} | {status}")
            
            time.sleep(0.3)
        
        print("=" * 80)
        
        # Save results
        output_file = "board1_complete_details.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved complete Board {BOARD_NUM} details to {output_file}")
        
        # Show sample
        print("\nSample results:")
        for result in all_results[:3]:
            print(f"  {result['pair_names'][:40]:40} | {result['contract']:5} {result['result']:3} | {result['score']:6.2f}%")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
