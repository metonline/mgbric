#!/usr/bin/env python3
"""Fetch all hands from January 2026 events using the existing unified_fetch infrastructure"""

import json
import time
from unified_fetch import DataFetcher

# All 23 January 2026 events
EVENTS = [
    404155, 404197, 404275, 404377, 404426, 404498, 404562, 404628,
    404691, 404854, 404821, 404876, 405128, 405007, 405061, 405123,
    405204, 405278, 405315, 405376, 405445, 405535, 405596,
]

def main():
    fetcher = DataFetcher()
    
    initial_count = len(fetcher.hands)
    print(f"Fetching hands from {len(EVENTS)} January 2026 events...")
    print(f"Starting with: {initial_count} hands\n")
    
    total_added = 0
    
    for idx, event_id in enumerate(EVENTS, 1):
        try:
            start = time.time()
            
            # Fetch hands for this event
            hands = fetcher.fetch_hands_for_event(event_id)
            elapsed = time.time() - start
            
            # Count how many are actually new
            new_count = 0
            for hand in hands:
                # Check if already exists
                existing = any(
                    h.get('event_id') == hand.get('event_id') and h.get('board') == hand.get('board')
                    for h in fetcher.hands
                )
                if not existing:
                    fetcher.hands.append(hand)
                    new_count += 1
            
            total_added += new_count
            
            status = f"✓ {len(hands)} hands, +{new_count} new"
            print(f"[{idx:2d}/{len(EVENTS)}] Event {event_id}: {status} ({elapsed:.1f}s)")
            
            # Save after each event to preserve progress
            with open('hands_database.json', 'w', encoding='utf-8') as f:
                json.dump(fetcher.hands, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[{idx:2d}/{len(EVENTS)}] Event {event_id}: ✗ Error: {e}")
            continue
    
    final_count = len(fetcher.hands)
    print(f"\n{'='*60}")
    print(f"Complete!")
    print(f"Initial hands: {initial_count}")
    print(f"Total added: {total_added}")
    print(f"Final hands: {final_count}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
