import requests
from bs4 import BeautifulSoup
import re

def get_all_pairs(event_id):
    """eventresults.php'den tüm çiftleri al"""
    url = f'https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}'
    r = requests.get(url, timeout=10)
    r.encoding = 'iso-8859-9'
    soup = BeautifulSoup(r.content, 'html.parser')
    
    pairs = {'NS': [], 'EW': []}
    current_direction = None
    
    # Tablo satırlarını tara
    for row in soup.find_all('tr'):
        text = row.get_text(strip=True)
        if 'Kuzey - Güney' in text:
            current_direction = 'NS'
            continue
        if 'Doğu - Batı' in text:
            current_direction = 'EW'
            continue
        
        if current_direction:
            cells = row.find_all('td')
            if len(cells) >= 3:
                try:
                    rank = int(cells[0].get_text(strip=True))
                    names = cells[1].get_text(strip=True)
                    score = cells[2].get_text(strip=True)
                    pairs[current_direction].append({
                        'rank': rank,
                        'names': names,
                        'score': score
                    })
                except:
                    pass
    
    return pairs

def get_board_results(event_id, board_num, section='A'):
    """boarddetails.php'den bir board için tüm sonuçları al"""
    # Herhangi bir çift için sayfayı al (pair=1)
    url = f'https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section={section}&pair=1&direction=NS&board={board_num}'
    r = requests.get(url, timeout=10)
    r.encoding = 'iso-8859-9'
    soup = BeautifulSoup(r.content, 'html.parser')
    
    results = []
    
    # Sonuç tablosunu bul (ikinci tablo genelde)
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            # 8 hücreli satırlar sonuç satırları
            if len(cells) == 8:
                cls = cells[0].get('class', [])
                if 'results' in cls or 'fantastic' in cls:
                    contract = cells[0].get_text(strip=True)
                    declarer = cells[1].get_text(strip=True)
                    result = cells[2].get_text(strip=True)
                    lead = cells[3].get_text(strip=True)
                    score_ns = cells[4].get_text(strip=True)
                    score_ew = cells[5].get_text(strip=True)
                    pct_ns = cells[6].get_text(strip=True)
                    pct_ew = cells[7].get_text(strip=True)
                    
                    results.append({
                        'contract': contract,
                        'declarer': declarer,
                        'result': result,
                        'lead': lead,
                        'score_ns': score_ns,
                        'score_ew': score_ew,
                        'pct_ns': pct_ns,
                        'pct_ew': pct_ew
                    })
    
    return results

# Test
event_id = 405278
print("=== TÜM ÇİFTLER ===")
pairs = get_all_pairs(event_id)
print(f"NS: {len(pairs['NS'])} çift")
for p in pairs['NS'][:3]:
    print(f"  {p['rank']}. {p['names']}")
print(f"EW: {len(pairs['EW'])} çift")
for p in pairs['EW'][:3]:
    print(f"  {p['rank']}. {p['names']}")

print("\n=== BOARD 1 SONUÇLARI ===")
results = get_board_results(event_id, 1)
print(f"Toplam {len(results)} sonuç")
for r in results[:5]:
    print(f"  {r['contract']} {r['declarer']} {r['result']} - NS:{r['score_ns']}({r['pct_ns']}%) EW:{r['score_ew']}({r['pct_ew']}%)")
