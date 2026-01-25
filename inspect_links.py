#!/usr/bin/env python3
"""
Inspect event 405596 page to find all links
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

opts = Options()
opts.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=opts)

try:
    # Event 405596
    driver.get('https://clubs.vugraph.com/hosgoru/eventresults.php?event=405596')
    time.sleep(3)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Get all links
    links = soup.find_all('a')
    
    print(f"Found {len(links)} links on event page:\n")
    
    for i, link in enumerate(links[:30]):  # First 30 links
        href = link.get('href', 'NO HREF')
        text = link.get_text(strip=True)[:50]
        print(f"[{i}] {text:50} -> {href[:70]}")

finally:
    driver.quit()
