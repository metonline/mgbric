#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check the new event 405659"""

import json
from unified_fetch import DataFetcher

fetcher = DataFetcher()

# Fetch event 405659
print("Fetching event 405659...")
hands = fetcher.fetch_hands_for_event(405659)

print(f"Fetched {len(hands)} hands\n")

if hands:
    h = hands[0]
    print(f"Sample hand:")
    print(f"  Event ID: {h.get('event_id')}")
    print(f"  Board: {h.get('board')}")
    print(f"  Date: {h.get('date')}")
    print(f"  Dealer: {h.get('dealer')}")
    print(f"  N: {h.get('N')[:20]}...")
