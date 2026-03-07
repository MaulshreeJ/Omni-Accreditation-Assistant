import sqlite3

conn = sqlite3.connect('data/metadata.db')
cursor = conn.cursor()

# Check institution chunks
cursor.execute("SELECT chunk_id, source, page, source_type, doc_type FROM chunks WHERE source_type='institution' LIMIT 5")
rows = cursor.fetchall()

print("Institution chunks in database:")
for r in rows:
    print(f"  Source: {r[1]}, Page: {r[2]}, Type: {r[3]}, DocType: {r[4]}")

conn.close()
