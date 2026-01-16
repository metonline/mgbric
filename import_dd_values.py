#!/usr/bin/env python3
"""
Parse DD values from user input and update database
Format: Board N: N S E W (for each suit in order NT S H D C)
"""
import json
import sys

def parse_dd_input(input_text):
    """Parse user input for DD values"""
    results = {}
    
    for line in input_text.strip().split('\n'):
        line = line.strip()
        if not line or 'Board' not in line:
            continue
        
        # Parse: Board N: values...
        parts = line.split(':')
        if len(parts) < 2:
            continue
        
        # Extract board number
        board_part = parts[0].strip()
        board_num = board_part.split()[-1]
        
        # Extract values
        values_str = parts[1].strip()
        values = [int(v) for v in values_str.split() if v.isdigit()]
        
        if len(values) == 20:  # NT(4) S(4) H(4) D(4) C(4)
            results[board_num] = values
        else:
            print(f"Warning: Board {board_num} has {len(values)} values, expected 20")
    
    return results

def values_to_dd_analysis(values):
    """Convert 20 values to DD analysis dict"""
    # values order: NTN NTS NTE NTW SN SS SE SW HN HS HE HW DN DS DE DW CN CS CE CW
    suits = ['NT', 'S', 'H', 'D', 'C']
    players = ['N', 'S', 'E', 'W']
    dd_analysis = {}
    
    idx = 0
    for suit in suits:
        for player in players:
            dd_analysis[f'{suit}{player}'] = values[idx]
            idx += 1
    
    return dd_analysis

def main():
    print("Paste DD values (Board N: 20 space-separated numbers)")
    print("Press Ctrl+Z then Enter to finish")
    print()
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    input_text = '\n'.join(lines)
    
    if not input_text.strip():
        print("No input provided")
        return
    
    results = parse_dd_input(input_text)
    
    if not results:
        print("No valid board data found")
        return
    
    print(f"\nParsed {len(results)} boards")
    
    # Load database
    db_file = r"c:\Users\metin\Desktop\BRIC\app\www\hands_database.json"
    with open(db_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    boards = data['events']['hosgoru_04_01_2026']['boards']
    
    # Update boards
    updated = 0
    for board_num_str, values in results.items():
        board_num = int(board_num_str)
        if str(board_num) in boards:
            dd_analysis = values_to_dd_analysis(values)
            boards[str(board_num)]['dd_analysis'] = dd_analysis
            updated += 1
            print(f"Updated Board {board_num}")
    
    # Save database
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDatabase updated with {updated} boards!")
    print("Refresh your browser to see the DD tables.")

if __name__ == '__main__':
    main()
