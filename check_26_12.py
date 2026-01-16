#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

records = [r for r in data if r.get('Tarih') == '26.12.2025']
print(f'26.12.2025 Toplam kayıt: {len(records)}')

# Event No'ya göre gruplama
by_event = {}
for rec in records:
    event_no = rec.get('Event No', 'N/A')
    if event_no not in by_event:
        by_event[event_no] = []
    by_event[event_no].append(rec)

print(f'\nEvent No sayısı: {len(by_event)}')
for event_no, recs in sorted(by_event.items()):
    print(f'\n  Event {event_no}: {len(recs)} kayıt')
    if recs:
        sample = recs[0]
        print(f'    Turnuva: {sample.get("Turnuva", "N/A")}')
        print(f'    İlk oyuncu: {sample.get("Oyuncu 1", "N/A")}')
