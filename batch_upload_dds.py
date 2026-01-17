#!/usr/bin/env python3
"""
Batch upload bridge hands to DDS solver and extract exact DD values.
Uses Selenium to automate the web interface at dds.bridgewebs.com
Updates hands_database.json with verified results.
"""

import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import subprocess

def create_pbn_file(database):
    """Create PBN format file from hands_database.json for DDS solver."""
    pbn_lines = []
    
    for board_id, board_data in sorted(database.items(), key=lambda x: int(x[0])):
        try:
            # PBN format: [Event "..."] [Site "..."] [Deal "N:..."] etc
            event = board_data.get('tournament', f'Board {board_id}').replace('"', "'")
            dealer = board_data.get('dealer', 'N')
            vuln = board_data.get('vulnerability', 'None')
            
            # Map vulnerability to PBN format
            vuln_map = {'None': 'None', 'NS': 'NS', 'EW': 'EW', 'Both': 'All',
                       'N': 'NS', 'S': 'NS', 'E': 'EW', 'W': 'EW'}
            vuln_pbn = vuln_map.get(vuln, 'None')
            
            # Create deal string: N:Nspades.Nhearts.Ndiamonds.Nclubs Espades...
            def parse_hand(hand_str):
                """Convert 'SAT73HAQ6DKJ7CK83' to 'AT73.AQ6.KJ7.K83'"""
                suits = {'S': '', 'H': '', 'D': '', 'C': ''}
                current_suit = None
                for char in hand_str:
                    if char in suits:
                        current_suit = char
                    elif current_suit:
                        suits[current_suit] += char
                return '.'.join([suits[s] for s in ['S', 'H', 'D', 'C']])
            
            n_pbn = parse_hand(board_data['N'])
            e_pbn = parse_hand(board_data['E'])
            s_pbn = parse_hand(board_data['S'])
            w_pbn = parse_hand(board_data['W'])
            
            deal_str = f"{dealer}:{n_pbn} {e_pbn} {s_pbn} {w_pbn}"
            
            # Create PBN record
            pbn_lines.append('[Event "' + event + '"]')
            pbn_lines.append(f'[Board "{board_id}"]')
            pbn_lines.append(f'[Dealer "{dealer}"]')
            pbn_lines.append(f'[Vulnerable "{vuln_pbn}"]')
            pbn_lines.append(f'[Deal "{deal_str}"]')
            pbn_lines.append('')  # Blank line between boards
        
        except Exception as e:
            print(f"Error converting board {board_id}: {e}")
    
    return '\n'.join(pbn_lines)


def solve_with_dds_web(pbn_content):
    """
    Upload PBN to DDS solver and extract results.
    Uses Selenium to automate the web interface.
    """
    try:
        # Setup Chrome options
        chrome_options = Options()
        # Don't use headless - need to interact with page
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Try to find ChromeDriver
        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except:
            print("[WARNING] ChromeDriver not found. Install with: pip install webdriver-manager")
            print("[INFO] Install ChromeDriver manually or use: pip install webdriver-manager")
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                return None
        
        print("[INFO] Opening DDS Bridge Solver...")
        driver.get("https://dds.bridgewebs.com/bsol_standalone/ddummy.html")
        
        # Wait for page to load
        time.sleep(3)
        
        # Try to find upload area/paste area
        # Different approaches depending on page structure
        try:
            # Look for textarea or input for pasting PBN
            textarea = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "textarea"))
            )
            textarea.clear()
            textarea.send_keys(pbn_content)
            print("[OK] Pasted PBN content into solver")
            
            # Look for solve/analyze button
            time.sleep(2)
            buttons = driver.find_elements(By.TAG_NAME, "button")
            solve_button = None
            for btn in buttons:
                if 'solve' in btn.text.lower() or 'analyze' in btn.text.lower():
                    solve_button = btn
                    break
            
            if solve_button:
                solve_button.click()
                print("[OK] Clicked solve button")
                
                # Wait for results
                time.sleep(5)
                
                # Extract results (page structure dependent)
                # This is simplified - actual extraction depends on DDS solver HTML structure
                page_source = driver.page_source
                
                driver.quit()
                return page_source
        
        except Exception as e:
            print(f"[ERROR] Could not interact with solver: {e}")
            print("[INFO] Manual approach needed:")
            print("1. Go to https://dds.bridgewebs.com/bsol_standalone/ddummy.html")
            print("2. Paste the PBN content below")
            print("3. Click 'Solve'")
            print("4. Copy the results and save to dd_results.html")
            print("\n" + "="*60)
            print("PBN TO PASTE:")
            print("="*60)
            print(pbn_content)
            print("="*60)
            driver.quit()
            return None
    
    except Exception as e:
        print(f"[ERROR] Selenium error: {e}")
        return None


def main():
    # Load database
    db_path = Path('hands_database.json')
    with open(db_path) as f:
        database = json.load(f)
    
    print(f"[INFO] Loaded {len(database)} boards")
    print(f"[INFO] Creating PBN file for batch upload to DDS solver...\n")
    
    # Create PBN file
    pbn_content = create_pbn_file(database)
    pbn_path = Path('hands_for_dds.pbn')
    
    with open(pbn_path, 'w', encoding='utf-8') as f:
        f.write(pbn_content)
    
    print(f"[OK] Created {pbn_path} ({len(pbn_content)} bytes)")
    print(f"\n[NEXT STEPS]")
    print(f"1. Go to: https://dds.bridgewebs.com/bsol_standalone/ddummy.html")
    print(f"2. Open {pbn_path}")
    print(f"3. Paste content or upload file")
    print(f"4. Click 'Solve All'")
    print(f"5. Save results as hands_dd_results.html")
    print(f"6. Run: python parse_dd_results.py")
    print(f"\nAttempting automatic upload with Selenium...")
    
    # Try Selenium approach (requires Chrome/Chromium installed)
    result = solve_with_dds_web(pbn_content)
    
    if result:
        print(f"[OK] Got solver results, now extract DD values...")
        # TODO: Parse HTML result and update database
    else:
        print(f"\n[INFO] Manual process:")
        print(f"- File ready: {pbn_path}")
        print(f"- Copy content and paste into DDS solver web interface")


if __name__ == '__main__':
    main()
