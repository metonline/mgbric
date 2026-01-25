import json

db = json.load(open('hands_database.json', encoding='utf-8'))
dates = sorted({h.get('date') for h in db})

print("Current database dates:")
for date in dates:
    hands_for_date = [h for h in db if h.get('date') == date]
    events_for_date = sorted({h['event_id'] for h in hands_for_date})
    print(f"  {date}: {len(events_for_date)} events, {len(hands_for_date)} hands")
    if len(events_for_date) <= 5:
        print(f"    Events: {events_for_date}")
