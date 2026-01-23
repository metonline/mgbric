import requests

# Section olmadan test et - otomatik bulması lazım
r = requests.get('http://localhost:5000/api/board-ranking?event=405376&board=1', timeout=120)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")
d = r.json()
results = d.get('results', [])

print('Total:', len(results))
print('NS:', len([x for x in results if x['direction']=='NS']))
print('EW:', len([x for x in results if x['direction']=='EW']))
print('---')

for res in results[:12]:
    print(f"{res.get('rank', '?')}. {res['direction']} {res['pair_names'][:40]} - {res['percent']}%")
