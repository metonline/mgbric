#!/usr/bin/env python3
"""
Player-based Vugraph hands fetcher with cross-validation.

Strategy:
1. Get all pairs from event overview
2. For each pair, navigate to their pair summary
3. Extract all boards they played (from table)
4. For each board, navigate to board details and extract hands
5. Cross-check against multiple sources
6. Save with provenance tracking
"""

import json
import time
import sys
import re
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

EVENT_ID = 404377
BASE_URL = "https://clubs.vugraph.com/hosgoru/"

class PlayerBasedHandsFetcher:
    def __init__(self):
        self.event_id = EVENT_ID
        self.base_url = BASE_URL
        self.driver = None
        
        # Track data by board with multiple sources
        self.boards_hands = defaultdict(lambda: {
            'dealer': 'N',
            'vulnerability': 'None',
            'hands': {'N': {}, 'S': {}, 'E': {}, 'W': {}},
            'sources': defaultdict(list),  # {'N': ['pair_1_NS', 'pair_2_NS'], ...}
            'raw_hands': defaultdict(list)  # Track all raw hands received
        })
        
        self.pairs_list = []
        
    def setup_driver(self):
        """Initialize Selenium driver."""
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=options
        )
    
    def get_pairs(self):
        """Get all pairs from event overview page."""
        print(f"\n{'='*70}")
        print(f"STEP 1: Fetching pairs list from event {self.event_id}")
        print(f"{'='*70}\n")
        
        url = f"{self.base_url}eventresults.php?event={self.event_id}"
        print(f"Opening: {url}\n")
        
        self.driver.get(url)
        time.sleep(3)
        
        try:
            # Find all pairsummary links
            links = self.driver.find_elements(
                By.XPATH, 
                "//a[contains(@href, 'pairsummary.php')]"
            )
            
            unique_pairs = {}
            
            for link in links:
                href = link.get_attribute("href")
                text = link.text.strip()
                
                if "pair=" in href:
                    # Extract pair number
                    match = re.search(r'pair=(\d+)', href)
                    if match:
                        pair_num = int(match.group(1))
                        pair_key = f"{pair_num}"
                        
                        if pair_key not in unique_pairs:
                            unique_pairs[pair_key] = {
                                'url': href,
                                'pair_num': pair_num,
                                'names': text
                            }
            
            self.pairs_list = sorted(unique_pairs.values(), key=lambda x: x['pair_num'])
            
            print(f"✓ Found {len(self.pairs_list)} pairs\n")
            for i, p in enumerate(self.pairs_list[:5]):
                print(f"  {i+1}. Pair {p['pair_num']:2d}: {p['names']}")
            if len(self.pairs_list) > 5:
                print(f"  ... and {len(self.pairs_list)-5} more\n")
            
            return True
            
        except Exception as e:
            print(f"✗ Error getting pairs: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_pair_boards(self, pair_info):
        """Get all boards for a specific pair from their summary page."""
        try:
            pair_num = pair_info['pair_num']
            
            print(f"  Pair {pair_num:2d}: ", end='', flush=True)
            
            self.driver.get(pair_info['url'])
            time.sleep(1.5)
            
            # Find the results table (second table is usually the results)
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            
            if len(tables) < 2:
                print(f"✗ No results table found")
                return []
            
            results_table = tables[1]
            rows = results_table.find_elements(By.TAG_NAME, "tr")
            
            boards = []
            
            for row in rows[1:]:  # Skip header row
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(cells) >= 1:
                    board_text = cells[0].text.strip()
                    
                    # Try to parse board number
                    if board_text.isdigit():
                        board_num = int(board_text)
                        
                        # Try to find boarddetails link
                        try:
                            link = row.find_element(
                                By.XPATH,
                                ".//a[contains(@href, 'boarddetails.php')]"
                            )
                            board_url = link.get_attribute("href")
                            boards.append({
                                'board_num': board_num,
                                'url': board_url,
                                'pair_num': pair_num
                            })
                        except:
                            # No direct link, construct URL
                            board_url = f"{self.base_url}boarddetails.php?event={self.event_id}&board={board_num}&pair={pair_num}"
                            boards.append({
                                'board_num': board_num,
                                'url': board_url,
                                'pair_num': pair_num
                            })
            
            print(f"✓ {len(boards)} boards")
            return boards
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return []
    
    def extract_hands_from_page(self, board_num, pair_num):
        """Extract hands from currently loaded board details page."""
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            hands = {'N': {}, 'S': {}, 'E': {}, 'W': {}}
            
            # Method 1: Parse lines with suit format "S:AK H:Q D:JT C:KQ9"
            lines = page_text.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Look for hand patterns
                if any(suit in line for suit in ['S:', 'H:', 'D:', 'C:']):
                    # This might be a hand line
                    hand_dict = self._parse_hand_line(line)
                    
                    if hand_dict and any(hand_dict.values()):
                        # Found a valid hand, try to assign to a player
                        # Look at previous lines for player name hints
                        player = self._detect_player_from_context(lines, i)
                        
                        if player and player not in hands:
                            hands[player] = hand_dict
            
            return hands
            
        except Exception as e:
            print(f"    Error extracting hands: {e}")
            return {'N': {}, 'S': {}, 'E': {}, 'W': {}}
    
    def _parse_hand_line(self, line):
        """Parse hand from line like 'S:AKQ H:J92 D:T8643 C:K7'"""
        hand = {'S': '', 'H': '', 'D': '', 'C': ''}
        
        # Pattern: suit:cards (case insensitive)
        # Cards are uppercase letters/numbers: A2-9TJKQ
        pattern = r'([SHDC]):([A2-9TJKQa2-9tjkq]+)'
        matches = re.findall(pattern, line, re.IGNORECASE)
        
        if matches:
            for suit, cards in matches:
                suit = suit.upper()
                hand[suit] = cards.upper()
        
        # Return only if we got all 4 suits
        if all(hand.values()) and sum(len(v) for v in hand.values()) == 13:
            return hand
        
        return {}
    
    def _detect_player_from_context(self, lines, current_line_idx):
        """Try to detect which player this hand belongs to."""
        # Look backwards up to 3 lines for player indicators
        for i in range(max(0, current_line_idx - 3), current_line_idx):
            prev_line = lines[i].strip().upper()
            
            if 'NORTH' in prev_line:
                return 'N'
            elif 'SOUTH' in prev_line:
                return 'S'
            elif 'EAST' in prev_line:
                return 'E'
            elif 'WEST' in prev_line:
                return 'W'
        
        return None
    
    def fetch_all_hands(self):
        """Main orchestration: fetch hands from all pairs."""
        print(f"\n{'='*70}")
        print(f"STEP 2: Fetching hands from board details pages")
        print(f"{'='*70}\n")
        
        total_pairs = len(self.pairs_list)
        
        for pair_idx, pair_info in enumerate(self.pairs_list):
            pair_num = pair_info['pair_num']
            
            # Get all boards for this pair
            boards = self.get_pair_boards(pair_info)
            
            # For each board, extract hands
            for board_info in boards:
                board_num = board_info['board_num']
                
                try:
                    self.driver.get(board_info['url'])
                    time.sleep(0.8)
                    
                    hands = self.extract_hands_from_page(board_num, pair_num)
                    
                    # Store hands with source attribution
                    for compass, hand in hands.items():
                        if hand and any(hand.values()):
                            self.boards_hands[board_num]['raw_hands'][compass].append({
                                'pair': pair_num,
                                'hand': hand
                            })
                            self.boards_hands[board_num]['sources'][compass].append(
                                f"pair_{pair_num}"
                            )
                    
                except Exception as e:
                    pass  # Continue to next board
        
        return True
    
    def resolve_conflicts(self):
        """Resolve any conflicting hands using majority vote."""
        print(f"\n{'='*70}")
        print(f"STEP 3: Resolving conflicts via cross-check")
        print(f"{'='*70}\n")
        
        conflicts = 0
        resolved = 0
        
        for board_num in sorted(self.boards_hands.keys()):
            board = self.boards_hands[board_num]
            
            for compass in ['N', 'S', 'E', 'W']:
                raw_hands = board['raw_hands'].get(compass, [])
                
                if not raw_hands:
                    continue
                
                # Group by hand value
                hand_groups = {}
                for entry in raw_hands:
                    hand_key = json.dumps(entry['hand'], sort_keys=True)
                    if hand_key not in hand_groups:
                        hand_groups[hand_key] = []
                    hand_groups[hand_key].append(entry)
                
                if len(hand_groups) == 1:
                    # All sources agree
                    best_hand = raw_hands[0]['hand']
                    resolved += 1
                else:
                    # Conflict detected
                    conflicts += 1
                    # Use most common hand
                    best_hand = max(hand_groups.values(), key=len)[0]['hand']
                    
                    print(f"Board {board_num:2d} {compass}: {len(hand_groups)} variants from {len(raw_hands)} sources")
                
                board['hands'][compass] = best_hand
        
        print(f"\n✓ Resolved: {resolved}")
        print(f"⚠ Conflicts: {conflicts}")
        
        return True
    
    def save_database(self):
        """Save all resolved hands to database."""
        print(f"\n{'='*70}")
        print(f"STEP 4: Saving to hands_database.json")
        print(f"{'='*70}\n")
        
        try:
            with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
                db = json.load(f)
        except:
            db = {'events': {'hosgoru_04_01_2026': {
                'name': 'Hoşgörü Pazar Simultane',
                'date': '04.01.2026',
                'boards': {}
            }}}
        
        # Update boards with fetched hands
        updated_count = 0
        
        for board_num in sorted(self.boards_hands.keys()):
            board_key = str(board_num)
            board_data = self.boards_hands[board_num]
            
            if board_key not in db['events']['hosgoru_04_01_2026']['boards']:
                db['events']['hosgoru_04_01_2026']['boards'][board_key] = {
                    'dealer': 'N',
                    'vulnerability': 'None',
                    'hands': {'North': {}, 'South': {}, 'East': {}, 'West': {}},
                    'dd_analysis': {},
                    'results': [],
                    'fetch_sources': {}
                }
            
            board_obj = db['events']['hosgoru_04_01_2026']['boards'][board_key]
            
            # Update hands
            has_hands = False
            if board_data['hands']['N']:
                board_obj['hands']['North'] = board_data['hands']['N']
                has_hands = True
            if board_data['hands']['S']:
                board_obj['hands']['South'] = board_data['hands']['S']
                has_hands = True
            if board_data['hands']['E']:
                board_obj['hands']['East'] = board_data['hands']['E']
                has_hands = True
            if board_data['hands']['W']:
                board_obj['hands']['West'] = board_data['hands']['W']
                has_hands = True
            
            if has_hands:
                board_obj['fetch_sources'] = {
                    compass: sources for compass, sources in board_data['sources'].items() if sources
                }
                updated_count += 1
        
        # Save database
        with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Updated {updated_count} boards")
        print(f"✓ Saved to app/www/hands_database.json")
        
        # Summary
        boards_complete = sum(1 for b in db['events']['hosgoru_04_01_2026']['boards'].values()
                             if all(b['hands'][p] for p in ['North', 'South', 'East', 'West']))
        total_boards = len(db['events']['hosgoru_04_01_2026']['boards'])
        
        print(f"\n{'='*70}")
        print(f"SUMMARY")
        print(f"{'='*70}")
        print(f"Total boards with hands: {boards_complete}/{total_boards}")
        
        return True
    
    def run(self):
        """Execute complete fetch operation."""
        try:
            self.setup_driver()
            
            if not self.get_pairs():
                return False
            
            if not self.fetch_all_hands():
                return False
            
            if not self.resolve_conflicts():
                return False
            
            if not self.save_database():
                return False
            
            print(f"\n{'='*70}")
            print(f"✓ FETCH COMPLETE")
            print(f"{'='*70}\n")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            if self.driver:
                self.driver.quit()


if __name__ == "__main__":
    fetcher = PlayerBasedHandsFetcher()
    success = fetcher.run()
    sys.exit(0 if success else 1)
