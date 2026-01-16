#!/usr/bin/env python3
"""
Automated DD Value Extraction from BBO
Attempts to extract Double Dummy values from BBO for all boards.
Falls back to manual input if automated extraction fails.
"""

import json
import time
import sys
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("\n" + "=" * 70)
    print("ERROR: Selenium is not installed")
    print("=" * 70)
    print("\nTo use automated extraction, install Selenium:")
    print("  pip install selenium")
    print("\nAlternatively, use the manual input interface:")
    print("  Open: http://localhost:8000/dd_input.html")
    print("=" * 70)
    sys.exit(1)

def hands_to_lin(hands):
    """Convert hands dict to LIN format string for BBO URL."""
    suits = ['S', 'H', 'D', 'C']
    
    lin_parts = []
    for direction in ['north', 'south', 'east', 'west']:
        hand_str = ""
        for suit in suits:
            cards = hands.get(direction, {}).get(suit, '')
            hand_str += cards
        lin_parts.append(hand_str)
    
    return " ".join(lin_parts)

def extract_dd_from_bbo(board_number, hands):
    """
    Extract DD values from BBO hand viewer.
    Returns dict with 20 values (5 suits × 4 players).
    """
    
    lin_string = hands_to_lin(hands)
    url = f"https://www.bridgebase.com/tools/handviewer.html?bbo=y&lin={lin_string}"
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = None
    
    try:
        print(f"  Board {board_number}: Opening BBO...")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        time.sleep(2)  # Wait for JavaScript rendering
        
        # Try to find DD table
        print(f"  Board {board_number}: Looking for DD table...")
        dd_values = {}
        
        try:
            # Try to find any table element
            tables = driver.find_elements(By.TAG_NAME, "table")
            
            if not tables:
                print(f"  Board {board_number}: ⚠ No tables found on page")
                return None
            
            # Look through each table for DD data
            suits = ['NT', 'S', 'H', 'D', 'C']
            players = ['N', 'S', 'E', 'W']
            
            for table in tables:
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    
                    for suit_idx, suit in enumerate(suits):
                        if suit_idx + 1 < len(rows):
                            cells = rows[suit_idx + 1].find_elements(By.TAG_NAME, "td")
                            
                            # Should have suit label + 4 player cells
                            if len(cells) >= 5:
                                for player_idx, player in enumerate(players):
                                    try:
                                        tricks_text = cells[player_idx + 1].text.strip()
                                        if tricks_text and tricks_text != '-':
                                            tricks = int(tricks_text)
                                            dd_values[f"{suit}{player}"] = tricks
                                    except (ValueError, IndexError):
                                        pass
                    
                    if len(dd_values) == 20:
                        break
                        
                except:
                    continue
            
            if len(dd_values) == 20:
                print(f"  Board {board_number}: ✓ Extracted all 20 values")
                return dd_values
            elif len(dd_values) > 0:
                print(f"  Board {board_number}: ⚠ Partial extraction ({len(dd_values)}/20)")
                return None
            else:
                print(f"  Board {board_number}: ✗ Could not find DD table")
                return None
        
        except Exception as e:
            print(f"  Board {board_number}: ✗ Error parsing page - {str(e)[:50]}")
            return None
        
    except Exception as e:
        print(f"  Board {board_number}: ✗ Browser error - {str(e)[:50]}")
        return None
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    print("\n" + "=" * 70)
    print("BBO DD VALUES EXTRACTOR - AUTOMATED")
    print("=" * 70)
    
    # Load database
    db_path = Path('app/www/hands_database.json')
    if not db_path.exists():
        print(f"ERROR: {db_path} not found!")
        sys.exit(1)
    
    print(f"\nLoading database...")
    with open(db_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    boards = database['events']['hosgoru_04_01_2026']['boards']
    print(f"Found {len(boards)} boards\n")
    print("Processing...")
    print("-" * 70)
    
    success_count = 0
    failed_count = 0
    failed_boards = []
    
    # Extract DD for boards 2-30 (Board 1 already has real values)
    for board_num in range(2, 31):
        hands = boards[str(board_num)].get('hands', {})
        
        if not hands:
            print(f"  Board {board_num}: ✗ No hands found")
            failed_boards.append(board_num)
            continue
        
        dd_values = extract_dd_from_bbo(board_num, hands)
        
        if dd_values and len(dd_values) == 20:
            boards[str(board_num)]['dd_analysis'] = dd_values
            success_count += 1
        else:
            failed_count += 1
            failed_boards.append(board_num)
        
        # Rate limiting
        if board_num < 30:
            time.sleep(2)
    
    # Save updated database
    print("-" * 70)
    print("\nSaving updated database...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"✓ Successfully extracted: {success_count}/29 boards")
    
    if failed_count > 0:
        print(f"✗ Failed extraction: {failed_count} boards")
        print(f"\nFailed boards: {', '.join(map(str, failed_boards))}")
        print("\nThese can be filled manually using:")
        print("  http://localhost:8000/dd_input.html")
    
    if success_count == 29:
        print("\n🎉 All boards successfully updated!")
    
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
