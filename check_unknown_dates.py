import json

db = json.load(open('hands_database.json', encoding='utf-8'))
unknown_hands = [h for h in db if h.get('date') == 'unknown']
unknown_events = sorted({h['event_id'] for h in unknown_hands})

print(f"Events with 'unknown' date: {len(unknown_events)} events, {len(unknown_hands)} hands")
print(f"Event IDs: {unknown_events}")
print()

# These should be from the January 2026 calendar
# Check the calendar crawler output or pipeline to see what dates they should have
print("These are likely the 01.01.2026 - 23.01.2026 events that were fetched without proper date extraction")
print("We need to re-extract their dates from the vugraph calendar or re-fetch with proper date handling")
