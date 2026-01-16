#!/usr/bin/env python3
"""
Corrected scraper: Extract Board 1 data with correct individual scores.
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
            
            pairs.append({
                "pair_num": pair_num,
                "direction": direction,
                "names": names
            })
        except:
            continue
    
    return pairs

def extract_board1_data(driver, pair_num, direction, board_num=1):
    """Extract Board 1 data: contract, result, and individual score from pair summary page."""
    try:
        time.sleep(0.5)
        
        # Find the specific board row
        rows = driver.find_elements(By.XPATH, "//tr[@onclick]")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if not cells or len(cells) < 4:
                continue
            
            try:
                board_text = cells[0].text.strip()
                if board_text == str(board_num):
                    # Found Board 1 row
                    # cells[2] = Result (points)
                    # cells[3] = Score (individual board score)
                    
                    result_points = cells[2].text.strip()
                    board_score = cells[3].text.strip()
                    
                    try:
                        board_score = float(board_score)
                    except:
                        board_score = None
                    
                    # Navigate to board details page to get contract
                    onclick = row.get_attribute("onclick")
                    board_url = None
                    
                    match = re.search(r"location\.href='([^']*)'", onclick)
                    if match:
                        board_url = match.group(1)
                    
                    contract = "?"
                    if board_url:
                        if not board_url.startswith("http"):
                            board_url = BASE_URL + board_url
                        
                        driver.get(board_url)
                        time.sleep(1)
                        
                        try:
                            page_text = driver.find_element(By.TAG_NAME, "body").text
                            # Look for contract pattern
                            m = re.search(r'\b([1-7][CDHSNTcdhnstnt]+(?:\*)?)\b', page_text)
                            if m:
                                contract = m.group(1).upper()
                        except:
                            pass
                    
                    return {
                        "contract": contract,
                        "result": result_points,
                        "board_score": board_score
                    }
            except:
                continue
        
        return None
        
    except Exception as e:
        return None

def main():
    driver = None
    
    try:
        print(f"Corrected scraper: Event {EVENT_ID}, Board {BOARD_NUM}")
        print(f"Collecting: Pairs, contracts, results, and individual board scores\n")
        
        driver = setup_driver()
        
        # Load event page
        event_url = f"{BASE_URL}eventresults.php?event={EVENT_ID}"
        print("Loading event results...")
        driver.get(event_url)
        time.sleep(3)
        
        # Get all pairs
        print("Extracting pair information...")
        pairs = extract_pairs_from_event_page(driver)
        
        ns_pairs = [p for p in pairs if p['direction'] == 'NS']
        ew_pairs = [p for p in pairs if p['direction'] == 'EW']
        
        all_results = []
        total = len(ns_pairs) + len(ew_pairs)
        
        print(f"\nFetching Board {BOARD_NUM} complete data for {total} pairs...")
        print("=" * 90)
        
        # Process N-S pairs
        for i, pair in enumerate(ns_pairs):
            pair_url = f"{BASE_URL}pairsummary.php?event={EVENT_ID}&section={SECTION}&pair={pair['pair_num']}&direction={pair['direction']}"
            driver.get(pair_url)
            
            # Extract board data with individual score
            data = extract_board1_data(driver, pair['pair_num'], pair['direction'], BOARD_NUM)
            
            if data:
                result_entry = {
                    "pair_names": pair['names'],
                    "pair_num": pair['pair_num'],
                    "direction": "N-S",
                    "contract": data['contract'],
                    "result": data['result'],
                    "score": data['board_score']
                }
                all_results.append(result_entry)
                status = "✓"
            else:
                status = "✗"
            
            print(f"[{i+1:2}/{len(ns_pairs):2}] Pair {pair['pair_num']:2} | {pair['names'][:40]:40} | {status}")
            time.sleep(0.3)
        
        # Process E-W pairs
        for i, pair in enumerate(ew_pairs):
            pair_url = f"{BASE_URL}pairsummary.php?event={EVENT_ID}&section={SECTION}&pair={pair['pair_num']}&direction={pair['direction']}"
            driver.get(pair_url)
            
            data = extract_board1_data(driver, pair['pair_num'], pair['direction'], BOARD_NUM)
            
            if data:
                result_entry = {
                    "pair_names": pair['names'],
                    "pair_num": pair['pair_num'],
                    "direction": "E-W",
                    "contract": data['contract'],
                    "result": data['result'],
                    "score": data['board_score']
                }
                all_results.append(result_entry)
                status = "✓"
            else:
                status = "✗"
            
            print(f"[{len(ns_pairs)+i+1:2}/{total:2}] Pair {pair['pair_num']:2} | {pair['names'][:40]:40} | {status}")
            time.sleep(0.3)
        
        print("=" * 90)
        
        # Save results
        output_file = "board1_correct_scores.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved corrected Board {BOARD_NUM} data to {output_file}")
        
        # Show sample
        print("\nSample results (with individual board scores):")
        for result in all_results[:5]:
            print(f"  {result['pair_names'][:40]:40} | {result['contract']:5} {result['result']:5} | {result['score']:6.2f}%")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
