#!/usr/bin/env python3
"""
Inspect pair summary page to understand structure.
"""

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Load a pair summary page
    url = "https://clubs.vugraph.com/hosgoru/pairsummary.php?event=404377&section=A&pair=9&direction=NS"
    print(f"Loading: {url}\n")
    driver.get(url)
    time.sleep(3)
    
    # Get page content
    body_text = driver.find_element("tag name", "body").text
    
    print("Page content (first 1500 chars):")
    print("=" * 80)
    print(body_text[:1500])
    print("=" * 80)
    
    # Save full HTML for inspection
    with open("pair_summary_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    
    print("\nFull HTML saved to pair_summary_page.html")
    
finally:
    driver.quit()
