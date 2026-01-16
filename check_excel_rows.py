#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import json

xlsx_file = 'database.xlsx'
json_file = 'database.json'

if os.path.exists(xlsx_file):
    try:
        df = pd.read_excel(xlsx_file, sheet_name='Sonuçlar')
        print(f'Excel Total rows: {len(df)}')
        print(f'Columns: {list(df.columns)}')
        print(f'Data types:\n{df.dtypes}')
        
        # Check for null values
        print(f'\nNull values per column:')
        print(df.isnull().sum())
        
        # Check JSON
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            print(f'\nJSON Total records: {len(json_data)}')
        else:
            print(f'\nJSON file not found')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
else:
    print('Excel file not found')
