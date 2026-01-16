#!/usr/bin/env python3
"""
Inspect the actual HTML structure of Vugraph event results page.
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
    url = "https://clubs.vugraph.com/hosgoru/eventresults.php?event=404377"
    print("Loading event results page...")
    driver.get(url)
    time.sleep(5)
    
    # Get the full page source
    html = driver.page_source
    
    # Look for different table structures
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"Tables found: {len(tables)}")
    
    # Try to find clickable elements containing pair names
    # Check for links, buttons, divs with onclick, etc.
    clickables = driver.find_elements(By.XPATH, "//*[self::a or self::button or self::tr or self::td][@onclick or @href]")
    print(f"Clickable elements (with onclick or href): {len(clickables)}")
    
    # Look specifically for table rows with pair info
    rows = driver.find_elements(By.TAG_NAME, "tr")
    print(f"\nTable rows found: {len(rows)}")
    
    # Inspect first few rows
    print("\nFirst 5 rows content:")
    for i, row in enumerate(rows[:5]):
        cells = row.find_elements(By.TAG_NAME, "td")
        cell_texts = [cell.text.strip() for cell in cells]
        print(f"Row {i}: {cell_texts}")
        
        # Check if any cells have onclick handlers
        for j, cell in enumerate(cells):
            onclick = cell.get_attribute("onclick")
            if onclick:
                print(f"  Cell {j} has onclick: {onclick}")
    
    # Save HTML to file for inspection
    with open("vugraph_page_source.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("\nPage source saved to vugraph_page_source.html")
    
finally:
    driver.quit()
