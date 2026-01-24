#!/usr/bin/env python3
"""
Generate LIN data for all hands in the database
Adds lin_string and bbo_url to each hand
"""

import json
from urllib.parse import quote

def hand_string_to_lin(hand_str):
    """Convert hand string (S.H.D.C) to LIN format (SxxxHxxxDxxxCxxx)"""
    if not hand_str:
        return ''
    parts = hand_str.split('.')
    s = parts[0] if len(parts) > 0 else ''
    h = parts[1] if len(parts) > 1 else ''
    d = parts[2] if len(parts) > 2 else ''
    c = parts[3] if len(parts) > 3 else ''
    return f'S{s}H{h}D{d}C{c}'

def generate_bbo_lin(hand, dealer, vulnerability='None'):
    """Generate complete LIN string for BBO hand viewer"""
    dealer_map = {'N': '1', 'E': '2', 'S': '3', 'W': '4'}
    d = dealer_map.get(dealer, '1')
    
    vuln_map = {'None': '0', 'NS': '1', 'EW': '2', 'Both': '3'}
    v = vuln_map.get(vulnerability, '0')
    
    # Order hands according to dealer
    dealer_order = {
        'N': ['N', 'E', 'S'],
        'E': ['E', 'S', 'W'],
        'S': ['S', 'W', 'N'],
        'W': ['W', 'N', 'E']
    }
    
    ordered = dealer_order.get(dealer, ['N', 'E', 'S'])
    hand_strings = [hand_string_to_lin(hand.get(pos)) for pos in ordered]
    hands_str = ','.join(hand_strings)
    
    return f'qx|o1|md|{d}{hands_str},|rh||ah|Board|sv|{v}|pg||'

def generate_bbo_viewer_url(hand, dealer, vulnerability='None', board_num=''):
    """Generate BBO viewer URL"""
    lin = generate_bbo_lin(hand, dealer, vulnerability)
    base_url = 'https://www.bridgebase.com/tools/handviewer.html'
    return f'{base_url}?lin={quote(lin)}'

def main():
    # Load hands database
    try:
        with open('hands_database.json', 'r', encoding='utf-8') as f:
            hands = json.load(f)
    except FileNotFoundError:
        print("❌ hands_database.json not found")
        return
    
    if not hands:
        print("❌ No hands in database")
        return
    
    # Generate LIN for each hand
    updated_count = 0
    for hand in hands:
        dealer = hand.get('dealer', 'N')
        board = hand.get('board', '')
        
        # Generate LIN string
        lin_string = generate_bbo_lin(hand, dealer)
        hand['lin_string'] = lin_string
        
        # Generate BBO URL
        bbo_url = generate_bbo_viewer_url(hand, dealer, 'None', board)
        hand['bbo_url'] = bbo_url
        
        updated_count += 1
    
    # Save updated database
    with open('hands_database.json', 'w') as f:
        json.dump(hands, f, indent=2)
    
    print(f"✅ Generated LIN data for {updated_count} hands")
    print(f"📊 Database updated: hands_database.json")
    
    # Show sample
    if hands:
        sample = hands[0]
        print(f"\n📋 Sample (Board {sample.get('board', 'N/A')}):")
        print(f"  Dealer: {sample.get('dealer')}")
        print(f"  LIN: {sample.get('lin_string', 'N/A')[:50]}...")
        print(f"  URL: {sample.get('bbo_url', 'N/A')[:80]}...")

if __name__ == '__main__':
    main()
