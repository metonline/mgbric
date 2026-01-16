#!/usr/bin/env python3
"""Manual database update script"""

from scheduler import DatabaseScheduler
import json
from datetime import datetime

print('='*60)
print('Starting manual database update: 12.01.2026 to 16.01.2026')
print('='*60)

# Create scheduler instance
scheduler = DatabaseScheduler()

# Update database
result = scheduler.update_database()

# Check database size
try:
    with open('database.json', 'r') as f:
        data = json.load(f)
    print(f'\n✅ Database now contains {len(data)} records')
    if data:
        print(f'Latest record date: {data[-1]["Tarih"]}')
except Exception as e:
    print(f'Error reading database: {e}')

print('='*60)
