"""
Vugraph ortak yardımcı fonksiyonlar.
Tüm vugraph işlemleri için tek kaynak (DRY prensibi).
"""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://clubs.vugraph.com/hosgoru"
REQUEST_TIMEOUT = 15


def parse_contract_cell(cell):
    """Kontrat hücresini parse et"""
    text = cell.get_text(strip=True)
    imgs = cell.find_all('img')
    for img in imgs:
        alt = img.get('alt', '')
        if alt == 'S':
            text = text.replace('', '♠')
        elif alt == 'H':
            text = text.replace('', '♥')
        elif alt == 'D':
            text = text.replace('', '♦')
        elif alt == 'C':
            text = text.replace('', '♣')
    suit_map = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
    for code, symbol in suit_map.items():
        if code in text:
            text = text.replace(code, symbol)
    return text


def parse_lead_cell(cell):
    """Atak hücresini parse et"""
    text = cell.get_text(strip=True)
    imgs = cell.find_all('img')
    suit_map = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
    for img in imgs:
        alt = img.get('alt', '')
        if alt in suit_map:
            text = text.replace(alt, suit_map[alt])
    for code, symbol in suit_map.items():
        if code in text:
            text = text.replace(code, symbol)
    return text


def get_event_info(event_id):
    """
    Turnuva bilgilerini, çift sayısını ve pair isimlerini al.
    
    Returns:
        dict: {
            'name': str,
            'date': str,
            'ns_pairs': int,
            'ew_pairs': int,
            'ns_pair_names': {pair_num: "Player1 - Player2"},
            'ew_pair_names': {pair_num: "Player1 - Player2"}
        }
    """
    try:
        url = f'{BASE_URL}/eventresults.php?event={event_id}'
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Turnuva adı ve tarihi
        tournament_name = ""
        tournament_date = ""
        h3 = soup.find('h3')
        if h3:
            h3_text = h3.get_text(strip=True)
            date_match = re.search(r'(\d{2})-(\d{2})-(\d{4})', h3_text)
            if date_match:
                day, month, year = date_match.groups()
                tournament_date = f"{day}.{month}.{year}"
            parts = h3_text.split()
            if parts:
                tournament_name = parts[0]
        
        # Turnuva adı h1'den de alınabilir
        if not tournament_name:
            h1 = soup.find('h1')
            if h1:
                tournament_name = h1.get_text(strip=True)
        
        # NS ve EW çiftlerini ve isimlerini bul
        ns_pairs = {}  # {pair_num: "Player1 - Player2"}
        ew_pairs = {}
        
        # colored tablosunu bul
        table = soup.find('table', class_='colored')
        if table:
            rows = table.find_all('tr')
            
            # İlk satırdan format belirle
            header_row = rows[0] if rows else None
            header_text = header_row.get_text(strip=True) if header_row else ""
            
            # Format 1: "Masa | Kuzey - Güney | IMP | Doğu - Batı" (IMP turnuvaları)
            if 'Masa' in header_text and 'Kuzey' in header_text and 'Doğu' in header_text:
                for row in rows[1:]:  # Header'ı atla
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        masa_num = cells[0].get_text(strip=True)
                        if masa_num.isdigit():
                            pair_num = int(masa_num)
                            ns_name = cells[1].get_text(strip=True)
                            ew_name = cells[3].get_text(strip=True)
                            if ns_name:
                                ns_pairs[pair_num] = ns_name
                            if ew_name:
                                ew_pairs[pair_num] = ew_name
            
            # Format 2: "Sıra/Rank" ile ayrı NS ve EW bölümleri (MP turnuvaları)
            else:
                in_ns = False
                in_ew = False
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if not cells:
                        continue
                    
                    first_text = cells[0].get_text(strip=True)
                    
                    # Bölüm başlığı mı?
                    if 'Kuzey' in first_text or 'North' in first_text:
                        in_ns = True
                        in_ew = False
                        continue
                    elif 'Doğu' in first_text or 'East' in first_text:
                        in_ew = True
                        in_ns = False
                        continue
                    elif first_text in ['Sıra', 'Rank']:
                        continue
                    
                    # Veri satırı mı?
                    if len(cells) >= 3 and first_text.isdigit():
                        pair_num = int(first_text)
                        # 2. hücre: "Player1 - Player2" formatında
                        pair_name = cells[1].get_text(strip=True)
                        
                        if in_ns:
                            ns_pairs[pair_num] = pair_name
                        elif in_ew:
                            ew_pairs[pair_num] = pair_name
        
        return {
            'name': tournament_name,
            'date': tournament_date,
            'ns_pairs': len(ns_pairs) if ns_pairs else 13,
            'ew_pairs': len(ew_pairs) if ew_pairs else 13,
            'ns_pair_names': ns_pairs,
            'ew_pair_names': ew_pairs
        }
    except Exception as e:
        print(f"    Event info error: {e}")
        return {
            'name': '', 
            'date': '', 
            'ns_pairs': 13, 
            'ew_pairs': 13, 
            'ns_pair_names': {}, 
            'ew_pair_names': {}
        }


