#!/usr/bin/env python3
"""
Extract DD values from BBO screenshot automatically using OCR.

Usage:
    python extract_dd_from_screenshot.py <image_file> <board_number>

Example:
    python extract_dd_from_screenshot.py board1.png 1
    
The script will read the DD table from the BBO screenshot and update the database.
"""

import sys
import json
import re
from pathlib import Path

try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
except ImportError:
    print("Error: Required packages not installed")
    print("Install with: pip install pytesseract pillow opencv-python numpy")
    print("\nYou also need to install Tesseract OCR:")
    print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
    print("  macOS:   brew install tesseract")
    print("  Linux:   sudo apt-get install tesseract-ocr")
    sys.exit(1)


def extract_dd_table_from_image(image_path):
    """
    Extract DD table values from BBO screenshot using OCR.
    
    Returns dict with keys: NTN, NTS, NTE, NTW, SN, SS, SE, SW, HN, HS, HE, HW, DN, DS, DE, DW, CN, CS, CE, CW
    """
    
    try:
        # Load image
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Enhance contrast for better OCR
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Get OCR text
        text = pytesseract.image_to_string(enhanced)
        
        print("Extracted text from image:")
        print("-" * 60)
        print(text)
        print("-" * 60)
        print()
        
        # Parse the DD table
        dd_values = parse_dd_table(text)
        
        if dd_values:
            print("Extracted DD values:")
            print_dd_table(dd_values)
            return dd_values
        else:
            print("Could not parse DD table from screenshot")
            return None
            
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def parse_dd_table(text):
    """
    Parse DD table from OCR text.
    
    Looking for pattern like:
        NT  S  H  D  C
    N   10  9  10 11 10
    S   9   11 11 9  9
    E   10  10 10 9  9
    W   9   12 11 10 11
    """
    
    lines = text.strip().split('\n')
    
    # Remove empty lines
    lines = [line.strip() for line in lines if line.strip()]
    
    # Find suit headers (NT, S, H, D, C) and player labels (N, S, E, W)
    dd_values = {}
    
    # Build a dictionary from the text
    # Try multiple parsing strategies
    
    # Strategy 1: Look for the table structure
    found_header = False
    suit_order = ['NT', 'S', 'H', 'D', 'C']
    player_order = ['N', 'S', 'E', 'W']
    
    for line in lines:
        # Skip header lines
        if 'NT' in line and 'S' in line and 'H' in line and 'D' in line and 'C' in line:
            found_header = True
            continue
        
        if not found_header:
            continue
        
        # Extract numbers from lines that start with player names
        if line and line[0] in player_order:
            player = line[0]
            # Extract all numbers from the rest of the line
            numbers = re.findall(r'\d+', line[1:])
            
            if len(numbers) >= 5:
                # Assign to suits
                for i, suit in enumerate(suit_order):
                    if i < len(numbers):
                        key = f"{suit}{player}"
                        dd_values[key] = int(numbers[i])
    
    # Validate we have all 20 values
    if len(dd_values) == 20:
        return dd_values
    
    # Strategy 2: Just extract all numbers and try to match them
    all_numbers = re.findall(r'\d+', text)
    all_numbers = [int(n) for n in all_numbers]
    
    if len(all_numbers) >= 20:
        # Assume the last 20 numbers form the DD table
        dd_numbers = all_numbers[-20:]
        
        idx = 0
        for suit in suit_order:
            for player in player_order:
                key = f"{suit}{player}"
                dd_values[key] = dd_numbers[idx]
                idx += 1
        
        return dd_values
    
    return None


def print_dd_table(dd_values):
    """Pretty print the DD table."""
    print("DD Table:")
    print("    N    S    E    W")
    print("   --- --- --- ---")
    
    suits = ['NT', 'S', 'H', 'D', 'C']
    players = ['N', 'S', 'E', 'W']
    
    for suit in suits:
        row = f"{suit:2} "
        for player in players:
            key = f"{suit}{player}"
            val = dd_values.get(key, '?')
            row += f"  {val:2} "
        print(row)


def update_database(board_number, dd_values):
    """Update the database with extracted DD values."""
    
    db_path = Path('app/www/hands_database.json')
    
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return False
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        # Update the board
        board_key = str(board_number)
        if board_key not in db['events']['hosgoru_04_01_2026']['boards']:
            print(f"Error: Board {board_number} not found in database")
            return False
        
        old_dd = db['events']['hosgoru_04_01_2026']['boards'][board_key]['dd_analysis']
        
        print(f"\nUpdating Board {board_number}...")
        print(f"Old DD values: {old_dd}")
        print(f"New DD values: {dd_values}")
        
        # Update the database
        db['events']['hosgoru_04_01_2026']['boards'][board_key]['dd_analysis'] = dd_values
        
        # Save
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Board {board_number} updated successfully!")
        return True
        
    except Exception as e:
        print(f"Error updating database: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    image_path = sys.argv[1]
    try:
        board_number = int(sys.argv[2])
    except ValueError:
        print(f"Error: Board number must be an integer")
        sys.exit(1)
    
    # Check if image exists
    if not Path(image_path).exists():
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    print(f"Processing screenshot: {image_path}")
    print(f"Board number: {board_number}")
    print()
    
    # Extract DD values
    dd_values = extract_dd_table_from_image(image_path)
    
    if dd_values and len(dd_values) == 20:
        # Validate values are in range 6-13
        valid = all(6 <= v <= 13 for v in dd_values.values())
        
        if valid:
            # Update database
            success = update_database(board_number, dd_values)
            if success:
                print("\n" + "="*60)
                print("SUCCESS! Board updated with extracted DD values.")
                print("="*60)
                sys.exit(0)
        else:
            print("Warning: Some DD values are outside valid range (6-13)")
            print("Please verify the screenshot quality")
            sys.exit(1)
    else:
        print("Error: Could not extract DD values from screenshot")
        print("Possible issues:")
        print("  - Screenshot quality too low")
        print("  - DD table not visible in the screenshot")
        print("  - Try adjusting the screenshot or zoom level")
        sys.exit(1)


if __name__ == '__main__':
    main()
