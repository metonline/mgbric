#!/usr/bin/env python3
"""
Try accessing Vugraph data via different approaches:
1. Direct JSON API if available
2. Different URL patterns
3. Check what the actual working event URL structure is
"""

import requests
import json
from bs4 import BeautifulSoup

print("\n" + "="*70)
print("VUGRAPH DATA FETCH - DIRECT HTTP APPROACH")
print("="*70 + "\n")

# Try direct requests (no Selenium, just HTTP)
base_url = "https://clubs.vugraph.com/hosgoru"
event_id = 404377

urls_to_test = [
    # Event API endpoints
    f"{base_url}/api/event/{event_id}",
    f"{base_url}/api/event/{event_id}/boards",
    f"{base_url}/api/boards/{event_id}",
    
    # Direct page requests
    f"{base_url}/eventresults.php?event={event_id}",
    f"{base_url}/boards.php?event={event_id}",
    f"{base_url}/event.php?id={event_id}",
    
    # Board-specific
    f"{base_url}/api/board/{event_id}/1",
    f"{base_url}/api/board/1",
    
    # Try JSON endpoints
    f"{base_url}/data.php?event={event_id}",
    f"{base_url}/json/event/{event_id}",
]

for url in urls_to_test:
    try:
        print(f"Testing: {url[:60]}...")
        
        response = requests.get(url, timeout=5)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            print(f"  Content-Type: {content_type}")
            
            if 'json' in content_type:
                data = response.json()
                print(f"  ✓ JSON Response: {type(data)} with keys: {list(data.keys())[:5]}")
                if isinstance(data, dict):
                    print(f"    Sample: {json.dumps(data, default=str)[:200]}")
            else:
                # Check if it's HTML with content
                if len(response.text) > 1000:
                    print(f"  ✓ HTML Response: {len(response.text)} chars")
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Look for data in common places
                    scripts = soup.find_all('script')
                    if scripts:
                        print(f"    Found {len(scripts)} script tags")
                        for script in scripts[:1]:
                            content = script.string[:200] if script.string else ""
                            if content:
                                print(f"    Script content: {content}...")
                else:
                    print(f"  Response: {response.text[:200]}")
        else:
            print(f"  ✗ Failed")
        
        print()
    
    except Exception as e:
        print(f"  ✗ Error: {e}\n")

print("="*70)
print("TESTING COMPLETE")
print("="*70 + "\n")

# Also try to see if we can download the entire event page
print("\nDownloading full event page...")
try:
    response = requests.get(f"{base_url}/eventresults.php?event={event_id}", timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Size: {len(response.text)} bytes")
    
    # Save to file for inspection
    with open('vugraph_event_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("✓ Saved to: vugraph_event_page.html")
    
    # Quick analysis
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for tables
    tables = soup.find_all('table')
    print(f"\nFound {len(tables)} tables")
    
    # Look for links
    links = soup.find_all('a', href=True)
    pair_links = [l for l in links if 'pairsummary' in l.get('href', '')]
    board_links = [l for l in links if 'boarddetails' in l.get('href', '')]
    
    print(f"Pair summary links: {len(pair_links)}")
    print(f"Board details links: {len(board_links)}")
    
    if pair_links:
        print(f"\nSample pair link: {pair_links[0].get('href')[:80]}")
    
    # Look for inline data (JSON, etc)
    scripts = soup.find_all('script')
    print(f"\nFound {len(scripts)} script tags")
    
    for i, script in enumerate(scripts):
        content = script.string or ""
        if 'board' in content.lower() or 'hand' in content.lower():
            print(f"\nScript {i} contains board/hand data:")
            print(content[:300])

except Exception as e:
    print(f"Error downloading: {e}")
