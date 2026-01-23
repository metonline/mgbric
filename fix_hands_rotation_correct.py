#!/usr/bin/env python3
"""
Fix hand rotation using the correct BBO LIN dealer rotation
Applies rotate_hands_by_dealer to all 660 hands
"""
import json

def rotate_hands_by_dealer(hands_dict, dealer):
    """
    Rotate hands based on dealer position.
    hands_dict: {N, E, S, W}
    dealer: 'N', 'E', 'S', or 'W'
    Returns rotated hands dict with correct positions
    """
    rotations = {
        'N': {'N': 'N', 'E': 'E', 'S': 'S', 'W': 'W'},  # No rotation
        'E': {'N': 'W', 'E': 'N', 'S': 'E', 'W': 'S'},  # Rotate 1
        'S': {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'},  # Rotate 2
        'W': {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'},  # Rotate 3
    }
    
    rotation_map = rotations[dealer]
    rotated = {}
    for key, value in rotation_map.items():
        rotated[key] = hands_dict[value]
    
    return rotated

# Load existing hands
with open('hands_database.json', 'r', encoding='utf-8') as f:
    hands = json.load(f)

print(f"Processing {len(hands)} hands...")

# Fix rotation for each hand
fixed_count = 0
for i, hand in enumerate(hands):
    if i % 50 == 0:
        print(f"  Fixed {i}/{len(hands)}...")
    
    dealer = hand.get('dealer', 'N')
    
    # Get current hands
    current = {
        'N': hand.get('N'),
        'E': hand.get('E'),
        'S': hand.get('S'),
        'W': hand.get('W'),
    }
    
    # Rotate to correct positions
    rotated = rotate_hands_by_dealer(current, dealer)
    
    # Update hands
    hand['N'] = rotated['N']
    hand['E'] = rotated['E']
    hand['S'] = rotated['S']
    hand['W'] = rotated['W']
    
    fixed_count += 1

print(f"✓ Fixed {fixed_count} hands")

# Save corrected hands
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(hands, f, ensure_ascii=False, indent=2)

print("✓ Saved hands_database.json")

# Verify one hand
h = hands[0]
print()
print("Sample hand verification:")
print(f"  Board {h['board']}, Date {h['date']}, Dealer {h['dealer']}")
print(f"  N: {h['N']}")
print(f"  E: {h['E']}")
print(f"  S: {h['S']}")
print(f"  W: {h['W']}")
