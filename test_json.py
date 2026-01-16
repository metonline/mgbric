import json

try:
    with open('app/www/hands_database.json', 'r') as f:
        data = json.load(f)
    
    print("OK - JSON valid")
    print(f"Events: {len(data.get('events', {}))}")
    
    for key in list(data['events'].keys())[:1]:
        event = data['events'][key]
        print(f"Event: {event['name']}")
        print(f"Date: {event['date']}")
        print(f"Boards: {len(event.get('boards', {}))}")
        
        for board_key in list(event['boards'].keys())[:1]:
            board = event['boards'][board_key]
            print(f"  Board {board_key}:")
            print(f"    Dealer: {board.get('dealer')}")
            print(f"    Hands: {list(board.get('hands', {}).keys())}")
            hands = board.get('hands', {})
            if 'North' in hands:
                print(f"    North hand: {hands['North']}")
    
except Exception as e:
    print(f"ERROR: {e}")
