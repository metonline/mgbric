#!/usr/bin/env python3
"""
Reverse the incorrect hand rotation
"""
import json

def reverse_rotate_hands_by_dealer(hands_dict, dealer):
    """
    REVERSE the rotation - undo what was applied
    """
    reverse_rotations = {
        'N': {'N': 'N', 'E': 'E', 'S': 'S', 'W': 'W'},  # No rotation to undo
        'E': {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'},  # Reverse of {'N': 'W', 'E': 'N', 'S': 'E', 'W': 'S'}
        'S': {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'},  # Reverse of {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'}
        'W': {'N': 'W', 'E': 'N', 'S': 'E', 'W': 'S'},  # Reverse of {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}
    }
    
    rotation_map = reverse_rotations[dealer]
    rotated = {}
    for key, value in rotation_map.items():
        rotated[key] = hands_dict[value]
    
    return rotated

# Load current hands
with open('hands_database.json', 'r', encoding='utf-8') as f:
    hands = json.load(f)

print(f"Reversing rotation for {len(hands)} hands...")

# Reverse rotation for each hand
for i, hand in enumerate(hands):
    if i % 50 == 0:
        print(f"  Reversed {i}/{len(hands)}...")
    
    dealer = hand.get('dealer', 'N')
    
    # Get current hands
    current = {
        'N': hand.get('N'),
        'E': hand.get('E'),
        'S': hand.get('S'),
        'W': hand.get('W'),
    }
    
    # Reverse the rotation
    rotated = reverse_rotate_hands_by_dealer(current, dealer)
    
    # Update hands
    hand['N'] = rotated['N']
    hand['E'] = rotated['E']
    hand['S'] = rotated['S']
    hand['W'] = rotated['W']

print(f"✓ Reversed rotation for all hands")

# Save
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(hands, f, ensure_ascii=False, indent=2)

print("✓ Saved hands_database.json")

# Verify
h = hands[0]
print()
print("Sample hand verification:")
print(f"  Board {h['board']}, Date {h['date']}, Dealer {h['dealer']}")
print(f"  N: {h['N']}")
print(f"  E: {h['E']}")
print(f"  S: {h['S']}")
print(f"  W: {h['W']}")
