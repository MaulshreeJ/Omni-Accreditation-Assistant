import sqlite3

conn = sqlite3.connect('data/metadata.db')
cursor = conn.cursor()

cursor.execute('SELECT criterion, COUNT(*) FROM chunks GROUP BY criterion LIMIT 10')
print('Criterion distribution:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

cursor.execute('SELECT text FROM chunks WHERE framework="NAAC" LIMIT 1')
row = cursor.fetchone()
if row:
    print('\nSample NAAC chunk text:')
    print(row[0][:500])

conn.close()
