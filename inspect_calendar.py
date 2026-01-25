#!/usr/bin/env python3
"""
Inspect calendar page structure
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

opts = Options()
opts.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=opts)

try:
    driver.get('https://clubs.vugraph.com/hosgoru/calendar.php')
    time.sleep(5)
    
    # Save to file to inspect
    with open('calendar_page.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    
    print(f"✅ Calendar page saved to calendar_page.html ({len(driver.page_source)} bytes)")
    
    # Print first 3000 chars
    print("\n=== Page Structure ===")
    print(driver.page_source[:3000])

finally:
    driver.quit()
