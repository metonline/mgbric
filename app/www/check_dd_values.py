import json

data = json.load(open('hands_database.json', encoding='utf-8'))
boards = data['events']['hosgoru_04_01_2026']['boards']

print("DD Values Sample:\n")
for board_num in [1, 2, 5, 10, 15, 20, 25, 30]:
    board = boards[str(board_num)]
    dd = board.get('dd_analysis', {})
    
    # Count non-zero values
    non_zero = sum(1 for v in dd.values() if v != 0)
    
    print(f"Board {board_num:2d}: {non_zero:2d}/20 values set")
    print(f"  NT: N={dd.get('NTN', 0)} S={dd.get('NTS', 0)} E={dd.get('NTE', 0)} W={dd.get('NTW', 0)}")
    print(f"  ♠:  N={dd.get('SN', 0)} S={dd.get('SS', 0)} E={dd.get('SE', 0)} W={dd.get('SW', 0)}")
    print()

print("\nTotal DD values by board:")
for board_num in range(1, 31):
    board = boards[str(board_num)]
    dd = board.get('dd_analysis', {})
    non_zero = sum(1 for v in dd.values() if v != 0)
    print(f"Board {board_num:2d}: {non_zero:2d}/20 values", "✓" if non_zero > 0 else "✗")
