#!/usr/bin/env python3
"""
Inspect boarddetails page HTML to find where contract info is stored.
"""

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Navigate to a specific board details page for Pair 9 (EMINE/RABIA) on Board 1
    url = "https://clubs.vugraph.com/hosgoru/boarddetails.php?event=404377&section=A&pair=9&direction=NS&board=1"
    print(f"Loading: {url}\n")
    driver.get(url)
    time.sleep(2)
    
    # Get page source
    html = driver.page_source
    
    # Save to file for analysis
    with open("boarddetails_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    # Print relevant sections
    print("Page text content:")
    print("=" * 80)
    body_text = driver.find_element("tag name", "body").text
    print(body_text[:2000])
    print("=" * 80)
    
    print("\nFile saved to boarddetails_page.html for detailed inspection")
    
finally:
    driver.quit()
