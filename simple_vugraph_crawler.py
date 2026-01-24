#!/usr/bin/env python3
"""
Simple Vugraph Crawler - Fetch ALL hands available on vugraph.com
Uses correct N/W/E/S mapping from vugraph HTML structure
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path

BASE_URL = "https://clubs.vugraph.com/hosgoru"
HANDS_FILE = Path("hands_database.json")

def get_dealer(board_num):
    """Get dealer for board number (1-based cycle)"""
    return ['N', 'E', 'S', 'W'][(board_num - 1) % 4]

def get_vulnerability(board_num):
    """Get vulnerability for board number (standard 4-board cycle)"""
    cycle = (board_num - 1) % 16
    if cycle < 4:
        return "None"
    elif cycle < 8:
        return "NS"
    elif cycle < 12:
        return "EW"
    else:
        return "Both"

def fetch_hand(event_id, board_num):
    """Fetch a single hand from vugraph"""
    url = f"{BASE_URL}/event/{event_id}/hands/{board_num}/"
    
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Find player cards containers
        # Vugraph displays cards in: N (top), W (left), E (right), S (bottom)
        # HTML structure has cells in order: 0=N, 1=W, 2=E, 3=S
        
        player_cells = soup.find_all('div', class_=lambda x: x and 'player' in (x or '').lower())
        
        if len(player_cells) < 4:
            print(f"  ⚠️  Board {board_num}: Only {len(player_cells)} players found")
            return None
        
        # Map vugraph HTML positions to compass (correct order discovered: N, W, E, S)
        visual_to_compass = {
            0: 'N',  # Position 0: North (top player)
            1: 'W',  # Position 1: West (left side player)
            2: 'E',  # Position 2: East (right side player)
            3: 'S'   # Position 3: South (bottom player)
        }
        
        hands = {}
        
        for idx, cell in enumerate(player_cells):
            if idx >= 4:
                break
            
            compass_pos = visual_to_compass[idx]
            
            # Find all img tags with suit images
            suit_imgs = cell.find_all('img')
            
            # Extract suits and cards
            suits = [[], [], [], []]  # S, H, D, C
            
            for img in suit_imgs:
                src = img.get('src', '')
                alt = img.get('alt', '')
                
                # Determine suit from image src or alt
                suit_idx = -1
                if 'spade' in src.lower() or '♠' in alt or 'S' in alt:
                    suit_idx = 0
                elif 'heart' in src.lower() or '♥' in alt or 'H' in alt:
                    suit_idx = 1
                elif 'diamond' in src.lower() or '♦' in alt or 'D' in alt:
                    suit_idx = 2
                elif 'club' in src.lower() or '♣' in alt or 'C' in alt:
                    suit_idx = 3
                
                # Extract rank from src or alt
                rank = ''
                if '/a' in src or 'A' in alt:
                    rank = 'A'
                elif '/k' in src or 'K' in alt:
                    rank = 'K'
                elif '/q' in src or 'Q' in alt:
                    rank = 'Q'
                elif '/j' in src or 'J' in alt:
                    rank = 'J'
                elif '/t' in src or 'T' in alt or '10' in alt:
                    rank = 'T'
                elif '/9' in src or '9' in alt:
                    rank = '9'
                elif '/8' in src or '8' in alt:
                    rank = '8'
                elif '/7' in src or '7' in alt:
                    rank = '7'
                elif '/6' in src or '6' in alt:
                    rank = '6'
                elif '/5' in src or '5' in alt:
                    rank = '5'
                elif '/4' in src or '4' in alt:
                    rank = '4'
                elif '/3' in src or '3' in alt:
                    rank = '3'
                elif '/2' in src or '2' in alt:
                    rank = '2'
                
                if suit_idx >= 0 and rank:
                    suits[suit_idx].append(rank)
            
            # Format hand as S.H.D.C
            hand_str = '.'.join(''.join(suits[i]) for i in range(4))
            hands[compass_pos] = hand_str
        
        if len(hands) == 4:
            return hands
        else:
            print(f"  ⚠️  Board {board_num}: Could not extract all 4 hands")
            return None
    
    except Exception as e:
        print(f"  ❌ Board {board_num}: {str(e)}")
        return None

def fetch_event(event_id, date_str):
    """Fetch all hands for an event"""
    print(f"\n📅 Event {event_id} ({date_str})")
    
    hands_list = json.load(open(HANDS_FILE)) if HANDS_FILE.exists() else []
    event_hands = []
    
    # Try to fetch boards 1-30 (standard tournament size)
    for board_num in range(1, 31):
        print(f"  Board {board_num}...", end=' ', flush=True)
        
        hand_data = fetch_hand(event_id, board_num)
        
        if hand_data:
            record = {
                'board': board_num,
                'date': date_str,
                'event_id': event_id,
                'dealer': get_dealer(board_num),
                'vulnerability': get_vulnerability(board_num),
                'N': hand_data.get('N', ''),
                'E': hand_data.get('E', ''),
                'S': hand_data.get('S', ''),
                'W': hand_data.get('W', ''),
                'dd_analysis': {}
            }
            
            event_hands.append(record)
            hands_list.append(record)
            print("✅")
        else:
            print("⏭️")
    
    # Save after each event
    if event_hands:
        with open(HANDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(hands_list, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved {len(event_hands)} hands for event {event_id}")
    
    return len(event_hands)

def main():
    """Main crawler - fetch from all available events"""
    
    # Load event registry to find event IDs
    from event_registry import EventRegistry
    registry = EventRegistry()
    
    print("=" * 60)
    print("🕷️  SIMPLE VUGRAPH CRAWLER")
    print("=" * 60)
    
    # Get all events and try to fetch them
    total_hands = 0
    events_tried = 0
    events_success = 0
    
    # Try dates from 01.01.2026 to 24.01.2026
    current_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 24)
    
    while current_date <= end_date:
        date_str = current_date.strftime('%d.%m.%Y')
        event_id = registry.get_event_id(date_str)
        
        if event_id:
            events_tried += 1
            hands_count = fetch_event(event_id, date_str)
            if hands_count > 0:
                events_success += 1
                total_hands += hands_count
        
        current_date += timedelta(days=1)
    
    print("\n" + "=" * 60)
    print(f"✅ CRAWL COMPLETE")
    print(f"   Events tried: {events_tried}")
    print(f"   Events with hands: {events_success}")
    print(f"   Total hands fetched: {total_hands}")
    print("=" * 60)

if __name__ == '__main__':
    main()
