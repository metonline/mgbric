import json

data = json.load(open('hands_database.json'))
h = [x for x in data if x['date']=='20.01.2026' and x['board']==1][0]

print('Current in DB:')
print(f'N: {h["N"]}')
print(f'E: {h["E"]}')
print(f'S: {h["S"]}')
print(f'W: {h["W"]}')
print()
print('Correct should be:')
print('N: K86.QJT7.AQT.832')
print('E: 975.A53.KJ93.J76')
print('S: T42.2.8542.KQT54')
print('W: AQJ3.K9864.76.A9')
