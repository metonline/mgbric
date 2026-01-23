"""Tek bir event için board results fetch et"""
import json
from fetch_all_board_results import get_event_info, fetch_pair_result
import sys

def fetch_event(event_id, max_boards=27):
    print(f'Fetching event {event_id}...')
    
    # Event bilgilerini al
    info = get_event_info(event_id)
    print(f'NS pairs: {info["ns_pairs"]}, EW pairs: {info["ew_pairs"]}')
    
    # Mevcut board_results'ı yükle
    with open('board_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Her board için sonuçları topla
    added = 0
    for board_num in range(1, max_boards + 1):
        board_key = f'{event_id}_{board_num}'
        results = []
        
        # NS pair'leri fetch et
        for pair_num in range(1, info['ns_pairs'] + 1):
            result = fetch_pair_result(event_id, board_num, pair_num, 'NS', 'A', info.get('ns_pair_names'))
            if result:
                results.append(result)
        
        # EW pair'leri fetch et
        for pair_num in range(1, info['ew_pairs'] + 1):
            result = fetch_pair_result(event_id, board_num, pair_num, 'EW', 'A', info.get('ew_pair_names'))
            if result:
                results.append(result)
        
        if results:
            data['boards'][board_key] = {'results': results}
            added += 1
            print(f'  Board {board_num}: {len(results)} results')
    
    # Kaydet
    with open('board_results.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f'\nAdded {added} boards for event {event_id}')
    print(f'Total boards now: {len(data["boards"])}')

if __name__ == '__main__':
    event_id = sys.argv[1] if len(sys.argv) > 1 else '404498'
    fetch_event(event_id)
