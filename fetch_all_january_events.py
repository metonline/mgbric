#!/usr/bin/env python3
"""Fetch all hands from all available events in the registry"""

import json
import time
from unified_fetch import DataFetcher, EventRegistry

def get_events_to_fetch():
    """Get all events from registry that need hands fetched"""
    fetcher = DataFetcher()
    registry = EventRegistry()
    
    # Get all event IDs from registry
    all_events = []
    if hasattr(registry, 'events'):
        all_events = [int(e) for e in registry.events.keys() if str(e).isdigit()]
    
    # Get events already in database
    fetched_events = set(str(h.get('event_id')) for h in fetcher.hands)
    
    # Return events not yet fetched, sorted
    unfetched = [e for e in all_events if str(e) not in fetched_events]
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
