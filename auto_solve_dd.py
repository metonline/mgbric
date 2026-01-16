#!/usr/bin/env python3
"""
Automated DD solver - Upload LIN file and get contract levels
"""
import requests
import json
import time
import re

def upload_to_bridgewebs(lin_file_path):
    """Upload LIN file to BridgeWebs DD solver"""
    
    url = "https://dds.bridgewebs.com/bridgesolver/upload.htm"
    
    try:
        # Try to read the API endpoint
        print("Attempting to upload to BridgeWebs solver...")
        
        with open(lin_file_path, 'rb') as f:
            files = {'file': f}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Try POST to upload endpoint
            response = requests.post(
                "https://dds.bridgewebs.com/bridgesolver/upload.htm",
                files=files,
                headers=headers,
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response length: {len(response.text)}")
            
            # Save response for inspection
            with open('solver_response.html', 'w', encoding='utf-8') as out:
                out.write(response.text)
            
            print("Saved response to solver_response.html")
            
            # Try to extract results from response
            if 'Board' in response.text:
                print("Found board data in response")
                return response.text
            else:
                print("No board data found in response")
                return None
                
    except Exception as e:
        print(f"Error uploading: {e}")
        return None

def parse_solver_output(html_content):
    """Parse DD results from solver HTML output"""
    
    results = {}
    
    # Look for patterns like "Board 1: NT(4,4,3,3) S(3,3,4,4) H(5,5,2,2) D(3,3,4,4) C(0,0,5,5)"
    board_pattern = r'Board (\d+)[:\s]+([^\n<]*)'
    
    matches = re.finditer(board_pattern, html_content)
    
    for match in matches:
        board_num = match.group(1)
        data = match.group(2)
        
        # Try to parse suit data
        suits = {}
        
        # Look for NT, S, H, D, C with values
        suit_pattern = r'([NSHDC]+)[:\s]*\(?(\d+)[,\s]+(\d+)[,\s]+(\d+)[,\s]+(\d+)\)?'
        
        suit_matches = re.finditer(suit_pattern, data)
        for suit_match in suit_matches:
            suit = suit_match.group(1)
            n_val = int(suit_match.group(2))
            s_val = int(suit_match.group(3))
            e_val = int(suit_match.group(4))
            w_val = int(suit_match.group(5))
            
            suits[suit] = {'N': n_val, 'S': s_val, 'E': e_val, 'W': w_val}
        
        if suits:
            results[board_num] = suits
    
    return results

def update_database_with_dd(dd_results):
    """Update hands_database.json with DD contract levels"""
    
    db_file = r"c:\Users\metin\Desktop\BRIC\app\www\hands_database.json"
    
    with open(db_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    boards = data['events']['hosgoru_04_01_2026']['boards']
    
    updated_count = 0
    
    for board_num_str, suits in dd_results.items():
        board_num = int(board_num_str)
        board_key = str(board_num)
        
        if board_key not in boards:
            print(f"Board {board_num} not found in database")
            continue
        
        # Create DD analysis structure
        dd_analysis = {}
        
        # Map suits to keys: NT, S, H, D, C
        suit_order = ['NT', 'S', 'H', 'D', 'C']
        
        for suit in suit_order:
            if suit in suits:
                values = suits[suit]
                dd_analysis[f'{suit}N'] = values.get('N', 0)
                dd_analysis[f'{suit}S'] = values.get('S', 0)
                dd_analysis[f'{suit}E'] = values.get('E', 0)
                dd_analysis[f'{suit}W'] = values.get('W', 0)
        
        boards[board_key]['dd_analysis'] = dd_analysis
        updated_count += 1
        print(f"Updated Board {board_num}")
    
    # Save updated database
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {updated_count} boards in database")
    
    return updated_count

def main():
    lin_file = r"c:\Users\metin\Desktop\BRIC\boards_for_solver.lin"
    
    print("="*60)
    print("BridgeWebs DD Solver - Automated Upload")
    print("="*60)
    
    # Upload file
    response_html = upload_to_bridgewebs(lin_file)
    
    if response_html:
        # Parse results
        dd_results = parse_solver_output(response_html)
        
        print(f"\nParsed {len(dd_results)} boards from solver")
        
        if dd_results:
            # Show sample
            for board_num in sorted(list(dd_results.keys())[:3]):
                print(f"Board {board_num}: {dd_results[board_num]}")
            
            # Update database
            count = update_database_with_dd(dd_results)
            print(f"\nDatabase updated successfully!")
        else:
            print("No results found in solver output")
            print("Check solver_response.html for debug info")
    else:
        print("Failed to upload to solver")

if __name__ == '__main__':
    main()
