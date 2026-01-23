"""
Board sonuçlarını analiz edip oyuncu sıralaması çıkarır.
fetch_all_board_results.py çalıştırıldıktan sonra kullanılır.
"""

import json
from collections import defaultdict
from datetime import datetime

def load_results():
    """board_results.json'dan verileri yükle"""
    with open('board_results.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_players(data, min_boards=10):
    """
    Oyuncu bazında analiz yap
    Her oyuncunun her boarddaki yüzdesini topla ve ortalama al
    """
    player_stats = defaultdict(lambda: {
        'boards': [],
        'total_percent': 0,
        'board_count': 0,
        'events': set(),
        'partners': set(),
        'best_boards': [],
        'worst_boards': []
    })
    
    for board_key, board_data in data.get('boards', {}).items():
        event_id = board_data.get('event_id', '')
        board_num = board_data.get('board', 0)
        date = board_data.get('date', '')
        
        for result in board_data.get('results', []):
            pair_names = result.get('pair_names', '')
            percent = result.get('percent', 0)
            direction = result.get('direction', '')
            contract = result.get('contract', '')
            rank = result.get('rank', 0)
            
            if not pair_names or ' - ' not in pair_names:
                continue
            
            # İki oyuncuyu ayır
            players = pair_names.split(' - ')
            if len(players) != 2:
                continue
            
            player1, player2 = players[0].strip(), players[1].strip()
            
            board_info = {
                'event_id': event_id,
                'board': board_num,
                'date': date,
                'percent': percent,
                'direction': direction,
                'contract': contract,
                'rank': rank,
                'partner': player2
            }
            
            # Player 1
            player_stats[player1]['boards'].append(board_info)
            player_stats[player1]['total_percent'] += percent
            player_stats[player1]['board_count'] += 1
            player_stats[player1]['events'].add(event_id)
            player_stats[player1]['partners'].add(player2)
            
            # Player 2
            board_info2 = board_info.copy()
            board_info2['partner'] = player1
            player_stats[player2]['boards'].append(board_info2)
            player_stats[player2]['total_percent'] += percent
            player_stats[player2]['board_count'] += 1
            player_stats[player2]['events'].add(event_id)
            player_stats[player2]['partners'].add(player1)
    
    # Ortalama hesapla ve best/worst bul
    rankings = []
    for player, stats in player_stats.items():
        if stats['board_count'] < min_boards:
            continue
        
        avg = stats['total_percent'] / stats['board_count']
        
        # En iyi ve en kötü boardları bul
        sorted_boards = sorted(stats['boards'], key=lambda x: x['percent'], reverse=True)
        best = sorted_boards[:3]
        worst = sorted_boards[-3:]
        
        rankings.append({
            'player': player,
            'average': avg,
            'board_count': stats['board_count'],
            'event_count': len(stats['events']),
            'partner_count': len(stats['partners']),
            'best_boards': best,
            'worst_boards': worst
        })
    
    # Ortalamaya göre sırala
    rankings.sort(key=lambda x: x['average'], reverse=True)
    
    return rankings

def analyze_pairs(data, min_boards=5):
    """
    Çift bazında analiz yap
    """
    pair_stats = defaultdict(lambda: {
        'boards': [],
        'total_percent': 0,
        'board_count': 0,
        'events': set()
    })
    
    for board_key, board_data in data.get('boards', {}).items():
        event_id = board_data.get('event_id', '')
        board_num = board_data.get('board', 0)
        date = board_data.get('date', '')
        
        for result in board_data.get('results', []):
            pair_names = result.get('pair_names', '')
            percent = result.get('percent', 0)
            
            if not pair_names:
                continue
            
            # Çift ismini normalize et (alfabetik sırala)
            if ' - ' in pair_names:
                players = sorted(pair_names.split(' - '))
                pair_key = ' - '.join(players)
            else:
                pair_key = pair_names
            
            pair_stats[pair_key]['boards'].append({
                'event_id': event_id,
                'board': board_num,
                'date': date,
                'percent': percent
            })
            pair_stats[pair_key]['total_percent'] += percent
            pair_stats[pair_key]['board_count'] += 1
            pair_stats[pair_key]['events'].add(event_id)
    
    rankings = []
    for pair, stats in pair_stats.items():
        if stats['board_count'] < min_boards:
            continue
        
        avg = stats['total_percent'] / stats['board_count']
        rankings.append({
            'pair': pair,
            'average': avg,
            'board_count': stats['board_count'],
            'event_count': len(stats['events'])
        })
    
    rankings.sort(key=lambda x: x['average'], reverse=True)
    return rankings

def print_player_rankings(rankings, top_n=20):
    """Oyuncu sıralamasını yazdır"""
    print("\n" + "="*80)
    print("OYUNCU SIRALAMASI (Board Bazında Ortalama)")
    print("="*80)
    print(f"{'Sıra':<5} {'Oyuncu':<35} {'Ort %':<8} {'Board':<7} {'Turnuva':<8}")
    print("-"*80)
    
    for i, r in enumerate(rankings[:top_n], 1):
        print(f"{i:<5} {r['player'][:34]:<35} {r['average']:.2f}%  {r['board_count']:<7} {r['event_count']:<8}")

def print_pair_rankings(rankings, top_n=20):
    """Çift sıralamasını yazdır"""
    print("\n" + "="*80)
    print("ÇİFT SIRALAMASI (Board Bazında Ortalama)")
    print("="*80)
    print(f"{'Sıra':<5} {'Çift':<50} {'Ort %':<8} {'Board':<7}")
    print("-"*80)
    
    for i, r in enumerate(rankings[:top_n], 1):
        print(f"{i:<5} {r['pair'][:49]:<50} {r['average']:.2f}%  {r['board_count']:<7}")

def save_rankings(player_rankings, pair_rankings, output_file='player_rankings.json'):
    """Sıralamaları JSON olarak kaydet"""
    output = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'player_rankings': player_rankings,
        'pair_rankings': pair_rankings
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\nSonuçlar {output_file} dosyasına kaydedildi.")

def main():
    print("Board sonuçları yükleniyor...")
    data = load_results()
    
    board_count = len(data.get('boards', {}))
    event_count = len(data.get('events', {}))
    
    print(f"Yüklendi: {board_count} board, {event_count} turnuva")
    print(f"Son güncelleme: {data.get('last_updated', 'N/A')}")
    
    if board_count == 0:
        print("Henüz veri yok! Önce fetch_all_board_results.py çalıştırın.")
        return
    
    print("\nOyuncu analizi yapılıyor...")
    player_rankings = analyze_players(data, min_boards=10)
    print(f"  {len(player_rankings)} oyuncu (min 10 board)")
    
    print("Çift analizi yapılıyor...")
    pair_rankings = analyze_pairs(data, min_boards=5)
    print(f"  {len(pair_rankings)} çift (min 5 board)")
    
    print_player_rankings(player_rankings, top_n=30)
    print_pair_rankings(pair_rankings, top_n=20)
    
    save_rankings(player_rankings, pair_rankings)

if __name__ == '__main__':
    main()
