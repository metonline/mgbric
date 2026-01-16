#!/usr/bin/env python3
"""
Simple stable server for BBO viewer
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os

class StableHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/hands_database.json' or self.path.startswith('/hands_database.json'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            try:
                with open('hands_database.json', 'rb') as f:
                    self.wfile.write(f.read())
            except Exception as e:
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            super().do_GET()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Log HTTP requests"""
        print(f"[{self.address_string()}] {format % args}")

if __name__ == '__main__':
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, StableHandler)
    print(f'Server running at http://127.0.0.1:{port}')
    print('Press Ctrl+C to stop')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped')
        httpd.server_close()
