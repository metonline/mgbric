#!/usr/bin/env python3
"""Fetch hands from all available events (since 2020), keep only 2026+ hands"""

import json
import time
from unified_fetch import DataFetcher, EventRegistry

def is_hand_from_2026_or_later(hand):
    """Check if hand is from 2026 or later"""
    date_str = hand.get('date', '')
    if not date_str or date_str == 'unknown':
        return False
    try:
        # Parse date format: "23.01.2026" or similar
        parts = date_str.split('.')
        if len(parts) == 3:
            year = int(parts[2])
            return year >= 2026
    except:
        return False
    return False

def get_events_to_fetch():
    """Get all events from registry that need hands fetched (events since 2020)"""
    fetcher = DataFetcher()
    registry = EventRegistry()
    
    # Get all events from registry using get_all_events() method
    all_events_dict = registry.get_all_events()  # Returns {date: event_id}
    all_event_ids = [int(e) for e in all_events_dict.values() if str(e).isdigit()]
    
    # Get events already in database
    fetched_events = set(str(h.get('event_id')) for h in fetcher.hands)
    
    # Return events not yet fetched, sorted
    unfetched = [e for e in all_event_ids if str(e) not in fetched_events]
    return sorted(unfetched), fetcher

def main():
    events, fetcher = get_events_to_fetch()
    
    initial_count = len(fetcher.hands)
    print(f"Fetching hands from {len(events)} available events...")
    print(f"Starting with: {initial_count} hands\n")
    
    total_added = 0
    
    for idx, event_id in enumerate(events, 1):
        try:
            start = time.time()
            
            # Fetch hands for this event
            hands = fetcher.fetch_hands_for_event(event_id)
            elapsed = time.time() - start
            
            # Count how many are actually new (only keep 2026+ hands)
            new_count = 0
            for hand in hands:
                # Only keep hands from 2026 or later
                if not is_hand_from_2026_or_later(hand):
                    continue
                    
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
            print(f"[{idx:3d}/{len(events)}] Event {event_id}: {status} ({elapsed:.1f}s)")
            
            # Save after each event to preserve progress
            with open('hands_database.json', 'w', encoding='utf-8') as f:
                json.dump(fetcher.hands, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[{idx:3d}/{len(events)}] Event {event_id}: ✗ Error: {e}")
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
