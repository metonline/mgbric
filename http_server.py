#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
import os
import mimetypes

PORT = 8000
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
SERVE_DIR = os.path.join(WORK_DIR, 'app', 'www')

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # Root'u index.html'e yönlendir
        if self.path == '/':
            self.path = '/index.html'
        
        # Normal işlemi yap
        super().do_GET()

os.chdir(SERVE_DIR)

# SO_REUSEADDR: Port'u hemen yeniden kullanabilmek için
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), NoCacheHTTPRequestHandler) as httpd:
    print(f"Web sunucusu basladi: http://localhost:{PORT}")
    print(f"  Veya: http://127.0.0.1:{PORT}")
    print("Cikis icin: Ctrl+C")
    httpd.serve_forever()
