from event_registry import EventRegistry
from datetime import datetime

registry = EventRegistry()

# Get all dates and filter out 'unknown'
all_dates_raw = list(registry.get_all_events().keys())
all_dates = []

for date in all_dates_raw:
    if date != 'unknown':
        try:
            datetime.strptime(date, "%d.%m.%Y")
            all_dates.append(date)
        except:
            pass

# Sort them
all_dates_sorted = sorted(all_dates, key=lambda x: datetime.strptime(x, "%d.%m.%Y"))

print(f'Total valid events: {len(all_dates_sorted)}')
print(f'Total unknown dates: {all_dates_raw.count("unknown")}')
if all_dates_sorted:
    print(f'First event: {all_dates_sorted[0]}')
    print(f'Latest event: {all_dates_sorted[-1]}')
    print(f'\nFirst 10 events:')
    for date in all_dates_sorted[:10]:
        print(f'  {date}')
    print('  ...')
    print(f'\nLast 10 events:')
    for date in all_dates_sorted[-10:]:
        print(f'  {date}')
