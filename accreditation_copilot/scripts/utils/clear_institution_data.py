import sqlite3
from pathlib import Path

# Clear institution chunks from database
conn = sqlite3.connect('data/metadata.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM chunks WHERE source_type='institution'")
conn.commit()
print(f'Deleted {cursor.rowcount} institution chunks from database')
conn.close()

# Delete institution index files
index_dir = Path('indexes/institution')
if index_dir.exists():
    for file in index_dir.glob('*'):
        file.unlink()
        print(f'Deleted {file}')
    print('Institution indexes cleared')
else:
    print('No institution index directory found')

print('\nNow run: python ingestion/institution/run_institution_ingestion.py')
