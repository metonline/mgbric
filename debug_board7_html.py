import requests
from bs4 import BeautifulSoup

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=404377&section=A&pair=1&direction=NS&board=7'
response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')
cells = soup.find_all('td', class_='oyuncu')

print('Cell 0 (North) full HTML:')
print(str(cells[0])[:1500])
