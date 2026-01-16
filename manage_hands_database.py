#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive tool to add tournament hands to database
"""

import json
import os

def load_database(db_path):
    """Load existing hands database"""
    if os.path.exists(db_path):
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading database: {e}")
    return {}

def save_database(db_path, database):
    """Save hands database"""
    try:
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False

def show_menu():
    """Show interactive menu"""
    db_path = r'C:\Users\metin\Desktop\BRIC\app\www\hands_database.json'
    
    print("=" * 60)
    print("📊 Tournament Hands Database Manager")
    print("=" * 60)
    
    # Load database
    db = load_database(db_path)
    current_count = len(db)
    
    print(f"\n📂 Current database: {current_count} boards\n")
    print("Options:")
    print("  1. Add hands from JSON file")
    print("  2. View current boards")
    print("  3. Add sample tournament hands")
    print("  4. Exit\n")
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == '1':
        add_from_json(db_path, db)
    elif choice == '2':
        view_boards(db)
    elif choice == '3':
        add_sample_tournament(db_path, db)
    elif choice == '4':
        print("\nExiting...")
        return
    else:
        print("Invalid choice")

def add_from_json(db_path, db):
    """Add hands from JSON file"""
    print("\n📁 Add hands from JSON file")
    print("-" * 60)
    
    json_file = input("Enter JSON file path (absolute or relative): ").strip()
    
    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            new_hands = json.load(f)
        
        # Validate structure
        if not isinstance(new_hands, dict):
            print("❌ Invalid JSON structure - must be a dictionary")
            return
        
        # Find highest board number
        highest_board = max([int(k) for k in db.keys() if k.isdigit()]) if any(k.isdigit() for k in db.keys()) else 0
        
        # Add new boards
        boards_added = 0
        for board_data in new_hands.values() if isinstance(next(iter(new_hands.values())), dict) else [new_hands]:
            highest_board += 1
            db[str(highest_board)] = board_data
            boards_added += 1
        
        # Save
        if save_database(db_path, db):
            print(f"✅ Added {boards_added} boards")
            print(f"   Database now contains {len(db)} boards")
        else:
            print("❌ Failed to save")
    
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON file: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def view_boards(db):
    """View existing boards"""
    print("\n📋 Existing Boards")
    print("-" * 60)
    
    board_numbers = sorted([int(k) for k in db.keys() if k.isdigit()])
    
    if not board_numbers:
        print("No boards in database")
        return
    
    print(f"Total boards: {len(board_numbers)}")
    print(f"Board range: {board_numbers[0]} - {board_numbers[-1]}\n")
    
    # Show sample
    print("Sample boards:")
    for board_num in board_numbers[:5]:
        board = db[str(board_num)]
        print(f"  Board {board_num}:")
        if isinstance(board, dict):
            for player, hand in board.items():
                if isinstance(hand, dict):
                    cards = ' '.join([f"{s}:{h}" for s, h in hand.items() if h])
                    print(f"    {player}: {cards}")

def add_sample_tournament(db_path, db):
    """Add sample tournament hands (for testing)"""
    print("\n➕ Add Sample Tournament Hands")
    print("-" * 60)
    
    # Sample hands for testing
    sample_hands = {
        "N": {"S": "AK9", "H": "QJ8", "D": "K87", "C": "AQJ"},
        "E": {"S": "QT8", "H": "A765", "D": "J92", "C": "K65"},
        "S": {"S": "J765", "H": "K942", "D": "AQT", "C": "87"},
        "W": {"S": "432", "H": "T3", "D": "643", "C": "T9432"}
    }
    
    highest_board = max([int(k) for k in db.keys() if k.isdigit()]) if any(k.isdigit() for k in db.keys()) else 0
    
    num_boards = input("How many sample boards to add? (default: 1): ").strip()
    try:
        num_boards = int(num_boards) if num_boards else 1
    except ValueError:
        num_boards = 1
    
    for i in range(num_boards):
        highest_board += 1
        db[str(highest_board)] = sample_hands.copy()
    
    if save_database(db_path, db):
        print(f"✅ Added {num_boards} sample boards")
        print(f"   Database now contains {len(db)} boards")
    else:
        print("❌ Failed to save")

if __name__ == '__main__':
    show_menu()
