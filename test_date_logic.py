#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

# Test the parseDate logic
def parseDate(dateStr):
    day, month, year = dateStr.split('.')
    fullYear = '20' + year if len(year) == 2 else year
    return datetime(int(fullYear), int(month), int(day))

# Test date
test_date = '30.12.2025'
parsed = parseDate(test_date)
print(f'✓ Parsed {test_date}: {parsed}')

# Test date range for current month (December 2025)
today = datetime(2025, 12, 31)  # Simulate today as Dec 31
startDate = datetime(today.year, today.month, 1)

# Get last day of current month
if today.month == 12:
    endDate = datetime(today.year + 1, 1, 1) - timedelta(days=1)
else:
    endDate = datetime(today.year, today.month + 1, 1) - timedelta(days=1)

print(f'Current month range: {startDate.strftime("%d.%m.%Y")} to {endDate.strftime("%d.%m.%Y")}')
print(f'Is 30.12.2025 in range? {startDate <= parsed <= endDate}')

# Test what JavaScript's new Date() does
print('\n--- JavaScript new Date() behavior ---')
print('JavaScript: new Date(2025, 11, 30) creates:', datetime(2025, 12, 30))
print('  (month is 0-indexed, so 11 = December)')
