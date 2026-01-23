import requests

try:
    r = requests.get('http://localhost:5000/api/hand-data?event=405315&board=1', timeout=10)
    print('Status:', r.status_code)
    print('Content-Type:', r.headers.get('Content-Type'))
    print('Body:', r.text[:500])
except Exception as e:
    print('Error:', e)
