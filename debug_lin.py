import re

lin_file = 'event_405376.lin'
boards_found = {}

with open(lin_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
            
        # Find md| section
        md_match = re.search(r'md\|(\d+)(.*?)\|sv\|', line)
        if md_match:
            board_num = int(md_match.group(1))
            if board_num not in boards_found:
                boards_found[board_num] = line[:120]

print("Boards found in LIN file:")
for board_num in sorted(boards_found.keys()):
    print(f"Board {board_num}: {boards_found[board_num]}")
