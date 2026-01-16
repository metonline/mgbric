#!/usr/bin/env python3
"""
Selenium-based scraper for Vugraph tournament board results.
Handles JavaScript-rendered content and pair links.
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Configuration
EVENT_ID = 404377
SECTION = "A"
BOARD_NUM = 1
MAX_PAIRS = 26
PAIRS_PER_DIRECTION = 13

BASE_URL = "https://clubs.vugraph.com/hosgoru/"
EVENT_URL = f"{BASE_URL}eventresults.php?event={EVENT_ID}"

def setup_driver():
    """Initialize Chrome driver with proper configuration."""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    # options.add_argument("--headless")  # Comment out for debugging
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def extract_pair_links(driver):
    """Extract all pair links from the event results page."""
    wait = WebDriverWait(driver, 10)
    
    # Wait for the page to load
    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
    
    pairs = []
    
    try:
        # Find all links that contain pair information
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='pairdetail.php']")
        
        if not links:
            print("No pair detail links found, trying alternative selectors...")
            # Try alternative selectors
            links = driver.find_elements(By.XPATH, "//a[contains(@href, 'pairdetail.php')]")
        
        print(f"Found {len(links)} pair links")
        
        for link in links:
            href = link.get_attribute("href")
            text = link.text.strip()
            
            if href and "pairdetail.php" in href:
                # Extract pair number and direction from URL
                if "pair=" in href:
                    pair_num = href.split("pair=")[1].split("&")[0]
                    direction = "NS" if "direction=NS" in href else "EW"
                    
                    pairs.append({
                        "url": href,
                        "pair_num": pair_num,
                        "direction": direction,
                        "names": text
                    })
        
        print(f"Extracted {len(pairs)} pairs with links")
        for p in pairs[:3]:
            print(f"  Sample: {p}")
        
    except Exception as e:
        print(f"Error extracting pairs: {e}")
    
    return pairs

def get_board_result(driver, pair_info):
    """Navigate to pair page and extract Board 1 result."""
    try:
        print(f"\nFetching Board {BOARD_NUM} for Pair {pair_info['pair_num']} ({pair_info['direction']})...")
        
        # Navigate to pair detail page
        driver.get(pair_info["url"])
        wait = WebDriverWait(driver, 10)
        
        # Wait for page to load
        time.sleep(2)
        
        # Find board links on this pair's page
        board_links = driver.find_elements(By.XPATH, f"//a[contains(@href, 'boarddetails.php')]")
        print(f"  Found {len(board_links)} board links on this pair's page")
        
        board_url = None
        for link in board_links:
            href = link.get_attribute("href")
            text = link.text.strip()
            
            # Look for Board 1 link
            if BOARD_NUM in [int(t) for t in text.split() if t.isdigit()]:
                board_url = href
                print(f"  Found Board {BOARD_NUM} link: {href}")
                break
        
        if not board_url:
            print(f"  Board {BOARD_NUM} not found on this pair's page")
            return None
        
        # Navigate to board detail page
        driver.get(board_url)
        time.sleep(1)
        
        # Try to extract contract and result from the page
        page_source = driver.page_source
        
        # Look for contract in the page (common patterns)
        contract = extract_contract(page_source, driver)
        result = extract_result(page_source, driver)
        score = None  # Will calculate later
        
        if contract or result:
            return {
                "pair_names": pair_info["names"],
                "pair_num": pair_info["pair_num"],
                "direction": "N-S" if pair_info["direction"] == "NS" else "E-W",
                "contract": contract,
                "result": result,
                "score": score
            }
        else:
            print(f"  Could not extract contract/result")
            return None
        
    except Exception as e:
        print(f"  Error fetching board result: {e}")
        return None

def extract_contract(page_source, driver):
    """Extract contract from page source or page elements."""
    try:
        # Try to find contract in text content
        body = driver.find_element(By.TAG_NAME, "body").text
        
        # Look for common contract patterns like "3NT", "4S", "7NT", etc
        import re
        contracts = re.findall(r'([1-7][CDHSNTcdntsnt]+(?:\+\d+|-\d+|=)?)', body)
        
        if contracts:
            return contracts[0]
    except:
        pass
    
    return None

def extract_result(page_source, driver):
    """Extract result (tricks over/under) from page elements."""
    try:
        body = driver.find_element(By.TAG_NAME, "body").text
        
        # Look for result patterns
        import re
        results = re.findall(r'([-+]?\d+(?:\+|-|=)?)', body)
        
        if results:
            for r in results:
                if r in ['+1', '+2', '+3', '-1', '-2', '=']:
                    return r
    except:
        pass
    
    return None

def main():
    """Main scraper function."""
    driver = None
    
    try:
        print(f"Starting Selenium scraper for Event {EVENT_ID}, Board {BOARD_NUM}")
        print(f"Target URL: {EVENT_URL}\n")
        
        # Initialize driver
        driver = setup_driver()
        
        # Load event results page
        print("Loading event results page...")
        driver.get(EVENT_URL)
        time.sleep(3)
        
        # Extract pair links
        print("\nExtracting pair links...")
        pairs = extract_pair_links(driver)
        
        if not pairs:
            print("\nNo pairs found! The page might be using a different structure.")
            print("Displaying page source sample...")
            print(driver.page_source[:1000])
            return
        
        # Fetch results for each pair (limit to first 5 for testing)
        results = []
        test_limit = 5
        
        print(f"\nFetching Board {BOARD_NUM} results for {min(test_limit, len(pairs))} pairs...")
        
        for i, pair in enumerate(pairs[:test_limit]):
            result = get_board_result(driver, pair)
            if result:
                results.append(result)
                print(f"  ✓ Pair {pair['pair_num']} ({pair['direction']}): {result['contract']} {result['result']}")
            
            time.sleep(1)  # Rate limit
        
        # Save results
        output_file = "board1_results_selenium.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nSaved {len(results)} results to {output_file}")
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("\nBrowser closed.")

if __name__ == "__main__":
    main()
