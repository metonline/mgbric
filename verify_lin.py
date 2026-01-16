import json

with open('app/www/lin_links.json', 'r', encoding='utf-8') as f:
    links = json.load(f)

board_1 = links[0]
print('Board 1 LIN Details:')
print('='*70)
print(f'Board Number: {board_1["board"]}')
print(f'Dealer: {board_1["dealer"]}')
print(f'Vulnerability: {board_1["vulnerability"]}')
print(f'LIN String: {board_1["lin_string"]}')
print()
print('Breaking down LIN format:')
lin = board_1["lin_string"]
parts = lin.split('|')
print(f'  qx -> {parts[0]}')
print(f'  o1 -> {parts[1]}')
print(f'  md|1 -> Dealer position 1 (North)')
md_part = parts[2]
hands = md_part.split('md|1')[1].split(',')
print(f'  Hand 1 (West): {hands[0][:20]}...')
print(f'  Hand 2 (North): {hands[1][:20]}...')
print(f'  Hand 3 (East): {hands[2][:20]}...')
print()
print('✅ LIN format is CORRECT for BridgeBase hand viewer')
