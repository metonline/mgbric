#!/usr/bin/env python3
"""
Bridgewebs DD Solver'dan DD sonuçlarını çeker
"""

import requests
import re
import json
import time

def fetch_dd_for_event(event_id):
    """Event ID için DD sonuçlarını bridgewebs'den çeker"""
    
    # 1. hands_database.json'dan elleri al
    with open('hands_database.json', 'r', encoding='utf-8') as f:
        hands = json.load(f)
    
    event_hands = [h for h in hands if h.get('event_id') == str(event_id)]
    if not event_hands:
        print(f"Event {event_id} için el bulunamadı")
        return None
    
    print(f"Event {event_id} için {len(event_hands)} el bulundu")
    
    # 2. LIN dosyası oluştur
    lin_content = ''
    for h in sorted(event_hands, key=lambda x: x.get('Board', 0)):
        board = h.get('Board', 1)
        n = h.get('N', '')
        s = h.get('S', '')
        e = h.get('E', '')
        w = h.get('W', '')
        
        dealer_idx = (board - 1) % 4
        vul_cycle = ['o', 'n', 'e', 'b', 'n', 'e', 'b', 'o', 'e', 'b', 'o', 'n', 'b', 'o', 'n', 'e']
        vul_code = vul_cycle[(board - 1) % 16]
        
        lin_content += f'pn|N,E,S,W|st||md|{dealer_idx+1}{n},{e},{s}|sv|{vul_code}|ah|Board {board}|pg||\n'
    
    # 3. Bridgewebs'e yükle
    print("Bridgewebs'e yükleniyor...")
    upload_url = 'https://dds.bridgewebs.com/bridgesolver/upload_file.php'
    files = {'fileToUpload': (f'event_{event_id}.lin', lin_content, 'text/plain')}
    data = {'edit': '0'}
    
    response = requests.post(upload_url, files=files, data=data, timeout=120)
    if response.status_code != 200:
        print(f"Yükleme hatası: {response.status_code}")
        return None
    
    # Dosya adını çıkar
    match = re.search(r'filename="([^"]+)"', response.text)
    if not match:
        print("Dosya adı bulunamadı")
        return None
    
    filename = match.group(1).replace('//dds.bridgewebs.com/bridgesolver/uploads/', '')
    print(f"Yüklenen dosya: {filename}")
    
    # 4. DD hesaplama için bekle ve sonuçları al
    # Doğrudan XML/JSON formatında DD verisi almayı dene
    time.sleep(2)
    
    # ddummy sayfasını al
    page_url = f'https://dds.bridgewebs.com/bsol2/ddummy.htm?club=bsol_site&file=https://dds.bridgewebs.com/bridgesolver/uploads/{filename}'
    print(f"DD sayfası yükleniyor: {page_url}")
    
    # Bu sayfayı tarayıcıda açmak gerekiyor çünkü DD hesaplama JavaScript ile yapılıyor
    print(f"\nDD sonuçları için bu sayfayı tarayıcıda açın:")
    print(page_url)
    print("\nSonra 'Download JSON' veya 'Export' butonuna tıklayın.")
    
    return page_url

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        event_id = sys.argv[1]
    else:
        event_id = '405376'
    
    fetch_dd_for_event(event_id)
