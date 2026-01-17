#!/usr/bin/env python3
"""Quick fetch for 13-16 Jan 2026"""

from vugraph_fetcher import VugraphDataFetcher
from datetime import datetime, timedelta

fetcher = VugraphDataFetcher()

# Fetch for each day from 13-16 Jan
dates = ['13.01.2026', '14.01.2026', '15.01.2026', '16.01.2026']

for tarih in dates:
    print(f"\n{'='*60}")
    print(f"Processing: {tarih}")
    print(f"{'='*60}")
    success = fetcher.add_date_to_database(tarih)
    if success:
        print(f"✅ {tarih} başarıyla eklendi")
    else:
        print(f"❌ {tarih} hata: {fetcher.errors}")
    fetcher.errors = []
    fetcher.records_added = []

print("\n✅ Tüm tarihler işlendi")
