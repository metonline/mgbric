#!/usr/bin/env python3
"""
Quick test to inspect Vugraph page structure with Selenium.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Load page
    url = "https://clubs.vugraph.com/hosgoru/eventresults.php?event=404377"
    print(f"Loading: {url}")
    driver.get(url)
    time.sleep(5)
    
    # Get page title
    print(f"Page title: {driver.title}")
    
    # Try to find pair-related elements
    links = driver.find_elements(By.TAG_NAME, "a")
    print(f"\nTotal links on page: {len(links)}")
    
    # Filter for pair-related links
    pair_links = [l for l in links if "pair" in l.get_attribute("href").lower()]
    print(f"Pair-related links: {len(pair_links)}")
    
    if pair_links:
        print("\nFirst 5 pair links:")
        for link in pair_links[:5]:
            href = link.get_attribute("href")
            text = link.text.strip()
            print(f"  Text: '{text}' -> {href}")
    
    # Check for iframes
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"\nIframes on page: {len(iframes)}")
    
    # Check body content
    body_text = driver.find_element(By.TAG_NAME, "body").text
    print(f"\nBody text length: {len(body_text)}")
    print("Body text (first 500 chars):")
    print(body_text[:500])
    
finally:
    driver.quit()
