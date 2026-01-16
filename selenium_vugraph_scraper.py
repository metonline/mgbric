#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium Vugraph Board Hands Scraper
Fetches all board hands for specified events using browser automation
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import json
import os

EVENT_ID = 404562
EVENT_URL = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event={EVENT_ID}"
WAIT_TIME = 2    # Seconds to wait for page load

# Helper to parse hand string
def parse_hand_string(hand_str):
    suits = ['S', 'H', 'D', 'C']
    result = {s: '' for s in suits}
    hand_str = hand_str.strip()
    parts = hand_str.split()
    for i, part in enumerate(parts):
        if i < 4 and len(part) > 1:
            suit = part[0]
            cards = part[1:]
            if suit in result:
                result[suit] = cards
    return result

def extract_hands_from_html(html):
    import re
    hands = {'N': {}, 'S': {}, 'E': {}, 'W': {}}
    # Look for lines like "North: SAKQ9 HT3 DKT7 CQJ2"
    for player in ['North', 'South', 'East', 'West']:
        pattern = rf'{player}[:\s]+([SHDCA2-9]+\s+[SHDCA2-9]+\s+[SHDCA2-9]+\s+[SHDCA2-9]+)'
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            hands[player[0]] = parse_hand_string(match.group(1))
    return hands

def main():
    print("=" * 60)
    print("🌐 Selenium Vugraph Board Hands Scraper")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1200x800')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Load existing database
    db_path = r'C:\Users\metin\Desktop\BRIC\app\www\hands_database.json'
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            try:
                all_boards = json.load(f)
            except Exception:
                all_boards = {}
    else:
        all_boards = {}

    board_counter = max([int(k) for k in all_boards.keys()] or [0]) + 1


    driver.get(EVENT_URL)
    time.sleep(WAIT_TIME * 3)  # Longer wait for dynamic content

    # Parse player and board info from page text
    page_source = driver.page_source
    import re
    # Find all pairs for NS and EW
    ns_pairs = re.findall(r'\|\s*(\d+) \| ([^|]+) \| ([\d.]+) \|', page_source)
    ew_pairs = re.findall(r'\|\s*(\d+) \| ([^|]+) \| ([\d.]+) \|', page_source)
    # Try to find all pair numbers (1-30 for both NS and EW)
    # If not found, fallback to 1-30
    ns_pair_nums = [int(p[0]) for p in ns_pairs] if ns_pairs else list(range(1, 31))
    ew_pair_nums = [int(p[0]) for p in ew_pairs] if ew_pairs else list(range(1, 31))
    print(f"NS pairs: {ns_pair_nums}")
    print(f"EW pairs: {ew_pair_nums}")

    # For each section (A/B), direction (NS/EW), and pair, try boards 1-30
    for section in ['A', 'B']:
        for direction, pair_nums in [('NS', ns_pair_nums), ('EW', ew_pair_nums)]:
            for pair in pair_nums:
                for board_num in range(1, 31):
                    board_url = f"https://clubs.vugraph.com/hosgoru/boarddetails.php?event={EVENT_ID}&section={section}&pair={pair}&direction={direction}&board={board_num}"
                    driver.get(board_url)
                    time.sleep(1)
                    html = driver.page_source
                    hands = extract_hands_from_html(html)
                    has_hands = any(any(hands[p].values()) for p in ['N', 'S', 'E', 'W'])
                    if has_hands:
                        # Avoid duplicates: check if already in DB
                        already = False
                        for v in all_boards.values():
                            if v.get('tournament') == f'Tournament {EVENT_ID}' and v.get('board_num') == board_num and v.get('section', None) == section and v.get('pair', None) == str(pair) and v.get('direction', None) == direction:
                                already = True
                                break
                        if not already:
                            all_boards[str(board_counter)] = {
                                'tournament': f'Tournament {EVENT_ID}',
                                'board_num': board_num,
                                'section': section,
                                'pair': str(pair),
                                'direction': direction,
                                'N': hands['N'],
                                'S': hands['S'],
                                'E': hands['E'],
                                'W': hands['W']
                            }
                            board_counter += 1
                            print(f"    ✓ Board {board_num} ({section} {pair} {direction}) fetched")
                        else:
                            print(f"    - Board {board_num} ({section} {pair} {direction}) already in DB, skipping.")
                    else:
                        print(f"    - Board {board_num} ({section} {pair} {direction}) not found or no hands")

    for player_url in player_urls:
        driver.get(player_url)
        time.sleep(WAIT_TIME)
        # Find all board links for this player
        board_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'boarddetails.php?event=404562')]")
        board_urls = [a.get_attribute('href') for a in board_links]
        print(f"  Player {player_url} has {len(board_urls)} boards.")
        for board_url in board_urls:
            driver.get(board_url)
            time.sleep(WAIT_TIME)
            html = driver.page_source
            hands = extract_hands_from_html(html)
            has_hands = any(any(hands[p].values()) for p in ['N', 'S', 'E', 'W'])
            # Extract board_num, section, pair, direction from URL
            import re
            m = re.search(r'boarddetails\.php\?event=404562&section=([A-Z])&pair=(\d+)&direction=([NSWE]+)&board=(\d+)', board_url)
            if m:
                section, pair, direction, board_num = m.groups()
                board_num = int(board_num)
            else:
                section = pair = direction = None
                board_num = None
            if has_hands and board_num is not None:
                # Avoid duplicates: check if already in DB
                already = False
                for v in all_boards.values():
                    if v.get('tournament') == f'Tournament {EVENT_ID}' and v.get('board_num') == board_num and v.get('section', None) == section and v.get('pair', None) == pair and v.get('direction', None) == direction:
                        already = True
                        break
                if not already:
                    all_boards[str(board_counter)] = {
                        'tournament': f'Tournament {EVENT_ID}',
                        'board_num': board_num,
                        'section': section,
                        'pair': pair,
                        'direction': direction,
                        'N': hands['N'],
                        'S': hands['S'],
                        'E': hands['E'],
                        'W': hands['W']
                    }
                    board_counter += 1
                    print(f"    ✓ Board {board_num} ({section} {pair} {direction}) fetched")
                else:
                    print(f"    - Board {board_num} ({section} {pair} {direction}) already in DB, skipping.")
            else:
                print(f"    - Board {board_num} ({section} {pair} {direction}) not found or no hands")

    driver.quit()

    # Save database
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(all_boards, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Database saved: {db_path}")
    print(f"   Total boards: {len(all_boards)}")

if __name__ == '__main__':
    main()
