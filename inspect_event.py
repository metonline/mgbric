#!/usr/bin/env python3
"""
Check one event page structure
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

opts = Options()
opts.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=opts)

try:
    # Check event 405596 which we know has hands
    driver.get('https://clubs.vugraph.com/hosgoru/eventresults.php?event=405596')
    time.sleep(5)
    
    # Save HTML
    with open('event_405596.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    
    print(f"✅ Event page saved ({len(driver.page_source)} bytes)")
    
    # Show first part
    print("\n=== First 4000 chars ===")
    print(driver.page_source[:4000])

finally:
    driver.quit()
