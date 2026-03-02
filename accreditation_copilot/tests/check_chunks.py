import sqlite3

conn = sqlite3.connect('data/metadata.db')
cursor = conn.cursor()

# Check chunks with criterion 3.2.1 or 3.3.1
cursor.execute('''
    SELECT chunk_id, framework, source, criterion, page, chunk_order, LENGTH(text) as text_len
    FROM chunks 
    WHERE criterion IN ("3.2.1", "3.3.1")
    ORDER BY source, page, chunk_order
''')

print("Chunks with criterion 3.2.1 or 3.3.1:")
print("="*80)
for row in cursor.fetchall():
    print(f"ID: {row[0][:8]}... | Framework: {row[1]} | Source: {row[2][:30]} | Criterion: {row[3]} | Page: {row[4]} | Order: {row[5]} | Text Len: {row[6]}")

# Check if chunk_order exists
cursor.execute("PRAGMA table_info(chunks)")
columns = cursor.fetchall()
print("\n\nDatabase columns:")
print("="*80)
for col in columns:
    print(f"{col[1]}: {col[2]}")

conn.close()
