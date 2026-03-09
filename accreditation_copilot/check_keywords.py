import sqlite3

conn = sqlite3.connect('data/metadata.db')
cursor = conn.cursor()

cursor.execute('SELECT text FROM chunks WHERE source_type="institution" LIMIT 3')
chunks = cursor.fetchall()

print(f"Found {len(chunks)} chunks\n")

for i, (text,) in enumerate(chunks, 1):
    text_lower = text.lower()
    print(f"Chunk {i}:")
    print(f"  Has 'inr': {'inr' in text_lower}")
    print(f"  Has 'lakhs': {'lakhs' in text_lower}")
    print(f"  Has 'projects': {'projects' in text_lower}")
    print(f"  Has 'dst': {'dst' in text_lower}")
    print(f"  Has 'serb': {'serb' in text_lower}")
    print(f"  Text sample: {text[:200]}")
    print()

conn.close()
