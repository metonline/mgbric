#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for tarih in ['26.12.2025', '30.12.2025']:
    records = [r for r in data if r.get('Tarih') == tarih]
    print(f'\n{tarih} - Toplam: {len(records)} kayıt')
    
    # Turnuva'ya göre gruplama
    by_turnuva = {}
    for rec in records:
        turnuva = rec.get('Turnuva', 'N/A')
        if turnuva not in by_turnuva:
            by_turnuva[turnuva] = []
        by_turnuva[turnuva].append(rec)
    
    print(f'  Turnuva sayısı: {len(by_turnuva)}')
    for turnuva, recs in list(by_turnuva.items())[:5]:
        event_nos = set(r.get('Event No', 'N/A') for r in recs)
        print(f'    - {turnuva[:40]}: {len(recs)} kayıt, Event No: {event_nos}')
