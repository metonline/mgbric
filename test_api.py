import requests
r = requests.get('http://localhost:5000/api/board-ranking?event=405315&board=1', timeout=90)
d = r.json()
results = d.get('results', [])
print('Total:', len(results))
print('NS:', len([x for x in results if x.get('direction') == 'NS']))
print('EW:', len([x for x in results if x.get('direction') == 'EW']))
print('First 5 results:')
for r in results[:5]:
    print(f"  {r.get('rank')}. {r.get('direction')} {r.get('pair_names','')[:30]} - {r.get('percent')}%")
