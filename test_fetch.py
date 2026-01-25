#!/usr/bin/env python3
import json
from unified_fetch import DataFetcher

df = DataFetcher()
print(f'Before: {len(df.hands)} hands')

# Fetch one event  
hands = df.fetch_hands_for_event(404155)
print(f'Fetched {len(hands)} hands from 404155')
if hands:
    print(f'First hand: {json.dumps(hands[0], indent=2, default=str)}')
