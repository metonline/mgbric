#!/usr/bin/env python3
"""
Auto-restarting Flask development server with cleanup
Handles port conflicts gracefully and auto-restarts on failures
"""
import os
import sys
import time
import subprocess
import signal
import socket
from pathlib import Path

def is_port_available(port):
    """Check if port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0

def find_available_port(start_port=5000):
    """Find next available port"""
    port = start_port
    while not is_port_available(port):
        port += 1
    return port

def kill_existing_server(port):
    """Kill any existing server on port"""
    try:
        # Windows
        os.system(f'netstat -ano | findstr :{port}')
        os.system(f'taskkill /f /im python.exe 2>nul')
        time.sleep(1)
    except:
        pass

def run_server():
    """Run Flask server with auto-restart"""
    os.chdir(Path(__file__).parent)
    
    port = 5000
    kill_existing_server(port)
    
    if not is_port_available(port):
        port = find_available_port(port)
    
    os.environ['PORT'] = str(port)
    
    print(f"\n{'='*60}")
    print(f"[SERVER] Bridge Hands Development Server")
    print(f"{'='*60}")
    print(f"[OK] Port: {port}")
    print(f"[OK] URL: http://localhost:{port}/hands_bbo_view.html")
    print(f"[OK] Press CTRL+C to stop")
    print(f"{'='*60}\n")
    
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            # Run Flask app
            result = subprocess.run([
                sys.executable, 'app.py'
            ], capture_output=False, text=True)
            
            if result.returncode == 0:
                print("[OK] Server stopped cleanly")
                break
            else:
                print(f"[ERROR] Server crashed (exit code {result.returncode})")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"  Restarting... (attempt {retry_count}/{max_retries})")
                    time.sleep(2)
                else:
                    print(f"[ERROR] Max retries reached. Giving up.")
                    break
        except KeyboardInterrupt:
            print("\n[OK] Server stopped by user")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"  Retrying in 2 seconds...")
                time.sleep(2)

if __name__ == '__main__':
    run_server()
