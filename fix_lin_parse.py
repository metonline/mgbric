import re

with open('event_405376.lin', 'r') as f:
    lines = f.readlines()

for i in range(3):
    line = lines[i]
    
    # Extract board number from "ah|Board NUM|"
    board_match = re.search(r'\|ah\|Board (\d+)\|', line)
    # Extract hands from md|
    hands_match = re.search(r'md\|([1-4])(.*?)\|sv', line)
    
    if board_match and hands_match:
        board_num = int(board_match.group(1))
        hands_str = hands_match.group(2)
        hands_list = hands_str.split(',')
        
        print(f"Board {board_num}:")
        print(f"  N: {hands_list[0]}")
        print(f"  E: {hands_list[1]}")
        print(f"  S: {hands_list[2]}")
        print()
