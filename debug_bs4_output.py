import requests
from bs4 import BeautifulSoup
import re

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=404377&section=A&pair=1&direction=NS&board=7'
response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')
cells = soup.find_all('td', class_='oyuncu')

# Get the HTML string that BeautifulSoup returns
html_from_bs = str(cells[0])
print("HTML from BeautifulSoup:")
print(repr(html_from_bs))

print("\n\nActual length:", len(html_from_bs))

# Try to extract just the suit images and cards manually
import re
matches = re.findall(r'<img[^>]*alt="([^"]+)"[^>]*/>([^<]*)', html_from_bs)
print("\n\nMatches with flexible pattern:")
print(matches)
