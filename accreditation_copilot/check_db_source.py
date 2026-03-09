import sqlite3

conn = sqlite3.connect('data/metadata.db')
cursor = conn.cursor()

cursor.execute('SELECT DISTINCT source FROM chunks WHERE source_type="institution"')
sources = cursor.fetchall()

print("Institution PDFs in database:")
for (source,) in sources:
    print(f"  - {source}")

cursor.execute('SELECT COUNT(*) FROM chunks WHERE source_type="institution"')
count = cursor.fetchone()[0]
print(f"\nTotal institution chunks: {count}")

conn.close()
