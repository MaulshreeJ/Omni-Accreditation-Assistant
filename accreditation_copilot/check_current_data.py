import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "data" / "metadata.db"
conn = sqlite3.connect(str(db_path))

# Check what institution files are in the database
cursor = conn.execute("SELECT source, COUNT(*) as count FROM chunks WHERE source_type='institution' GROUP BY source")
print("Current institution chunks in database:")
for row in cursor:
    print(f"  {row[0]}: {row[1]} chunks")

# Get a sample chunk to see the content
cursor = conn.execute("SELECT text FROM chunks WHERE source_type='institution' LIMIT 1")
sample = cursor.fetchone()
if sample:
    print(f"\nSample text (first 200 chars):")
    print(sample[0][:200])

conn.close()
