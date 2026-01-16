#!/usr/bin/env python3
"""
Fetch hands by inspecting board details page structure.
Strategy: Navigate to each board details page and extract hands using Selenium.
"""

import json
import time
import sys
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

EVENT_ID = 404377

class VugraphHandsFetcher:
    def __init__(self):
        self.boards_data = {}
        self.driver = None
    
    def setup_driver(self):
        """Initialize Selenium Chrome driver."""
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=options
        )
    
    def fetch_board_hands(self, board_num):
        """Fetch hands for a specific board from board details page."""
        try:
            # Construct board details URL
            url = f"https://clubs.vugraph.com/hosgoru/boarddetails.php?event={EVENT_ID}&board={board_num}"
            
            print(f"Board {board_num}: Opening {url[:60]}...")
            self.driver.get(url)
            time.sleep(2)
            
            hands = {'N': {}, 'S': {}, 'E': {}, 'W': {}}
            
            # Get page source and text
            page_html = self.driver.page_source
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Look for dealer information
            try:
                dealer_elem = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Dealer')]")
                dealer_text = dealer_elem.text
                print(f"  Found dealer info: {dealer_text}")
            except:
                print(f"  No dealer info found")
            
            # Method 1: Look for specific hand display format
            # On Vugraph, hands are often shown as:
            # North: S...  H... D... C...
            # South: S...  H... D... C...
            # etc.
            
            # Try to find all text nodes containing suit symbols
            lines = page_text.split('\n')
            
            current_player = None
            for line in lines:
                line = line.strip()
                
                # Look for player headers
                if line.startswith('North') or line == 'North':
                    current_player = 'N'
                    print(f"  Found North section")
                elif line.startswith('South') or line == 'South':
                    current_player = 'S'
                    print(f"  Found South section")
                elif line.startswith('East') or line == 'East':
                    current_player = 'E'
                    print(f"  Found East section")
                elif line.startswith('West') or line == 'West':
                    current_player = 'W'
                    print(f"  Found West section")
                
                # Look for hand data lines (contain S:, H:, D:, C: or suit symbols)
                if current_player and any(s in line for s in ['S:', 'H:', 'D:', 'C:']):
                    # Parse hand from this line
                    # Format: "S:AKJ  H:Q92  D:T8643  C:K7"
                    hands[current_player] = self._parse_hand_line(line)
                    print(f"    {current_player}: {line[:40]}...")
                    current_player = None  # Reset for next player
            
            # If no hands found, try alternative parsing
            if not any(hands.values()):
                print(f"  Trying alternative hand extraction...")
                hands = self._extract_from_html(self.driver)
            
            return hands
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return {'N': {}, 'S': {}, 'E': {}, 'W': {}}
    
    def _parse_hand_line(self, line):
        """Parse hand from a line like 'S:AK  H:Q92  D:T8643  C:K7'"""
        hand = {'S': '', 'H': '', 'D': '', 'C': ''}
        
        # Split by suit indicators
        import re
        
        # Pattern: S:cards H:cards D:cards C:cards
        pattern = r'([SHDC]):([A2-9TJKQa2-9tjkq]+)'
        matches = re.findall(pattern, line, re.IGNORECASE)
        
        for suit, cards in matches:
            suit = suit.upper()
            hand[suit] = cards.upper()
        
        return hand
    
    def _extract_from_html(self, driver):
        """Extract hands from HTML structure."""
        hands = {'N': {}, 'S': {}, 'E': {}, 'W': {}}
        
        try:
            # Look for elements containing hand data
            # Try to find divs or tables with hand information
            elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'S:') or contains(text(), '♠')]")
            
            print(f"    Found {len(elements)} potential hand elements")
            
            for elem in elements:
                text = elem.text.strip()
                if text and any(s in text for s in ['S:', 'H:', 'D:', 'C:']):
                    print(f"    Hand data: {text[:60]}...")
            
        except Exception as e:
            print(f"    Could not extract from HTML: {e}")
        
        return hands
    
    def fetch_all_boards(self, num_boards=30):
        """Fetch hands for all 30 boards."""
        print(f"\n{'='*70}")
        print(f"FETCHING HANDS FOR {num_boards} BOARDS")
        print(f"{'='*70}\n")
        
        for board_num in range(1, num_boards + 1):
            hands = self.fetch_board_hands(board_num)
            self.boards_data[board_num] = hands
        
        return True
    
    def save_results(self):
        """Save to database."""
        print(f"\n{'='*70}")
        print(f"SAVING RESULTS")
        print(f"{'='*70}\n")
        
        try:
            with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
                db = json.load(f)
        except:
            db = {'events': {'hosgoru_04_01_2026': {
                'name': 'Hoşgörü Pazar Simultane',
                'boards': {}
            }}}
        
        # Update with fetched hands
        for board_num, hands in self.boards_data.items():
            board_key = str(board_num)
            if board_key not in db['events']['hosgoru_04_01_2026']['boards']:
                db['events']['hosgoru_04_01_2026']['boards'][board_key] = {
                    'dealer': 'N',
                    'vulnerability': 'None',
                    'hands': {'North': {}, 'South': {}, 'East': {}, 'West': {}},
                    'dd_analysis': {},
                    'results': []
                }
            
            # Map compass to player names
            db['events']['hosgoru_04_01_2026']['boards'][board_key]['hands']['North'] = hands.get('N', {})
            db['events']['hosgoru_04_01_2026']['boards'][board_key]['hands']['South'] = hands.get('S', {})
            db['events']['hosgoru_04_01_2026']['boards'][board_key]['hands']['East'] = hands.get('E', {})
            db['events']['hosgoru_04_01_2026']['boards'][board_key]['hands']['West'] = hands.get('W', {})
        
        with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved to app/www/hands_database.json")
    
    def run(self):
        """Execute complete fetch."""
        try:
            self.setup_driver()
            self.fetch_all_boards(30)
            self.save_results()
            return True
        except Exception as e:
            print(f"\n✗ Error: {e}")
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
