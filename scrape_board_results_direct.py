#!/usr/bin/env python3
"""
Selenium scraper that directly extracts all pair results from pair summary pages.
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
    # Comment out for headless mode
    # options.add_argument("--headless")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def extract_pairs_from_event_page(driver):
    """Extract all pair info from event results page."""
    time.sleep(2)
    
    # Find all rows with onclick handlers
    rows = driver.find_elements(By.XPATH, "//tr[@onclick]")
    
    pairs = []
    
    for row in rows:
        try:
            onclick = row.get_attribute("onclick")
            
            # Extract pair number and direction from onclick
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
                "score": score
            })
        except Exception as e:
            continue
    
    return pairs

def extract_board_from_pair_summary(driver, pair_info, board_num):
    """Extract board result directly from pair summary page table."""
    try:
        time.sleep(1)
        
        # Find table rows for this board
        # The table is structure: Board | Opponent | Result | Score
        rows = driver.find_elements(By.XPATH, f"//tr[@onclick]")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if not cells:
                continue
            
            try:
                # First cell is board number
                board_text = cells[0].text.strip()
                if board_text == str(board_num):
                    # Found the right board
                    # cells[2] is the "Sonuç" (Result) column
                    result_text = cells[2].text.strip() if len(cells) > 2 else None
                    score_text = cells[3].text.strip() if len(cells) > 3 else None
                    
                    # Navigate to board details page to get contract info
                    onclick = row.get_attribute("onclick")
                    board_url = None
                    if "boarddetails.php" in onclick:
                        # Extract URL from onclick
                        match = re.search(r"'([^']*boarddetails\.php[^']*)'", onclick)
                        if match:
                            board_url = match.group(1)
                    
                    if board_url:
                        driver.execute_script(f"window.open('{board_url}', '_blank')")
                        time.sleep(2)
                        
                        # Get the new window and switch to it
                        windows = driver.window_handles
                        if len(windows) > 1:
                            driver.switch_to.window(windows[-1])
                            time.sleep(1)
                            
                            # Extract contract and result
                            page_text = driver.find_element(By.TAG_NAME, "body").text
                            
                            # Look for contract pattern (e.g., "3NT", "4S", etc.)
                            contract = None
                            result_contract = None
                            
                            # Contract patterns: 1-7 followed by C/D/H/S/NT
                            match = re.search(r'\b([1-7][CDHSNTcdhnstnt]+(?:\*)?)\b', page_text)
                            if match:
                                contract = match.group(1).upper()
                            
                            # Result patterns: +X, -X, =
                            match = re.search(r'([-+]?\d+|=)', page_text)
                            if match:
                                result_contract = match.group(1)
                            
                            # Close this window and go back
                            driver.close()
                            driver.switch_to.window(windows[0])
                            
                            return {
                                "result_points": result_text,
                                "score": score_text,
                                "contract": contract,
                                "result": result_contract
                            }
                    else:
                        # Just return what we can extract from the pair summary page
                        return {
                            "result_points": result_text,
                            "score": score_text
                        }
            except Exception as e:
                continue
        
        return None
        
    except Exception as e:
        print(f"    Error extracting board: {e}")
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
        print(f"Loading event results: {event_url}")
        driver.get(event_url)
        time.sleep(3)
        
        # Extract all pairs
        print("Extracting pair information...")
        pairs = extract_pairs_from_event_page(driver)
        
        print(f"Found {len(pairs)} pairs total")
        print(f"  N-S pairs: {len([p for p in pairs if p['direction'] == 'NS'])}")
        print(f"  E-W pairs: {len([p for p in pairs if p['direction'] == 'EW'])}")
        
        # Group by direction and sort by score
        ns_pairs = sorted([p for p in pairs if p['direction'] == 'NS'], key=lambda x: float(x['score']) if x['score'] else 0, reverse=True)
        ew_pairs = sorted([p for p in pairs if p['direction'] == 'EW'], key=lambda x: float(x['score']) if x['score'] else 0, reverse=True)
        
        # Fetch board details for each pair
        all_results = []
        
        print(f"\nFetching Board {BOARD_NUM} details for all pairs...")
        
        combined_pairs = [(p, 'N-S') for p in ns_pairs] + [(p, 'E-W') for p in ew_pairs]
        
        for i, (pair, direction_name) in enumerate(combined_pairs[:5]):  # Test with first 5
            print(f"  [{i+1}/5] Pair {pair['pair_num']:2} ({direction_name}): {pair['names'][:40]}...", end=" ")
            
            # Navigate to pair summary
            pair_url = f"{BASE_URL}pairsummary.php?event={EVENT_ID}&section={SECTION}&pair={pair['pair_num']}&direction={pair['direction']}"
            driver.get(pair_url)
            
            # Extract board score
            board_data = extract_board_from_pair_summary(driver, pair, BOARD_NUM)
            
            if board_data:
                result = {
                    "pair_names": pair['names'],
                    "pair_num": pair['pair_num'],
                    "direction": direction_name,
                    "result": board_data.get('result_points'),
                    "score": pair['score']
                }
                all_results.append(result)
                print(f"✓ {board_data.get('result_points')} pts")
            else:
                print("✗")
            
            time.sleep(1)
        
        # Save results
        output_file = "board1_results.json"
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
