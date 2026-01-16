#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

event_id = 403999
url = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}"

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    # Save raw HTML for inspection
    with open('event_403999.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Search for "Doğu" or "Batı" text anywhere on page
    body = soup.find('body')
    body_text = body.get_text()
    
    if 'Doğu' in body_text or 'Batı' in body_text:
        print("✓ Page contains Doğu-Batı text")
        
        # Find where it appears
        idx = body_text.find('Doğu')
        if idx == -1:
            idx = body_text.find('Batı')
        
        context = body_text[max(0, idx-100):idx+100]
        print(f"Context: ...{context}...")
    else:
        print("✗ Page does NOT contain Doğu-Batı text")
    
    # Look for all divs, sections, spans
    print("\n=== Looking for Doğu/Batı in specific elements ===")
    for element in soup.find_all(['div', 'section', 'span', 'h1', 'h2', 'h3', 'h4', 'p']):
        text = element.get_text(strip=True)
        if 'Doğu' in text or 'Batı' in text:
            print(f"{element.name}: {text[:100]}")
    
    print("\n✓ Raw HTML saved to event_403999.html")

except Exception as e:
    print(f"Error: {e}")
