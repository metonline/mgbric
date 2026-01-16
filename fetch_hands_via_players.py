#!/usr/bin/env python3
"""
Fetch hands from Vugraph by going through players' list.

Strategy:
1. Get event overview page to extract players/pairs
2. For each player, fetch their pair summary page (with sections)
3. From pair summary, extract all boards they played
4. For each board, fetch detailed game info to extract hands
5. Cross-reference across players to build complete hands_database
6. Use board details for sorting/extra data validation
"""

import json
import time
import sys
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configuration
EVENT_ID = 404377
SECTION = "A"
BASE_URL = "https://clubs.vugraph.com/hosgoru/"

# Card parsing
SUITS = ['S', 'H', 'D', 'C']
SUIT_SYMBOLS = {'♠': 'S', '♥': 'H', '♦': 'D', '♣': 'C'}
RANK_ORDER = {'A': '14', 'K': '13', 'Q': '12', 'J': '11', 'T': '10', '9': '9', '8': '8', '7': '7', '6': '6', '5': '5', '4': '4', '3': '3', '2': '2'}

class VugraphHandsFetcher:
    def __init__(self):
        self.event_id = EVENT_ID
        self.section = SECTION
        self.boards_data = defaultdict(lambda: {
            'dealer': None,
            'vulnerability': None,
            'hands': {'North': {}, 'South': {}, 'East': {}, 'West': {}},
            'hands_sources': defaultdict(list),  # Track where each player's hand came from
            'cross_check': {}  # Store cross-reference validation
        })
        self.driver = None
        self.pairs_list = []
        
    def setup_driver(self):
        """Initialize Selenium Chrome driver."""
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        # options.add_argument("--headless")  # Remove for debugging
        
        self.driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=options
        )
    
    def get_pairs_list(self):
        """Fetch the list of all pairs/players in the event."""
        print(f"\n{'='*70}")
        print(f"STEP 1: Fetching pairs/players list for Event {self.event_id}")
        print(f"{'='*70}\n")
        
        event_url = f"{BASE_URL}eventresults.php?event={self.event_id}"
        print(f"Opening: {event_url}")
        self.driver.get(event_url)
        
        time.sleep(3)
        
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
            
            # Find all links to pair summary pages
            # Format: pairsummary.php?event=404377&section=A&pair=1&direction=NS
            links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'pairsummary.php')]")
            
            unique_pairs = {}
            for link in links:
                href = link.get_attribute("href")
                text = link.text.strip()
                
                if "event=" in href and "pair=" in href:
                    pair_num = href.split("pair=")[1].split("&")[0]
                    direction = "NS" if "direction=NS" in href else "EW"
                    
                    # Store only once per pair (we'll fetch both sections from pair page)
                    pair_key = f"{pair_num}_{direction}"
                    if pair_key not in unique_pairs:
                        unique_pairs[pair_key] = {
                            'url': href,
                            'pair_num': pair_num,
                            'direction': direction,
                            'names': text
                        }
            
            self.pairs_list = list(unique_pairs.values())
            
            print(f"✓ Found {len(self.pairs_list)} unique pairs")
            for i, p in enumerate(self.pairs_list[:5]):
                print(f"  {i+1}. Pair {p['pair_num']} ({p['direction']}): {p['names']}")
            if len(self.pairs_list) > 5:
                print(f"  ... and {len(self.pairs_list)-5} more")
            
            return True
            
        except Exception as e:
            print(f"✗ Error fetching pairs: {e}")
            return False
    
    def fetch_pair_boards(self, pair_url, pair_num, direction):
        """Fetch all boards for a specific pair."""
        try:
            print(f"\n  Fetching boards for Pair {pair_num} ({direction})...")
            self.driver.get(pair_url)
            time.sleep(2)
            
            boards = []
            
            # Find all board links on pair summary page
            # Format: boarddetails.php?event=404377&board=1&pair=1&direction=NS
            links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'boarddetails.php')]")
            
            for link in links:
                href = link.get_attribute("href")
                text = link.text.strip()
                
                if "board=" in href:
                    board_num = href.split("board=")[1].split("&")[0]
                    boards.append({
                        'board_num': int(board_num),
                        'url': href,
                        'pair_num': pair_num,
                        'direction': direction
                    })
            
            boards.sort(key=lambda x: x['board_num'])
            print(f"    ✓ Found {len(boards)} boards for this pair")
            return boards
            
        except Exception as e:
            print(f"    ✗ Error fetching boards for pair: {e}")
            return []
    
    def extract_hands_from_board_page(self, board_url, board_num, pair_num, direction):
        """Extract hand information from board details page."""
        try:
            self.driver.get(board_url)
            time.sleep(1.5)
            
            hands = {'N': None, 'S': None, 'E': None, 'W': None}
            
            # Try to find hand display in various formats
            # Looking for patterns like "S:..  H:... D:... C:..."
            
            # Method 1: Look for text nodes with card information
            try:
                # Find dealer info if available
                dealer_text = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Dealer')]").text
                print(f"      Found dealer text: {dealer_text}")
            except:
                pass
            
            # Method 2: Look for hand displays in table cells
            cells = self.driver.find_elements(By.TAG_NAME, "td")
            hand_content = {}
            
            for cell in cells:
                text = cell.text.strip()
                # Look for suit patterns (S: or ♠)
                if any(suit in text for suit in ['S:', 'H:', 'D:', 'C:', '♠', '♥', '♦', '♣']):
                    hand_content[text[:20]] = text  # Store sample
            
            # Method 3: Look for script tags that might contain hand data in JSON
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            for script in scripts:
                script_text = script.get_attribute("innerHTML")
                if "deal" in script_text.lower() or "hand" in script_text.lower():
                    # Look for patterns like: deal: "SAKJT93..." or similar
                    if "SAKJT93" in script_text or script_text.count('"S') > 0:
                        print(f"      Found potential hand data in script")
                        # Try to extract from script
                        hands = self._parse_hands_from_script(script_text)
                        if hands['N']:
                            return hands
            
            return hands
            
        except Exception as e:
            print(f"      ✗ Error extracting hands: {e}")
            return {'N': None, 'S': None, 'E': None, 'W': None}
    
    def _parse_hands_from_script(self, script_text):
        """Parse hand data from JavaScript."""
        hands = {'N': None, 'S': None, 'E': None, 'W': None}
        
        # Look for patterns like: SAKJT93HQ... or similar
        # This is tricky - looking for 13-card sequences
        import re
        
        # Pattern for hand data: uppercase letters and numbers for cards
        pattern = r'[SAKQJT2-9]{13,}'
        matches = re.findall(pattern, script_text)
        
        if len(matches) >= 4:
            hands['W'] = matches[0] if len(matches) > 0 else None
            hands['N'] = matches[1] if len(matches) > 1 else None
            hands['E'] = matches[2] if len(matches) > 2 else None
            hands['S'] = matches[3] if len(matches) > 3 else None
        
        return hands
    
    def fetch_all_hands(self):
        """Main orchestration: fetch hands from all pairs' boards."""
        print(f"\n{'='*70}")
        print(f"STEP 2: Fetching hands from players' boards")
        print(f"{'='*70}\n")
        
        total_pairs = len(self.pairs_list)
        
        for pair_idx, pair_info in enumerate(self.pairs_list):
            pair_num = pair_info['pair_num']
            direction = pair_info['direction']
            
            print(f"\n[{pair_idx+1}/{total_pairs}] Processing Pair {pair_num} ({direction})...")
            
            # Get all boards for this pair
            boards = self.fetch_pair_boards(pair_info['url'], pair_num, direction)
            
            if not boards:
                continue
            
            # For each board, extract hands
            for board_info in boards:
                board_num = board_info['board_num']
                
                hands = self.extract_hands_from_board_page(
                    board_info['url'], 
                    board_num, 
                    pair_num, 
                    direction
                )
                
                # Store this data
                if hands['N']:
                    # Map pair direction to compass positions
                    if direction == 'NS':
                        self.boards_data[board_num]['hands_sources']['N'].append({
                            'pair': pair_num,
                            'direction': direction,
                            'hand': hands['N']
                        })
                        self.boards_data[board_num]['hands_sources']['S'].append({
                            'pair': pair_num,
                            'direction': direction,
                            'hand': hands['S']
                        })
                    else:  # EW
                        self.boards_data[board_num]['hands_sources']['E'].append({
                            'pair': pair_num,
                            'direction': direction,
                            'hand': hands['E']
                        })
                        self.boards_data[board_num]['hands_sources']['W'].append({
                            'pair': pair_num,
                            'direction': direction,
                            'hand': hands['W']
                        })
        
        return True
    
    def resolve_hands(self):
        """Cross-check and resolve hands from multiple sources."""
        print(f"\n{'='*70}")
        print(f"STEP 3: Cross-checking and resolving hands")
        print(f"{'='*70}\n")
        
        resolved_count = 0
        
        for board_num in sorted(self.boards_data.keys()):
            board = self.boards_data[board_num]
            
            # For each compass position, resolve from collected sources
            for compass in ['N', 'S', 'E', 'W']:
                sources = board['hands_sources'].get(compass, [])
                
                if sources:
                    # If multiple sources, they should all agree (cross-check)
                    hands_set = set(s['hand'] for s in sources)
                    
                    if len(hands_set) == 1:
                        # All sources agree
                        hand_str = sources[0]['hand']
                        board['hands'][compass] = self._format_hand(hand_str)
                        board['cross_check'][compass] = f"✓ {len(sources)} source(s) agree"
                        resolved_count += 1
                    else:
                        # Multiple conflicting hands
                        print(f"\n⚠ Board {board_num} {compass}: {len(hands_set)} conflicting hands found:")
                        for i, h in enumerate(hands_set, 1):
                            matching_sources = [s for s in sources if s['hand'] == h]
                            print(f"    {i}. {h[:20]}... ({len(matching_sources)} source(s))")
                        
                        # Use most common one
                        from collections import Counter
                        hand_counts = Counter(s['hand'] for s in sources)
                        most_common = hand_counts.most_common(1)[0][0]
                        board['hands'][compass] = self._format_hand(most_common)
                        board['cross_check'][compass] = f"⚠ Resolved from {len(sources)} sources (conflicts)"
        
        print(f"\n✓ Resolved {resolved_count} compass positions from player data")
        return True
    
    def _format_hand(self, hand_str):
        """Format hand string into dictionary with suits."""
        """
        Format: 'SAKJT93HQD854CT' -> {'S': 'AKJT93', 'H': 'Q', 'D': '854', 'C': 'T'}
        """
        suits = {'S': '', 'H': '', 'D': '', 'C': ''}
        current_suit = None
        
        for char in hand_str:
            if char in suits:
                current_suit = char
            elif current_suit:
                suits[current_suit] += char
        
        return suits
    
    def save_results(self):
        """Save resolved hands to database."""
        print(f"\n{'='*70}")
        print(f"STEP 4: Saving results")
        print(f"{'='*70}\n")
        
        # Load existing database
        try:
            with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
                db = json.load(f)
        except:
            db = {'events': {'hosgoru_04_01_2026': {'name': 'Hoşgörü Pazar Simultane', 'boards': {}}}}
        
        # Update with resolved hands
        for board_num in sorted(self.boards_data.keys()):
            board_key = str(board_num)
            board_data = self.boards_data[board_num]
            
            if board_key not in db['events']['hosgoru_04_01_2026']['boards']:
                db['events']['hosgoru_04_01_2026']['boards'][board_key] = {
                    'dealer': 'N',
                    'vulnerability': 'None',
                    'hands': {'North': {}, 'South': {}, 'East': {}, 'West': {}},
                    'dd_analysis': {},
                    'results': [],
                    'sources': {}
                }
            
            board_obj = db['events']['hosgoru_04_01_2026']['boards'][board_key]
            
            # Update hands with resolved data
            if any(board_data['hands'].values()):
                board_obj['hands']['North'] = board_data['hands'].get('N', {})
                board_obj['hands']['South'] = board_data['hands'].get('S', {})
                board_obj['hands']['East'] = board_data['hands'].get('E', {})
                board_obj['hands']['West'] = board_data['hands'].get('W', {})
                board_obj['sources'] = dict(board_data['cross_check'])
        
        # Save to file
        with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved to app/www/hands_database.json")
        
        # Print summary
        boards_with_hands = sum(1 for b in self.boards_data.values() 
                               if any(b['hands'].values()))
        print(f"\n✓ Boards with hands: {boards_with_hands}/{len(self.boards_data)}")
    
    def run(self):
        """Execute complete fetch operation."""
        try:
            self.setup_driver()
            
            if not self.get_pairs_list():
                return False
            
            if not self.fetch_all_hands():
                return False
            
            if not self.resolve_hands():
                return False
            
            self.save_results()
            
            print(f"\n{'='*70}")
            print(f"FETCH COMPLETE")
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
    fetcher = VugraphHandsFetcher()
    success = fetcher.run()
    sys.exit(0 if success else 1)
