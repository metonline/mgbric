import os
import sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
SERVE_DIR = os.path.join(WORK_DIR, 'app', 'www')

print(f"WORK_DIR: {WORK_DIR}")
print(f"SERVE_DIR: {SERVE_DIR}")
print(f"SERVE_DIR exists: {os.path.exists(SERVE_DIR)}")
print(f"index.html exists: {os.path.exists(os.path.join(SERVE_DIR, 'index.html'))}")

# List files in SERVE_DIR
if os.path.exists(SERVE_DIR):
    files = os.listdir(SERVE_DIR)
    print(f"Files in SERVE_DIR: {len(files)}")
    print("First 5 files:", files[:5])
