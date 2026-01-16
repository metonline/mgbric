#!/usr/bin/env python3
"""
Selenium-based scraper that extracts all pair data from Vugraph.
Uses onclick handlers to navigate to pair pages.
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def extract_pairs_from_event_page(driver):
    """Extract all pair info from event results page."""
    wait = WebDriverWait(driver, 10)
    time.sleep(3)
    
    # Find all rows with onclick handlers
    rows = driver.find_elements(By.XPATH, "//tr[@onclick]")
    print(f"Found {len(rows)} clickable pair rows")
    
    pairs = []
    
    for row in rows:
        try:
            # Get onclick attribute to extract pair info
            onclick = row.get_attribute("onclick")
            
            # Extract pair number and direction from onclick
            # Pattern: pairsummary.php?event=404377&section=A&pair=9&direction=NS
            match = re.search(r"pair=(\d+)&direction=(\w+)", onclick)
            if not match:
                continue
            
            pair_num = match.group(1)
            direction = match.group(2)
            
            # Get cells
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 2:
                continue
            
            # Get pair names from second cell
            names = cells[1].text.strip()
            
            # Get score from third cell
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
                "score": score,
                "onclick": onclick
            })
        except Exception as e:
            continue
    
    return pairs

def extract_board_score(driver, board_num):
    """Extract contract and result for a specific board from pair summary page."""
    try:
        # Wait for page to load
        time.sleep(1)
        
        # Look for board link
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Look for board link in text
        if f"Board {board_num}" not in body_text and f"Devre {board_num}" not in body_text:
            # Page might still be loading or board info is in different format
            time.sleep(1)
            body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Try to find board links
        board_links = driver.find_elements(By.XPATH, f"//a[contains(@href, 'boarddetails.php')]")
        
        board_url = None
        for link in board_links:
            text = link.text.strip()
            if str(board_num) in text:
                board_url = link.get_attribute("href")
                break
        
        if not board_url:
            # If no link found, try looking through page text more carefully
            return None
        
        # Navigate to board details
        current_url = driver.current_url
        if not board_url.startswith("http"):
            board_url = BASE_URL + board_url
        
        driver.get(board_url)
        time.sleep(1)
        
        # Extract contract and result from board page
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Look for contract patterns (1NT, 3NT, 4S, etc.)
        contract_match = re.search(r'([1-7][CDHSNTcdhnstnt]+)', page_text)
        contract = contract_match.group(1).upper() if contract_match else None
        
        # Look for result (like +1, -2, =, etc.)
        result_match = re.search(r'([-+]?[0-9]|[-+]=)', page_text)
        result = result_match.group(1) if result_match else None
        
        return {
            "contract": contract,
            "result": result
        }
        
    except Exception as e:
        print(f"    Error extracting board {board_num}: {e}")
        return None

def main():
    """Main function."""
    driver = None
    
    try:
        print(f"Scraping Vugraph Event {EVENT_ID}")
        print(f"Target: All pairs, Board {BOARD_NUM} results\n")
        
        driver = setup_driver()
        
        # Load event results page
        event_url = f"{BASE_URL}eventresults.php?event={EVENT_ID}"
        print(f"Loading: {event_url}")
        driver.get(event_url)
        time.sleep(3)
        
        # Extract all pairs
        print("\nExtracting pair information...")
        pairs = extract_pairs_from_event_page(driver)
        
        print(f"Found {len(pairs)} pairs total")
        print(f"  N-S pairs: {len([p for p in pairs if p['direction'] == 'NS'])}")
        print(f"  E-W pairs: {len([p for p in pairs if p['direction'] == 'EW'])}")
        
        # Group by direction
        ns_pairs = sorted([p for p in pairs if p['direction'] == 'NS'], key=lambda x: float(x['score']) if x['score'] else 0, reverse=True)
        ew_pairs = sorted([p for p in pairs if p['direction'] == 'EW'], key=lambda x: float(x['score']) if x['score'] else 0, reverse=True)
        
        # Fetch board details for each pair (limit to first 3 for testing)
        all_results = []
        
        print(f"\nFetching Board {BOARD_NUM} details...")
        
        test_limit = 3
        for i, pair in enumerate(ns_pairs[:test_limit]):
            print(f"  [{i+1}/{test_limit}] Pair {pair['pair_num']} (N-S): {pair['names'][:40]}...")
            
            # Navigate to pair summary
            pair_url = f"{BASE_URL}pairsummary.php?event={EVENT_ID}&section={SECTION}&pair={pair['pair_num']}&direction={pair['direction']}"
            driver.get(pair_url)
            
            # Extract board score
            board_data = extract_board_score(driver, BOARD_NUM)
            
            if board_data:
                result = {
                    "pair_names": pair['names'],
                    "pair_num": pair['pair_num'],
                    "direction": "N-S",
                    "contract": board_data['contract'],
                    "result": board_data['result'],
                    "score": pair['score']
                }
                all_results.append(result)
                print(f"       ✓ {board_data['contract']} {board_data['result']} ({pair['score']}%)")
            else:
                print(f"       ✗ Could not extract board data")
            
            time.sleep(1)
        
        # Save results
        output_file = "board1_scraped_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(all_results)} results to {output_file}")
        
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    main()
