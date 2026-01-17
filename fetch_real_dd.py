#!/usr/bin/env python3
"""
Fetch real DD (Double Dummy) solutions from DDS Bridge Solver
https://dds.bridgewebs.com/bsol_standalone/ddummy.html
"""

import json
import time
import requests
from pathlib import Path
from typing import Dict, Optional

# DDS Solver URL
DDS_SOLVER_URL = "https://dds.bridgewebs.com/bsol_standalone/ddummy.html"

def hand_to_lin(hand_id: str, hand: Dict) -> str:
    """Convert hand to LIN format for DDS solver"""
    try:
        dealer_map = {'N': 1, 'E': 2, 'S': 3, 'W': 4}
        vuln_map = {'None': 0, 'NS': 1, 'EW': 2, 'Both': 3}
        
        dealer = dealer_map.get(hand.get('dealer', 'N'), 1)
        vuln = vuln_map.get(hand.get('vulnerability', 'None'), 0)
        
        # LIN format: qx|o1|md|{dealer}{N},{E},{S}|rh||ah|Board {id}|sv|{vuln}|pg||
        lin = f"qx|o1|md|{dealer}{hand['N']},{hand['E']},{hand['S']}|rh||ah|Board {hand_id}|sv|{vuln}|pg||"
        return lin
    except Exception as e:
        print(f"  [ERROR] Failed to convert hand {hand_id}: {e}")
        return None

def submit_to_dds(lin: str) -> Optional[Dict]:
    """
    Submit hand to DDS solver and get results
    Returns dict with DD values or None on failure
    """
    try:
        # DDS expects LIN format via URL parameter
        url = f"{DDS_SOLVER_URL}?lin={lin}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"  Submitting to DDS solver...", end=" ", flush=True)
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Parse HTML response to extract DD values
            html = response.text
            dd_values = parse_dds_response(html)
            if dd_values:
                print("[OK]")
                return dd_values
            else:
                print("[PARSE ERROR]")
                return None
        else:
            print(f"[HTTP {response.status_code}]")
            return None
            
    except requests.Timeout:
        print("[TIMEOUT]")
        return None
    except Exception as e:
        print(f"[ERROR: {e}]")
        return None

def parse_dds_response(html: str) -> Optional[Dict]:
    """
    Parse DD values from DDS solver HTML response
    Looking for table with NT, S, H, D, C rows and N, E, S, W columns
    """
    try:
        import re
        
        dd_values = {}
        suits = ['NT', 'S', 'H', 'D', 'C']
        players = ['N', 'E', 'S', 'W']
        
        # Look for patterns like "9" in table cells
        # This is a simplified parser - may need adjustment based on actual HTML
        for suit in suits:
            for player in players:
                # Try to find pattern in HTML (very basic)
                pattern = f"{suit}.*?{player}"
                if re.search(pattern, html):
                    # Extract number following the pattern
                    match = re.search(rf"{suit}[^0-9]*({player}[^0-9]*)?(\d+)", html)
                    if match:
                        value = int(match.group(2))
                        dd_values[f'{suit}{player}'] = value
        
        return dd_values if dd_values else None
        
    except Exception as e:
        print(f"    [Parse error: {e}]")
        return None

def fetch_dd_for_board(hand_id: str, hand: Dict) -> Optional[Dict]:
    """Fetch real DD analysis for a single board"""
    try:
        lin = hand_to_lin(hand_id, hand)
        if not lin:
            return None
        
        print(f"Board {hand_id}: ", end="", flush=True)
        
        dd_values = submit_to_dds(lin)
        return dd_values
        
    except Exception as e:
        print(f"Board {hand_id}: [ERROR: {e}]")
        return None

def main():
    """Fetch real DD solutions for all boards"""
    
    db_path = Path('hands_database.json')
    if not db_path.exists():
        print("[ERROR] hands_database.json not found")
        return
    
    print("[INFO] Loading hands database...")
    with open(db_path, 'r', encoding='utf-8') as f:
        hands_db = json.load(f)
    
    total = len(hands_db)
    updated = 0
    skipped = 0
    
    print(f"[INFO] Found {total} boards")
    print(f"[INFO] Fetching real DD solutions from DDS solver...\n")
    
    for i, (hand_id, hand) in enumerate(hands_db.items(), 1):
        # Skip if already has real DD data
        if hand.get('dd_analysis') and hand.get('dd_source') == 'dds':
            skipped += 1
            if i % 10 == 0:
                print(f"  [{i}/{total}] Skipping (already solved)")
            continue
        
        dd_values = fetch_dd_for_board(hand_id, hand)
        
        if dd_values:
            hand['dd_analysis'] = dd_values
            hand['dd_source'] = 'dds'  # Mark as from real solver
            updated += 1
        
        # Rate limiting - be nice to the server
        if i % 5 == 0:
            print(f"  [{i}/{total}] Waiting 2 seconds...")
            time.sleep(2)
        elif dd_values:
            time.sleep(0.5)
        
        if i % 50 == 0:
            print(f"  Progress: {i}/{total} ({updated} updated)")
    
    print(f"\n[INFO] Saving updated database...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(hands_db, f, indent=2, ensure_ascii=False)
    
    print(f"\n[DONE] Results:")
    print(f"  - Updated: {updated} boards")
    print(f"  - Skipped: {skipped} boards (already solved)")
    print(f"  - Total: {total} boards")

if __name__ == '__main__':
    main()
