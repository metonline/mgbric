import re

with open('event_405376.lin', 'r') as f:
    lines = f.readlines()

for i in range(3):
    line = lines[i]
    print(f"Line {i+1}:")
    print(f"  Full: {line[:180]}")
    
    # Extract the board info differently
    # Look for "md|DIGIT" where DIGIT is 1-4
    md_match = re.search(r'md\|([1-4])(.*?)\|sv', line)
    if md_match:
        board = md_match.group(1)
        hands = md_match.group(2)
        print(f"  Board: {board}")
        print(f"  Hands part: {hands[:100]}")
        print(f"  Hands list: {hands.split(',')}")
    print()
