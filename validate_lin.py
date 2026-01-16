#!/usr/bin/env python3
"""
Verify and validate the LIN file format
Check if all hands are complete (13 cards each) and properly formatted
"""

import re

def validate_hand(hand_str):
    """Validate a single hand has 13 cards"""
    suits = hand_str.split('.')
    if len(suits) != 4:
        return False, f"Missing suits (got {len(suits)}, need 4)"
    
    total_cards = 0
    for suit in suits:
        total_cards += len(suit)
    
    if total_cards != 13:
        return False, f"Wrong number of cards ({total_cards}, need 13)"
    
    return True, "OK"

# Read and validate LIN file
with open('hosgoru_boards.lin', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all Deal lines
deal_pattern = r'\[Deal "([^"]+)"\]'
deals = re.findall(deal_pattern, content)

print("=" * 80)
print("LIN FILE VALIDATION")
print("=" * 80)
print(f"\nFound {len(deals)} deals\n")

issues = []

for i, deal in enumerate(deals, 1):
    parts = deal.split()
    
    print(f"Board {i}:")
    
    # Expected format: N:S.H.D.C E:S.H.D.C S:S.H.D.C W:S.H.D.C
    # or: N:S.H.D.C hand2 hand3 hand4
    
    if len(parts) < 4:
        print(f"  ❌ ERROR: Only {len(parts)} parts (need 4)")
        issues.append(f"Board {i}: Only {len(parts)} parts")
        continue
    
    # Check format of each part
    for pos_idx, (part, expected_pos) in enumerate(zip(parts, ['N', 'E', 'S', 'W'])):
        if ':' in part:
            # Labeled format: E:S.H.D.C
            label, hand = part.split(':')
            valid, msg = validate_hand(hand)
            if not valid:
                print(f"  ❌ {label} hand: {msg}")
                issues.append(f"Board {i} {label}: {msg}")
            else:
                print(f"  ✓ {label}: {hand}")
        else:
            # Unlabeled format - assume order
            valid, msg = validate_hand(part)
            if not valid:
                print(f"  ❌ {expected_pos} hand: {msg}")
                issues.append(f"Board {i} {expected_pos}: {msg}")
            else:
                print(f"  ✓ {expected_pos}: {part}")

print("\n" + "=" * 80)
if issues:
    print(f"❌ FOUND {len(issues)} ISSUES:\n")
    for issue in issues:
        print(f"  {issue}")
    print("\nThe LIN file has errors and may not load properly.")
else:
    print("✓ All hands validated successfully!")
    print("\nIf the solver still doesn't work, try:")
    print("1. Manually entering one board at a time")
    print("2. Using a different solver format (PBN instead of LIN)")
    print("3. Checking if the solver has specific format requirements")
