#!/usr/bin/env python3
"""
Fully automated pipeline for continuous hand data collection and analysis.
Workflow: Fetch → Generate LIN → Calculate DD Analysis

Handles all events in the registry, not just a fixed date range.
Can be run repeatedly to add new events as they become available.
"""

import json
import subprocess
import sys
from pathlib import Path
from unified_fetch import DataFetcher, EventRegistry

def get_available_events():
    """Get all events from registry that we should fetch"""
    registry = EventRegistry()
    
    # Get all event IDs from registry
    all_events = []
    if hasattr(registry, 'events'):
        all_events = list(registry.events.keys())
    
    return sorted([int(e) for e in all_events if e.isdigit()])

def get_unfetched_events(fetched_event_ids):
    """Get events that haven't been fetched yet"""
    all_events = get_available_events()
    return [e for e in all_events if e not in fetched_event_ids]

def run_step(description, script_path, args=None):
    """Run a pipeline step"""
    print(f"\n{'='*70}")
    print(f"📍 {description}")
    print(f"{'='*70}\n")
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    result = subprocess.run(cmd, cwd=Path.cwd())
    
    if result.returncode != 0:
        print(f"\n❌ Error in {description}")
        return False
    
    return True

def main():
    print("\n" + "="*70)
    print("🔄 Bridge Hands Automated Pipeline (Full Workflow)")
    print("="*70)
    print("Workflow: Fetch Hands → Generate LIN → Calculate DD Analysis")
    print("="*70)
    
    # Load current database
    hands = json.load(open('hands_database.json')) if Path('hands_database.json').exists() else []
    
    # Get events already in database
    fetched_events = set(str(h.get('event_id')) for h in hands)
    print(f"\n📊 Current database: {len(hands)} hands from {len(fetched_events)} events")
    
    # Get all available events
    all_events = get_available_events()
    unfetched = get_unfetched_events([int(e) for e in fetched_events])
    
    print(f"📅 Total available events: {len(all_events)}")
    print(f"🆕 New events to fetch: {len(unfetched)}")
    
    if unfetched:
        print(f"   Events: {unfetched[:10]}{'...' if len(unfetched) > 10 else ''}")
    
    # Pipeline steps
    steps = [
        ("Step 1: Fetch hands from all available events", "fetch_all_january_events.py"),
        ("Step 2: Generate LIN strings for all hands", "generate_all_lin.py"),
        ("Step 3: Calculate DD (Double Dummy) analysis", "double_dummy/dd_solver.py", ["--update-db"]),
    ]
    
    for i, (description, script, *args_list) in enumerate(steps, 1):
        args = args_list[0] if args_list else None
        if not run_step(description, script, args):
            print(f"\n⚠️ Pipeline stopped at step {i}")
            return False
    
    # Final summary
    hands = json.load(open('hands_database.json'))
    events = len(set(str(h.get('event_id')) for h in hands))
    
    print(f"\n{'='*70}")
    print(f"✅ Pipeline Complete!")
    print(f"{'='*70}")
    print(f"Total hands: {len(hands)}")
    print(f"Total events: {events}")
    print(f"Each hand has:")
    print(f"  • N/E/S/W hand distributions")
    print(f"  • LIN string format")
    print(f"  • DD optimal contract")
    print(f"  • DD optimal tricks (optimum)")
    print(f"  • Law of Total Tricks (LoTT)")
    print(f"{'='*70}\n")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