def fetch_board_all_results(event_id, board_num, event_info=None):
    """
    Bir board'un TÜM sonuçlarını tek sayfadan çeker.
    Her satır bir masa sonucunu temsil eder.
    
    Args:
        event_id: Turnuva ID
        board_num: Board numarası  
        event_info: get_event_info() sonucu (opsiyonel)
    
    Returns:
        list: [{'direction': 'NS'/'EW', 'contract': ..., 'score': ..., 'percent': ...}, ...]
    """
    try:
        url = f'{BASE_URL}/boarddetails.php?event={event_id}&section=A&pair=1&direction=NS&board={board_num}'
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        if 'Page not Found' in resp.text:
            return []
        
        results_table = soup.find('table', class_='results')
        if not results_table:
            return []
        
        rows = results_table.find_all('tr')
        all_results = []
        table_num = 0
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 8:
                continue
            
            # Header/caption satırlarını atla
            first_text = cells[0].get_text(strip=True)
            if first_text in ['K - G', 'D - B', 'Kontrat', '']:
                continue
            
            # results class'ı olan satırlar veri satırı
            first_cell_class = cells[0].get('class', [])
            if 'results' not in first_cell_class and 'fantastic' not in first_cell_class:
                continue
            
            table_num += 1
            
            contract = parse_contract_cell(cells[0])
            if not contract:
                continue
            
            declarer = cells[1].get_text(strip=True)
            result_text = cells[2].get_text(strip=True)
            lead = parse_lead_cell(cells[3])
            
            # Kolonlar: [Kontrat, Dek, Sonuç, Atak, Skor K-G, Skor D-B, % K-G, % D-B]
            score_ns = cells[4].get_text(strip=True) if not cells[4].find('img') else ''
            score_ew = cells[5].get_text(strip=True) if not cells[5].find('img') else ''
            pct_str = cells[6].get_text(strip=True) if not cells[6].find('img') else ''
            
            try:
                pct_ns = float(pct_str) if pct_str else None
            except ValueError:
                pct_ns = None
            
            if pct_ns is None:
                continue
            
            # NS sonucu
            ns_score = score_ns if score_ns else (f"-{score_ew}" if score_ew else '0')
            all_results.append({
                'direction': 'NS',
                'table_num': table_num,
                'pair_names': f'Masa {table_num} NS',
                'contract': contract,
                'declarer': declarer,
                'result': result_text,
                'lead': lead,
                'score': ns_score,
                'percent': pct_ns
            })
            
            # EW sonucu (100 - NS%)
            ew_score = score_ew if score_ew else (f"-{score_ns}" if score_ns else '0')
            all_results.append({
                'direction': 'EW',
                'table_num': table_num,
                'pair_names': f'Masa {table_num} EW',
                'contract': contract,
                'declarer': declarer,
                'result': result_text,
                'lead': lead,
                'score': ew_score,
                'percent': round(100 - pct_ns, 2)
            })
        
        # NS ve EW ayrı ayrı yüzdeye göre sırala ve rank ekle
        ns_results = [r for r in all_results if r['direction'] == 'NS']
        ew_results = [r for r in all_results if r['direction'] == 'EW']
        
        ns_results.sort(key=lambda x: x.get('percent', 0), reverse=True)
        ew_results.sort(key=lambda x: x.get('percent', 0), reverse=True)
        
        for i, r in enumerate(ns_results):
            r['rank'] = i + 1
        for i, r in enumerate(ew_results):
            r['rank'] = i + 1
        
        return ns_results + ew_results
        
    except Exception as e:
        print(f"    fetch_board_all_results error: {e}")
        return []


def _fetch_single_pair_result(event_id, board_num, pair_num, direction, pair_names_dict):
    """
    Tek bir pair'in board sonucunu çeker (kullanılmıyor, referans için).
    """
    pass


