#!/usr/bin/env python3
"""Quick database verification and status check"""

import json
from collections import Counter

def verify():
    try:
        with open('hands_database.json', 'r', encoding='utf-8') as f:
            hands = json.load(f)
    except Exception as e:
        print(f"Error loading database: {e}")
        return False
    
    print("\n" + "="*70)
    print("DATABASE VERIFICATION REPORT")
    print("="*70)
    
    # Basic counts
    total = len(hands)
    print(f"\nTotal hands: {total}/720 {'✓' if total == 720 else '✗'}")
    
    # Date distribution
    dates = Counter(h.get('date') for h in hands)
    print(f"Unique dates: {len(dates)}/24 {'✓' if len(dates) == 24 else '✗'}")
    
    if len(dates) > 0:
        print(f"\nDate distribution:")
        for date, count in sorted(dates.items()):
            expected = 30
            status = '✓' if count == expected else '✗'
            print(f"  {date}: {count} hands {status}")
    
    # Event distribution
    events = Counter(h.get('event_id') for h in hands)
    print(f"\nEvents: {len(events)} unique")
    for event_id, count in sorted(events.items()):
        print(f"  Event {event_id}: {count} hands")
    
    # Field completeness
    print(f"\nField completeness:")
    has_lin = sum(1 for h in hands if 'lin_string' in h and h['lin_string'])
    has_dd = sum(1 for h in hands if 'dd_result' in h and h['dd_result'])
    has_optimum = sum(1 for h in hands if 'optimum' in h and h['optimum'])
    has_lott = sum(1 for h in hands if 'lott' in h and h['lott'])
    
    print(f"  LIN strings: {has_lin}/{total} {'✓' if has_lin == total else '✗'}")
    print(f"  DD results: {has_dd}/{total} {'✓' if has_dd == total else '✗'}")
    print(f"  Optimum contracts: {has_optimum}/{total} {'✓' if has_optimum == total else '✗'}")
    print(f"  Law of Total Tricks: {has_lott}/{total} {'✓' if has_lott == total else '✗'}")
    
    # Sample verification
    if hands:
        sample = hands[0]
        print(f"\nSample hand (Event {sample.get('event_id')}, Board {sample.get('board')}):")
        print(f"  Date: {sample.get('date')}")
        print(f"  Dealer: {sample.get('dealer')}")
        print(f"  N: {sample.get('N')}")
        print(f"  S: {sample.get('S')}")
        print(f"  E: {sample.get('E')}")
        print(f"  W: {sample.get('W')}")
        if sample.get('lin_string'):
            print(f"  LIN: {sample.get('lin_string')[:50]}...")
        else:
            print(f"  LIN: MISSING")
        optimum = sample.get('optimum', {})
        if isinstance(optimum, dict):
            print(f"  Optimum: {optimum.get('text', 'MISSING')}")
        else:
            print(f"  Optimum: {optimum}")
        lott = sample.get('lott', {})
        if isinstance(lott, dict):
            print(f"  LoTT: {lott.get('total_tricks', 'MISSING')}")
        else:
            print(f"  LoTT: {lott}")
    
    # Overall status
    all_ok = all([
        total == 720,
        len(dates) == 24,
        all(count == 30 for count in dates.values()) if len(dates) > 0 else False,
        has_lin == total,
        has_optimum == total,
        has_lott == total
    ])
    
    print("\n" + "="*70)
    if all_ok:
        print("STATUS: VERIFICATION PASSED ✓")
    elif has_dd == total:
        print("STATUS: ALL FIELDS COMPLETE ✓")
    elif has_dd > 0:
        print(f"STATUS: PROCESSING... ({has_dd}/{total} DD results) - {has_dd*100//total}% complete")
    else:
        print("STATUS: PENDING...")
    print("="*70 + "\n")
    
    return all_ok

if __name__ == '__main__':
    verify()
