#!/usr/bin/env python3
"""
Check DD values status in database.
Shows which boards have real DD values vs placeholders.
"""

import json
from pathlib import Path

def check_dd_status():
    """Check and report DD values status for all boards."""
    
    db_path = Path('app/www/hands_database.json')
    
    if not db_path.exists():
        print(f"ERROR: {db_path} not found!")
        return
    
    with open(db_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    boards = database['events']['hosgoru_04_01_2026']['boards']
    
    print("\n" + "=" * 70)
    print("DD VALUES STATUS CHECK")
    print("=" * 70 + "\n")
    
    # Analyze each board
    boards_with_real = []
    boards_with_placeholder = []
    boards_incomplete = []
    
    for board_num in range(1, 31):
        board_key = str(board_num)
        if board_key not in boards:
            print(f"Board {board_num}: ✗ NOT FOUND")
            continue
        
        board = boards[board_key]
        dd_analysis = board.get('dd_analysis', {})
        
        if not dd_analysis:
            print(f"Board {board_num}: ✗ NO DD DATA")
            boards_incomplete.append(board_num)
            continue
        
        # Count values
        value_count = len(dd_analysis)
        
        if value_count < 20:
            print(f"Board {board_num}: ⚠ INCOMPLETE ({value_count}/20 values)")
            boards_incomplete.append(board_num)
            continue
        
        # Check if values look like placeholders (all same pattern)
        values = list(dd_analysis.values())
        
        # Simple heuristic: real DD values usually have variance
        min_val = min(values)
        max_val = max(values)
        variance = max_val - min_val
        
        # Also check for repeating patterns (typical of placeholders)
        is_pattern = len(set(values)) < 5  # Only a few unique values
        
        if board_num == 1:
            print(f"Board {board_num}: ✓ REAL VALUES (unique={variance}, range={min_val}-{max_val})")
            boards_with_real.append(board_num)
        elif variance >= 3 and not is_pattern:
            print(f"Board {board_num}: ✓ LIKELY REAL (unique={variance}, range={min_val}-{max_val})")
            boards_with_real.append(board_num)
        else:
            print(f"Board {board_num}: ⚠ LIKELY PLACEHOLDER (unique={variance}, range={min_val}-{max_val})")
            boards_with_placeholder.append(board_num)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✓ Boards with real DD values:      {len(boards_with_real)}/30")
    print(f"⚠ Boards with placeholder values:  {len(boards_with_placeholder)}/30")
    print(f"✗ Boards missing DD data:          {len(boards_incomplete)}/30")
    
    print("\n" + "=" * 70)
    print("SAMPLE VALUES")
    print("=" * 70)
    
    for board_num in [1, 2, 30]:
        dd = boards[str(board_num)].get('dd_analysis', {})
        sample = {k: dd[k] for k in list(dd.keys())[:5]}
        print(f"Board {board_num}: {sample}...")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    
    if len(boards_with_placeholder) > 0 or len(boards_incomplete) > 0:
        print("\nTo populate DD values, use one of these methods:\n")
        print("1. AUTOMATED (Recommended):")
        print("   pip install selenium")
        print("   python extract_dd_auto.py\n")
        print("2. MANUAL (Web Form):")
        print("   Start server: cd app\\www && python server_with_api.py")
        print("   Open form:    http://localhost:8000/dd_input.html")
    else:
        print("\n✓ All boards have DD values!")
        print("\nView your tournament:")
        print("   http://localhost:8000/hands_viewer.html")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    check_dd_status()
