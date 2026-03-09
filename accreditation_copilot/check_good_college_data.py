import sqlite3

conn = sqlite3.connect('data/metadata.db')
cursor = conn.cursor()

cursor.execute('SELECT text FROM chunks WHERE source_type="institution" AND source="Good_College_B+_SSR.pdf" LIMIT 3')
chunks = cursor.fetchall()

print("Good College B+ chunks:\n")
for i, (text,) in enumerate(chunks, 1):
    print(f"Chunk {i}:")
    print(f"  {text[:200]}")
    print()

conn.close()
