#!/usr/bin/env python3
"""Fetch hands ONLY from events in 2026 onwards (ignore historical data before 2026)"""

import json
import time
from unified_fetch import DataFetcher, EventRegistry

def is_event_from_2026_or_later(date_str):
    """Check if event date is from 2026 or later"""
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

def is_hand_from_2026_or_later(hand):
    """Check if hand is from 2026 or later"""
    return is_event_from_2026_or_later(hand.get('date', ''))

def get_events_to_fetch():
    """Get events from 2026 onwards that need hands fetched"""
    fetcher = DataFetcher()
    registry = EventRegistry()
    
    # Get all events from registry using get_all_events() method
    all_events_dict = registry.get_all_events()  # Returns {date: event_id}
    
    # Filter to only include events from 2026 onwards
    events_2026_plus = [
        int(event_id)
        for date_str, event_id in all_events_dict.items() 
        if str(event_id).isdigit() and is_event_from_2026_or_later(date_str)
    ]
    
    # Build a set of existing (event_id, board) tuples to skip duplicates
    existing_hands = set(
        (h.get('event_id'), h.get('board')) 
        for h in fetcher.hands 
        if h.get('event_id') and h.get('board')
    )
    
    # Get events already in database
    fetched_events = set(str(h.get('event_id')) for h in fetcher.hands)
    
    # Return events not yet fetched, sorted, plus the existing hands set
    unfetched = [e for e in events_2026_plus if str(e) not in fetched_events]
    return sorted(unfetched), fetcher, existing_hands

def main():
    events, fetcher, existing_hands = get_events_to_fetch()
    
    initial_count = len(fetcher.hands)
    print(f"Fetching hands from {len(events)} events in 2026 onwards...")
    print(f"Starting with: {initial_count} hands (will skip duplicates)\n")
    
    total_added = 0
    total_skipped = 0
    total_ignored = 0  # Pre-2026 hands
    
    if len(events) == 0:
        print("✅ All events already fetched! No new data to retrieve.\n")
    
    for idx, event_id in enumerate(events, 1):
        try:
            start = time.time()
            
            # Fetch hands for this event
            hands = fetcher.fetch_hands_for_event(event_id)
            elapsed = time.time() - start
            
            # Process hands: add only new 2026+ hands
            new_count = 0
            skipped_count = 0
            ignored_count = 0
            
            for hand in hands:
                # Filter 1: Only keep hands from 2026 or later
                if not is_hand_from_2026_or_later(hand):
                    ignored_count += 1
                    continue
                
                # Filter 2: Skip if already in database
                event_board = (hand.get('event_id'), hand.get('board'))
                if event_board in existing_hands:
                    skipped_count += 1
                    continue
                
                # Add new hand
                fetcher.hands.append(hand)
                existing_hands.add(event_board)
                new_count += 1
            
            total_added += new_count
            total_skipped += skipped_count
            total_ignored += ignored_count
            
            status = f"✓ fetched {len(hands)} hands"
            details = []
            if new_count > 0:
                details.append(f"+{new_count} new")
            if skipped_count > 0:
                details.append(f"-{skipped_count} skipped")
            if ignored_count > 0:
                details.append(f"-{ignored_count} pre-2026")
            
            if details:
                status += f" ({', '.join(details)})"
            
            print(f"[{idx:3d}/{len(events)}] Event {event_id}: {status} ({elapsed:.1f}s)")
            
            # Save after each event to preserve progress
            with open('hands_database.json', 'w', encoding='utf-8') as f:
                json.dump(fetcher.hands, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[{idx:3d}/{len(events)}] Event {event_id}: ✗ Error: {e}")
            continue
    
    final_count = len(fetcher.hands)
    print(f"\n{'='*60}")
    print(f"✅ Fetch Complete!")
    print(f"Initial hands: {initial_count}")
    print(f"Hands added: {total_added}")
    print(f"Hands skipped (duplicates): {total_skipped}")
    print(f"Hands ignored (pre-2026): {total_ignored}")
    print(f"Final hands: {final_count}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
