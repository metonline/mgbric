import requests
from bs4 import BeautifulSoup
import re

url = 'https://clubs.vugraph.com/hosgoru/calendar.php?month=1&year=2026'
print(f"Fetching: {url}")

r = requests.get(url, timeout=10)
r.encoding = 'utf-8'

soup = BeautifulSoup(r.text, 'html.parser')

# Check for table
table = soup.find('table')
print(f"Table found: {table is not None}")
if table:
    print(f"Table rows: {len(table.find_all('tr'))}")

# Count event links
event_links = r.text.count('eventresults.php')
print(f"eventresults.php links in page: {event_links}")

# Extract event IDs
events = []
for link in soup.find_all('a', href=True):
    match = re.search(r'event=(\d+)', link['href'])
    if match:
        events.append(match.group(1))

print(f"Event IDs found: {len(set(events))}")
print(f"Unique events: {sorted(set(events))}")
