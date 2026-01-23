import json

# Load the hands
with open('hands_database.json', 'r') as f:
    hands = json.load(f)

# Rotate forward once more to check (E->N, S->E, W->S, N->W)
fixed_count = 0
for hand in hands:
    old_N = hand['N']
    old_E = hand['E']
    old_S = hand['S']
    old_W = hand['W']
    
    # Rotate back (W->N, N->E, E->S, S->W)
    hand['N'] = old_W
    hand['E'] = old_N
    hand['S'] = old_E
    hand['W'] = old_S
    fixed_count += 1

# Save the corrected hands
with open('hands_database.json', 'w') as f:
    json.dump(hands, f, indent=2)

print(f"✓ Rotated {fixed_count} hands forward")
print("\nNew positions - Board 1, 20.01.2026:")
h = [x for x in hands if x['date']=='20.01.2026' and x['board']==1][0]
print(f"  N: {h['N']}")
print(f"  E: {h['E']}")
print(f"  S: {h['S']}")
print(f"  W: {h['W']}")
