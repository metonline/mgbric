#!/usr/bin/env python3
"""
Quick test: Fetch hands for Board 1 only to validate the approach.
Tests each step of the data pipeline before running full fetch.
"""

import json
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

EVENT_ID = 404377
BASE_URL = "https://clubs.vugraph.com/hosgoru/"

print("""
╔════════════════════════════════════════════════════════════════════╗
║                   BOARD 1 HANDS FETCH TEST                         ║
║                                                                    ║
║  This script tests the player-based fetching approach on Board 1  ║
║  to validate data before running full 30-board fetch              ║
╚════════════════════════════════════════════════════════════════════╝
""")

# Setup driver
print("\n[1/5] Setting up Selenium driver...")
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(
    service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
    options=options
)

try:
    # Step 1: Get pairs
    print("[2/5] Fetching pairs list...")
    
    event_url = f"{BASE_URL}eventresults.php?event={EVENT_ID}"
    driver.get(event_url)
    time.sleep(2)
    
    links = driver.find_elements(By.XPATH, "//a[contains(@href, 'pairsummary.php')]")
    
    pairs = []
    for link in links:
        href = link.get_attribute("href")
        if "pair=" in href:
            match = re.search(r'pair=(\d+)', href)
            if match:
                pair_num = int(match.group(1))
                pair_key = f"{pair_num}"
                if pair_key not in [p['pair_num'] for p in pairs]:
                    pairs.append({'url': href, 'pair_num': pair_num})
    
    pairs = sorted(pairs, key=lambda x: x['pair_num'])[:5]  # Test with first 5 pairs
    
    print(f"   ✓ Found {len(pairs)} pairs")
    
    # Step 2: For each pair, navigate to Board 1
    print("\n[3/5] Fetching Board 1 from multiple pairs...")
    
    board1_sources = {}
    
    for pair in pairs:
        pair_num = pair['pair_num']
        print(f"\n   Pair {pair_num}:")
        
        # Get pair summary page
        driver.get(pair['url'])
        time.sleep(1)
        
        # Find Board 1 link
        try:
            tables = driver.find_elements(By.TAG_NAME, "table")
            if len(tables) >= 2:
                rows = tables[1].find_elements(By.TAG_NAME, "tr")
                board1_found = False
                
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells and cells[0].text.strip() == "1":
                        # Found Board 1 row
                        try:
                            link = row.find_element(By.XPATH, ".//a[contains(@href, 'boarddetails.php')]")
                            board_url = link.get_attribute("href")
                            print(f"     - Found Board 1 link")
                            
                            # Navigate to board details
                            driver.get(board_url)
                            time.sleep(1)
                            
                            # Extract hands
                            page_text = driver.find_element(By.TAG_NAME, "body").text
                            
                            # Parse hands
                            hands = {'N': {}, 'S': {}, 'E': {}, 'W': {}}
                            lines = page_text.split('\n')
                            
                            for line in lines:
                                if any(suit in line for suit in ['S:', 'H:', 'D:', 'C:']):
                                    pattern = r'([SHDC]):([A2-9TJKQa2-9tjkq]+)'
                                    matches = re.findall(pattern, line, re.IGNORECASE)
                                    
                                    if matches and len(matches) == 4:
                                        # Found a complete hand
                                        hand_dict = {}
                                        for suit, cards in matches:
                                            hand_dict[suit.upper()] = cards.upper()
                                        
                                        if all(hand_dict.values()):
                                            # Determine which player
                                            if 'North' in lines[max(0, lines.index(line)-2):lines.index(line)]:
                                                hands['N'] = hand_dict
                                            elif 'South' in lines[max(0, lines.index(line)-2):lines.index(line)]:
                                                hands['S'] = hand_dict
                                            elif 'East' in lines[max(0, lines.index(line)-2):lines.index(line)]:
                                                hands['E'] = hand_dict
                                            elif 'West' in lines[max(0, lines.index(line)-2):lines.index(line)]:
                                                hands['W'] = hand_dict
                            
                            # Store if any hands found
                            if any(hands.values()):
                                source_key = f"pair_{pair_num}"
                                board1_sources[source_key] = hands
                                print(f"     - ✓ Extracted hands")
                                
                                for compass, hand in hands.items():
                                    if hand and any(hand.values()):
                                        card_count = sum(len(v) for v in hand.values())
                                        print(f"       {compass}: {card_count} cards - {hand}")
                            else:
                                print(f"     - ⚠ No hands found on page")
                            
                            board1_found = True
                            break
                        except Exception as e:
                            print(f"     - ✗ Error: {e}")
                
                if not board1_found:
                    print(f"     - ⚠ Board 1 not found in pair summary")
        
        except Exception as e:
            print(f"   ✗ Error processing pair: {e}")
    
    # Step 3: Analyze results
    print("\n[4/5] Analyzing cross-checks...")
    
    if not board1_sources:
        print("   ✗ No hands were extracted from any pair!")
        print("   This suggests the hand display format on Vugraph is different than expected.")
    else:
        print(f"   ✓ Extracted from {len(board1_sources)} pairs")
        
        # Check if hands match across pairs
        for compass in ['N', 'S', 'E', 'W']:
            hands_for_compass = {}
            for source, hands in board1_sources.items():
                if hands.get(compass):
                    hand_key = json.dumps(hands[compass], sort_keys=True)
                    if hand_key not in hands_for_compass:
                        hands_for_compass[hand_key] = []
                    hands_for_compass[hand_key].append(source)
            
            if hands_for_compass:
                if len(hands_for_compass) == 1:
                    print(f"\n   ✓ {compass} (North/South/East/West):")
                    hand, sources = list(hands_for_compass.items())[0]
                    print(f"      {hand}")
                    print(f"      Sources: {', '.join(sources)}")
                else:
                    print(f"\n   ⚠ {compass}: {len(hands_for_compass)} different hands found!")
                    for i, (hand_data, sources) in enumerate(hands_for_compass.items(), 1):
                        print(f"      Variant {i}: {hand_data[:50]}... (from {', '.join(sources)})")
    
    # Step 4: Save results
    print("\n[5/5] Saving test results...")
    
    test_results = {
        'status': 'success' if board1_sources else 'failed',
        'board': 1,
        'pairs_tested': len(pairs),
        'sources_found': len(board1_sources),
        'hands_data': board1_sources,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('test_board1_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"   ✓ Saved to test_board1_results.json")
    
    # Final summary
    print(f"\n{'='*70}")
    print(f"TEST RESULTS FOR BOARD 1")
    print(f"{'='*70}")
    print(f"\nStatus:        {'✓ SUCCESS' if board1_sources else '✗ FAILED'}")
    print(f"Pairs tested:  {len(pairs)}")
    print(f"Hands found:   {len(board1_sources)}")
    
    if board1_sources:
        print(f"\nRecommendation: Run full fetch with fetch_hands_with_validation.py")
        print(f"                (This test shows the approach works)")
    else:
        print(f"\nRecommendation: Inspect Vugraph page structure")
        print(f"                The hand display format may be different than expected")
        print(f"                Run: python inspect_page_for_hands.py")
    
    print(f"\n{'='*70}\n")

finally:
    driver.quit()
