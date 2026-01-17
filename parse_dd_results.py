#!/usr/bin/env python3
"""
Parse DD results HTML from DDS solver and update hands_database.json with exact values.
Steps:
1. Run generate_pbn_for_dds.py
2. Upload to DDS solver and get results
3. Save results as dd_results.html
4. Run this script to extract and update database
"""

import json
import re
from pathlib import Path
from html.parser import HTMLParser


class DDResultsParser(HTMLParser):
    """Parse DD analysis table from DDS solver HTML."""
    
    def __init__(self):
        super().__init__()
        self.current_board = None
        self.dd_results = {}
        self.in_table = False
        self.in_row = False
        self.row_data = []
        self.board_in_table = None
    
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
        elif tag == 'tr' and self.in_table:
            self.in_row = True
            self.row_data = []
        elif tag == 'th' or tag == 'td':
            pass
    
    def handle_endtag(self, tag):
        if tag == 'tr' and self.in_row:
            self.in_row = False
            if self.row_data:
                self.process_row(self.row_data)
        elif tag == 'table':
            self.in_table = False
    
    def handle_data(self, data):
        if self.in_row:
            data = data.strip()
            if data:
                self.row_data.append(data)
    
    def process_row(self, row):
        """Process a row from the DD results table."""
        # Different DDS solver versions have different formats
        # Common format: [Contract] [Tricks_N] [Tricks_E] [Tricks_S] [Tricks_W]
        # or: [Board] [Contract] [Tricks] etc.
        
        if len(row) < 2:
            return
        
        first_col = row[0].strip()
        
        # Try to identify board number
        if first_col.isdigit() and self.board_in_table is None:
            self.board_in_table = first_col
            return
        
        # Try to match contract (NT, S, H, D, C followed by tricks)
        contracts = ['NT', 'S', 'H', 'D', 'C']
        for contract in contracts:
            if contract in first_col:
                # This row contains contract results
                try:
                    # Parse remaining columns as trick counts
                    if self.board_in_table:
                        if self.board_in_table not in self.dd_results:
                            self.dd_results[self.board_in_table] = {}
                        
                        # Extract tricks for each player
                        # Typically: NT column has N/E/S/W tricks separated
                        # This is a simplified version - adjust based on actual HTML structure
                        
                except Exception as e:
                    print(f"Error parsing {contract}: {e}")


def parse_dds_html_regex(html_content):
    """
    Parse DD results from HTML using regex.
    Extracts tables with trick counts for each contract and player.
    """
    results = {}
    
    # Pattern: Board XXX, Contract NT: N=9, E=4, S=9, W=5
    # or similar variations
    
    # Look for board numbers
    board_pattern = r'Board\s+(\d+)'
    contract_pattern = r'(NT|[SHDC])\s*[:=]?\s*N[T=]*\s*(\d+)'
    
    boards = re.finditer(board_pattern, html_content)
    
    for board_match in boards:
        board_id = board_match.group(1)
        start_pos = board_match.end()
        
        # Find next board or end of content
        next_board = re.search(board_pattern, html_content[start_pos:])
        end_pos = start_pos + next_board.start() if next_board else len(html_content)
        
        board_section = html_content[start_pos:end_pos]
        
        # Extract contracts and tricks for this board
        board_dd = {}
        
        # Look for contract results (format varies by solver)
        # Try multiple patterns
        contract_matches = re.finditer(
            r'([SHDC]|NT)\s+(?:N|N[T]?)[=:]?(\d+)\s+E[=:]?(\d+)\s+S[=:]?(\d+)\s+W[=:]?(\d+)',
            board_section,
            re.IGNORECASE
        )
        
        for match in contract_matches:
            suit = match.group(1).upper()
            n_tricks = int(match.group(2))
            e_tricks = int(match.group(3))
            s_tricks = int(match.group(4))
            w_tricks = int(match.group(5))
            
            board_dd[f'{suit}N'] = n_tricks
            board_dd[f'{suit}E'] = e_tricks
            board_dd[f'{suit}S'] = s_tricks
            board_dd[f'{suit}W'] = w_tricks
        
        if board_dd:
            results[board_id] = board_dd
    
    return results


def main():
    html_path = Path('dd_results.html')
    db_path = Path('hands_database.json')
    
    if not html_path.exists():
        print(f"[ERROR] {html_path} not found")
        print(f"[INFO] Steps:")
        print(f"1. Run: python generate_pbn_for_dds.py")
        print(f"2. Upload to: https://dds.bridgewebs.com/bsol_standalone/ddummy.html")
        print(f"3. Save results as {html_path}")
        return
    
    if not db_path.exists():
        print(f"[ERROR] {db_path} not found")
        return
    
    print(f"[OK] Found {html_path}")
    print(f"[INFO] Parsing DD results...\n")
    
    with open(html_path, encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse results from HTML
    dd_results = parse_dds_html_regex(html_content)
    
    print(f"[OK] Extracted DD results for {len(dd_results)} boards")
    
    if len(dd_results) == 0:
        print(f"[ERROR] No results found. HTML format may be different.")
        print(f"[INFO] Please check {html_path} structure and adjust regex patterns")
        return
    
    # Load database
    with open(db_path) as f:
        database = json.load(f)
    
    # Update database with exact DD values
    updated = 0
    for board_id, dd_data in dd_results.items():
        if board_id in database:
            database[board_id]['dd_analysis'] = dd_data
            updated += 1
    
    # Save updated database
    with open(db_path, 'w') as f:
        json.dump(database, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"[COMPLETE] Updated {updated} boards with EXACT DD values")
    print(f"[SAVED] {db_path}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
