#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import json

xlsx_file = 'database.xlsx'
json_file = 'database.json'

if os.path.exists(xlsx_file):
    try:
        # Read Excel
        df = pd.read_excel(xlsx_file, sheet_name='Sonuçlar')
        print(f'Excel Total rows: {len(df)}')
        
        # Check for duplicate rows
        duplicates = df.duplicated(keep=False).sum()
        print(f'Duplicate rows: {duplicates}')
        
        # Check for rows with NaN values in key columns
        df_with_nan = df[df.isnull().any(axis=1)]
        print(f'Rows with ANY null values: {len(df_with_nan)}')
        
        # Convert to records and check
        records = df.to_dict('records')
        print(f'Records after to_dict: {len(records)}')
        
        # Check JSON
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            print(f'JSON Total records: {len(json_data)}')
            
            # Find missing records
            excel_set = set((r['Sıra'], r['Oyuncu 1'], r['Oyuncu 2']) for r in records)
            json_set = set((r['Sıra'], r['Oyuncu 1'], r['Oyuncu 2']) for r in json_data)
            
            missing = excel_set - json_set
            extra = json_set - excel_set
            
            print(f'\nMissing from JSON (Excel but not in JSON): {len(missing)}')
            if missing:
                print('Examples of missing:', list(missing)[:5])
            
            print(f'Extra in JSON (JSON but not in Excel): {len(extra)}')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
else:
    print('Excel file not found')
