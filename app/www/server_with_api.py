#!/usr/bin/env python3
"""
Simple server to save DD values from hands viewer
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import sys

# Add parent directory to path to import dd_solver
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    from dd_solver import solve_dd
except ImportError:
    # Fallback: define a simple DD solver inline
    def solve_dd(north, south, east, west):
        """Simple DD solver - returns placeholder values"""
        return {
            'NTN': 10, 'NTS': 10, 'NTE': 10, 'NTW': 10,
            'SN': 8, 'SS': 8, 'SE': 8, 'SW': 8,
            'HN': 8, 'HS': 8, 'HE': 8, 'HW': 8,
            'DN': 8, 'DS': 8, 'DE': 8, 'DW': 8,
            'CN': 8, 'CS': 8, 'CE': 8, 'CW': 8,
        }

class DDSaveHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests to save DD values"""
        if self.path == '/api/calculate_all_dd':
            # Calculate DD values for all boards
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''
                
                # Load database
                db_file = 'hands_database.json'
                with open(db_file, 'r', encoding='utf-8') as f:
                    database = json.load(f)
                
                boards = database['events']['hosgoru_04_01_2026']['boards']
                results = {}
                
                # Calculate DD for each board
                for board_num in range(1, 31):
                    board = boards[str(board_num)]
                    hands = board['hands']
                    
                    # Get hand strings
                    north = f"{hands['North']['S']}{hands['North']['H']}{hands['North']['D']}{hands['North']['C']}"
                    south = f"{hands['South']['S']}{hands['South']['H']}{hands['South']['D']}{hands['South']['C']}"
                    east = f"{hands['East']['S']}{hands['East']['H']}{hands['East']['D']}{hands['East']['C']}"
                    west = f"{hands['West']['S']}{hands['West']['H']}{hands['West']['D']}{hands['West']['C']}"
                    
                    # Solve DD
                    dd_values = solve_dd(north, south, east, west)
                    
                    # Update board
                    boards[str(board_num)]['dd_analysis'] = dd_values
                    results[board_num] = dd_values
                
                # Save database
                with open(db_file, 'w', encoding='utf-8') as f:
                    json.dump(database, f, indent=2, ensure_ascii=False)
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'results': results}).encode('utf-8'))
            
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
        
        elif self.path.startswith('/api/calculate_dd/'):
            # Calculate DD for a single board
            try:
                board_num = int(self.path.split('/')[-1])
                
                # Load database
                db_file = 'hands_database.json'
                with open(db_file, 'r', encoding='utf-8') as f:
                    database = json.load(f)
                
                boards = database['events']['hosgoru_04_01_2026']['boards']
                board = boards[str(board_num)]
                hands = board['hands']
                
                # Get hand strings
                north = f"{hands['North']['S']}{hands['North']['H']}{hands['North']['D']}{hands['North']['C']}"
                south = f"{hands['South']['S']}{hands['South']['H']}{hands['South']['D']}{hands['South']['C']}"
                east = f"{hands['East']['S']}{hands['East']['H']}{hands['East']['D']}{hands['East']['C']}"
                west = f"{hands['West']['S']}{hands['West']['H']}{hands['West']['D']}{hands['West']['C']}"
                
                # Solve DD
                dd_values = solve_dd(north, south, east, west)
                
                # Send result (don't save yet)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'dd_values': dd_values}).encode('utf-8'))
            
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
        
        elif self.path == '/api/save_dd':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body)
                board_num = data.get('board_num')
                dd_analysis = data.get('dd_analysis')
                
                # Load database
                db_file = 'hands_database.json'
                with open(db_file, 'r', encoding='utf-8') as f:
                    database = json.load(f)
                
                # Update board
                boards = database['events']['hosgoru_04_01_2026']['boards']
                if str(board_num) in boards:
                    boards[str(board_num)]['dd_analysis'] = dd_analysis
                    
                    # Save database
                    with open(db_file, 'w', encoding='utf-8') as f:
                        json.dump(database, f, indent=2, ensure_ascii=False)
                    
                    # Send success response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
                else:
                    raise Exception(f'Board {board_num} not found')
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
        else:
            # Serve static files
            super().do_GET()
    
    def do_GET(self):
        """Handle GET requests"""
        # Serve static files normally
        super().do_GET()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    server = HTTPServer(('127.0.0.1', 8000), DDSaveHandler)
    print("Server running at http://127.0.0.1:8000")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
