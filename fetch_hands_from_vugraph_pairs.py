import json
import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict
import time

# All 52 cards in each suit
ALL_CARDS = 'AKQJT98765432'

def calculate_remaining_hand(hand1, hand2, hand3):
    """Calculate 4th hand from remaining cards"""
    suits1 = hand1.split('.')
    suits2 = hand2.split('.')
    suits3 = hand3.split('.')
    
    remaining_suits = []
    for suit_idx in range(4):
        used_cards = suits1[suit_idx] + suits2[suit_idx] + suits3[suit_idx]
        remaining = ''.join(c for c in ALL_CARDS if c not in used_cards)
        remaining_suits.append(remaining)
    
    return '.'.join(remaining_suits)

def rotate_hands_by_dealer(hand_in_dealer_order, dealer):
    """Rotate hands from dealer-relative order to N-E-S-W order"""
    hands_from_dealer = {
        'N': {'N': 0, 'E': 1, 'S': 2},
        'E': {'E': 0, 'S': 1, 'W': 2},
        'S': {'S': 0, 'W': 1, 'N': 2},
        'W': {'W': 0, 'N': 1, 'E': 2},
    }
    
    mapping = hands_from_dealer[dealer]
    result = {}
    
    for direction, index in mapping.items():
        result[direction] = hand_in_dealer_order[index]
    
    return result

def extract_board_hands_from_page(html):
    """Extract board hand data from vugraph board detail page"""
    soup = BeautifulSoup(html, 'html.parser')
    boards = defaultdict(dict)
    
    # Look for board data in page
    # Vugraph typically shows: Board X, Dealer N, N: ..., E: ..., S: ..., W: ...
    
    # Try to find board number and hands
    board_pattern = r'Board\s+(\d+)'
    hand_pattern = r'[NEWS]:\s*([A-Z2-9\.]+)'
    
    text = soup.get_text()
    
    # Try to extract from tables or divs containing hand data
    tables = soup.find_all('table')
    for table in tables:
        table_text = table.get_text()
        if 'Board' in table_text:
            # This might contain board data
            pass
    
    return boards

def fetch_board_details_from_tournament(tournament_link):
    """Fetch board details from a vugraph tournament link"""
    try:
        print(f"Fetching: {tournament_link}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(tournament_link, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"  ✗ Failed: {response.status_code}")
            return {}
        
        # Extract board data from HTML
        boards = extract_board_hands_from_page(response.text)
        print(f"  ✓ Found {len(boards)} boards")
        return boards
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:60]}")
        return {}

def aggregate_hands_from_vugraph():
    """
    Aggregate hand data from vugraph tournament pages
    Each pair result has a link to a tournament, fetch boards from multiple tournaments
    to accumulate complete hand set
    """
    # Load vugraph data
    with open('database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find Event 405376 records and get unique tournament links
    event_records = [r for r in data.get('legacy_records', []) if 'Event 405376' in r.get('Turnuva', '')]
    
    print(f"Found {len(event_records)} records for Event 405376")
    
    # Get unique links
    unique_links = set()
    for record in event_records:
        if 'Link' in record:
            unique_links.add(record['Link'])
    
    print(f"Found {len(unique_links)} unique tournament links\n")
    
    # Aggregate boards from each link
    aggregated_boards = defaultdict(dict)
    
    for link in list(unique_links)[:5]:  # Start with first 5 links to test
        boards = fetch_board_details_from_tournament(link)
        for board_num, board_data in boards.items():
            if board_num not in aggregated_boards:
                aggregated_boards[board_num] = board_data
        time.sleep(2)  # Be respectful to server
    
    return aggregated_boards

# For now, show that we have the infrastructure
print("Vugraph Board Data Aggregator")
print("="*50)
print("\nThis script will:")
print("1. Read vugraph database records for Event 405376")
print("2. Extract unique tournament links")
print("3. Fetch board details from each tournament page")
print("4. Aggregate hands across all boards")
print("5. Build complete hands_database.json from vugraph data")
print("\nNote: Requires BeautifulSoup4 and Requests libraries")
print("And careful HTML parsing as vugraph structure varies\n")

try:
    with open('database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    event_records = [r for r in data.get('legacy_records', []) if 'Event 405376' in r.get('Turnuva', '')]
    
    print(f"✓ Found {len(event_records)} records for Event 405376")
    
    unique_links = set()
    for record in event_records:
        if 'Link' in record:
            unique_links.add(record['Link'])
    
    print(f"✓ Found {len(unique_links)} unique tournament links")
    print("\nSample links:")
    for link in list(unique_links)[:3]:
        print(f"  - {link}")
        
except Exception as e:
    print(f"Error: {e}")
