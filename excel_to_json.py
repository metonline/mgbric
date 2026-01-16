#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
import os

# Excel'i JSON'a çevir
def excel_to_json():
    """Convert database.xlsx to database.json"""
    xlsx_file = 'database.xlsx'
    json_file = 'database.json'
    
    if not os.path.exists(xlsx_file):
        print(f"Error: {xlsx_file} not found")
        return False
    
    try:
        # Read Excel
        df = pd.read_excel(xlsx_file, sheet_name='Sonuçlar')
        print(f"✓ Read {len(df)} records from {xlsx_file}")
        
        # Convert to records
        records = df.to_dict('records')
        
        # Write to JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=None)
        
        # Verify written records
        with open(json_file, 'r', encoding='utf-8') as f:
            written = json.load(f)
        
        print(f"✓ Saved {len(written)} records to {json_file}")
        
        if len(written) != len(records):
            print(f"⚠ Warning: {len(records) - len(written)} records were lost!")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    excel_to_json()
