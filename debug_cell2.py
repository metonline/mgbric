import requests
from bs4 import BeautifulSoup
import re

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=404377&section=A&pair=1&direction=NS&board=7'
response = requests.get(url, timeout=10)
response.encoding = 'ISO-8859-9'

soup = BeautifulSoup(response.text, 'html.parser')
cells = soup.find_all('td', {'class': 'oyuncu'})

print("Cell 2 (East) HTML:")
print(str(cells[2]))