def fetch_pair_result(event_id, board_num, pair_num, direction, section='A', pair_names_dict=None):
    """
    Bir çift için board sonucunu çeker.
    NS için section=A, EW için section=B kullanılır.
    EW için D-B kolonundan yüzde okunur.
    
    Args:
        event_id: Turnuva ID
        board_num: Board numarası
        pair_num: Çift numarası
        direction: 'NS' veya 'EW'
        section: Bölüm (kullanılmıyor, direction'a göre otomatik belirlenir)
        pair_names_dict: Çift isimleri sözlüğü
    
    Returns:
        dict veya None
    """
    try:
        # NS için section=A, EW için section=B kullan
        actual_section = 'A' if direction == 'NS' else 'B'
        url = f'{BASE_URL}/boarddetails.php?event={event_id}&section={actual_section}&pair={pair_num}&direction={direction}&board={board_num}'
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Page not found kontrolü
        if 'Page not Found' in resp.text or 'Sayfa Bulunamadı' in resp.text:
            return None
        
        # Pair ismini h3'ten al
        pair_names = ""
        h3 = soup.find('h3')
        if h3:
            h3_text = h3.get_text(strip=True)
            match = re.search(r'\d{2}:\d{2}\s*\.\.\.\s*(.+?)\s*\.\.\.\s*(?:Bord|Masa)', h3_text)
            if match:
                pair_names = match.group(1).strip()
        
        # h3'te bulunamazsa dict'ten al
        if not pair_names and pair_names_dict and pair_num in pair_names_dict:
            pair_names = pair_names_dict[pair_num]
        
        if not pair_names:
            return None
        
        # Highlighted satırı bul
        results_table = soup.find('table', class_='results')
        if not results_table:
            return None
        
        rows = results_table.find_all('tr')
        if not rows:
            return None
        
        # Format belirleme
        first_row_cells = rows[0].find_all('td')
        first_header = first_row_cells[0].get_text(strip=True) if first_row_cells else ''
        
        # IMP Format
        if first_header == 'Atak':
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    cell_class = cells[0].get('class', [''])[0] if cells[0].get('class') else ''
                    if cell_class in ['fantastic', 'resultspecial', 'resultsimportant']:
                        score_ns = ''
                        imp = ''
                        
                        for c in cells:
                            txt = c.get_text(strip=True)
                            if txt and txt.replace('.','').replace('-','').isdigit():
                                if '.' in txt:
                                    imp = txt
                                elif not score_ns:
                                    score_ns = txt
                        
                        if score_ns:
                            if direction == 'NS':
                                return {
                                    'pair_names': pair_names,
                                    'direction': 'NS',
                                    'contract': '-',
                                    'declarer': '-',
                                    'result': '-',
                                    'lead': '-',
                                    'score': score_ns,
                                    'percent': float(imp) if imp else 0
                                }
                            elif direction == 'EW':
                                return {
                                    'pair_names': pair_names,
                                    'direction': 'EW',
                                    'contract': '-',
                                    'declarer': '-',
                                    'result': '-',
                                    'lead': '-',
                                    'score': f"-{score_ns}" if score_ns else '',
                                    'percent': -float(imp) if imp else 0
                                }
            return None
        
        # MP Format
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 7:
                cell_class = cells[0].get('class', [''])[0] if cells[0].get('class') else ''
                if cell_class in ['fantastic', 'resultspecial', 'resultsimportant']:
                    contract = parse_contract_cell(cells[0])
                    if not contract or contract in ['-6', '-', '']:
                        return None
                    
                    declarer = cells[1].get_text(strip=True)
                    result_text = cells[2].get_text(strip=True)
                    
                    if len(cells) >= 8:
                        lead = parse_lead_cell(cells[3])
                        score_ns = cells[4].get_text(strip=True) if not cells[4].find('img') else ''
                        score_ew = cells[5].get_text(strip=True) if not cells[5].find('img') else ''
                        pct_ns_str = cells[6].get_text(strip=True) if not cells[6].find('img') else ''
                        pct_ew_str = cells[7].get_text(strip=True) if not cells[7].find('img') else ''
                    else:
                        lead = ''
                        score_ns = cells[3].get_text(strip=True) if not cells[3].find('img') else ''
                        score_ew = cells[4].get_text(strip=True) if not cells[4].find('img') else ''
                        pct_ns_str = cells[5].get_text(strip=True) if not cells[5].find('img') else ''
                        pct_ew_str = cells[6].get_text(strip=True) if not cells[6].find('img') else ''
                    
                    pct_ns = float(pct_ns_str) if pct_ns_str else 0
                    
                    if direction == 'NS':
                        if score_ns:
                            return {
                                'pair_names': pair_names,
                                'direction': 'NS',
                                'contract': contract,
                                'declarer': declarer,
                                'result': result_text,
                                'lead': lead,
                                'score': score_ns,
                                'percent': pct_ns
                            }
                        elif score_ew:
                            return {
                                'pair_names': pair_names,
                                'direction': 'NS',
                                'contract': contract,
                                'declarer': declarer,
                                'result': result_text,
                                'lead': lead,
                                'score': f"-{score_ew}",
                                'percent': pct_ns
                            }
                    elif direction == 'EW':
                        # EW için D-B kolonundan direkt yüzde oku
                        pct_ew = float(pct_ew_str) if pct_ew_str else 0
                        if score_ew:
                            return {
                                'pair_names': pair_names,
                                'direction': 'EW',
                                'contract': contract,
                                'declarer': declarer,
                                'result': result_text,
                                'lead': lead,
                                'score': score_ew,
                                'percent': pct_ew
                            }
                        elif score_ns:
                            return {
                                'pair_names': pair_names,
                                'direction': 'EW',
                                'contract': contract,
                                'declarer': declarer,
                                'result': result_text,
                                'lead': lead,
                                'score': f"-{score_ns}",
                                'percent': pct_ew
                            }
        return None
    except Exception as e:
        return None
