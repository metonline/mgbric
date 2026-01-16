#!/usr/bin/env python3
"""
Extract DD values from BBO hand viewer pages automatically using Selenium.
For each board, opens the BBO page and scrapes the DD table.
"""

import json
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def hand_to_lin(board_data):
    """Convert hand data to LIN format for BBO URL"""
    hands = board_data.get('hands', {})
    
    def format_hand(player_hand):
        if not player_hand:
            return 'SDHC'
        suits = ['S', 'H', 'D', 'C']
        return ''.join([suits[i] + (player_hand.get(s, '-')) for i, s in enumerate(suits)])
    
    n_hand = format_hand(hands.get('North', {}))
    s_hand = format_hand(hands.get('South', {}))
    e_hand = format_hand(hands.get('East', {}))
    w_hand = format_hand(hands.get('West', {}))
    
    dealer = board_data.get('dealer', 'N').lower()
    lin_string = f"md|{dealer}{s_hand},{w_hand},{n_hand},{e_hand}|sv|n"
    
    return lin_string

def extract_dd_from_bbo(board_num, board_data):
    """
    Open BBO hand viewer for a board and extract DD table values.
    Returns dict with DD tricks for each suit/player combination.
    """
    try:
        lin = hand_to_lin(board_data)
        url = f"https://www.bridgebase.com/tools/handviewer.html?bbo=y&lin={lin}"
        
        print(f"  Opening BBO for Board {board_num}...", flush=True)
        
        # Create headless browser
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        
        driver.get(url)
        
        # Wait for DD table to load
        wait = WebDriverWait(driver, 10)
        
        # Try to find DD table - BBO uses various possible class names
        dd_table_selectors = [
            'dd-table',
            'double-dummy',
            'DD',
            'dd-analysis',
            '[class*="dd"]',
        ]
        
        dd_data = {}
        
        # Look for DD table cells
        try:
            # BBO typically shows DD in a structured table
            table_rows = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
            )
            
            denominations = ['NT', 'S', 'H', 'D', 'C']
            players = ['N', 'S', 'E', 'W']
            
            for row_idx, row in enumerate(table_rows):
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 5:  # Should have denom + 4 player cells
                    denom = cells[0].text.strip()
                    if denom in denominations:
                        for col_idx in range(1, 5):
                            tricks_text = cells[col_idx].text.strip()
                            if tricks_text and tricks_text != '-':
                                try:
                                    tricks = int(tricks_text)
                                    player = players[col_idx - 1]
                                    dd_data[f"{denom}{player}"] = tricks
                                except ValueError:
                                    pass
        except:
            pass
        
        driver.quit()
        
        if dd_data and len(dd_data) == 20:  # Should have 5 denoms × 4 players
            print(f"  ✓ Extracted {len(dd_data)} DD values")
            return dd_data
        else:
            print(f"  ✗ Could not extract complete DD table (got {len(dd_data)} values)")
            return None
    
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def main():
    # Check if Selenium/Chrome available
    try:
        import selenium
        print("Selenium available - will attempt to extract from BBO\n")
    except ImportError:
        print("ERROR: Selenium not installed")
        print("Install with: pip install selenium")
        print("\nAlternatively, manually input DD values using the web form at:")
        print("http://localhost:8000/dd_input.html")
        return
    
    db_path = 'app/www/hands_database.json'
    
    print("Loading database...")
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    boards = data['events']['hosgoru_04_01_2026']['boards']
    
    print(f"Extracting DD values from BBO for {len(boards)} boards...\n")
    
    updated_count = 0
    for board_num_str in sorted(boards.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        board_num = int(board_num_str)
        board = boards[board_num_str]
        
        print(f"Board {board_num}:", end=" ")
        
        dd_values = extract_dd_from_bbo(board_num, board)
        if dd_values and len(dd_values) == 20:
            board['dd_analysis'] = dd_values
            updated_count += 1
        else:
            print(f"  Skipped (could not extract)")
        
        time.sleep(1)  # Rate limiting to avoid overwhelming BBO
    
    # Save updated database
    print(f"\nSaving updated database...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {updated_count}/{len(boards)} boards")
    print(f"Saved to {db_path}")

if __name__ == '__main__':
    main()
