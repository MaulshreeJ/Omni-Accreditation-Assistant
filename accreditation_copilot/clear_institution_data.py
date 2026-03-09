import sqlite3
from pathlib import Path
import shutil

# Clear database
db_path = Path(__file__).parent / "data" / "metadata.db"
conn = sqlite3.connect(str(db_path))
cursor = conn.execute("DELETE FROM chunks WHERE source_type='institution'")
deleted = cursor.rowcount
conn.commit()
conn.close()
print(f"Deleted {deleted} institution chunks from database")

# Clear indexes
indexes_dir = Path(__file__).parent / "indexes" / "institution"
if indexes_dir.exists():
    for f in indexes_dir.glob("institution*"):
        f.unlink()
        print(f"Deleted: {f.name}")

# Clear raw_docs except Struggling College
raw_docs = Path(__file__).parent / "data" / "raw_docs"
for f in raw_docs.glob("*.pdf"):
    if "Struggling" not in f.name:
        f.unlink()
        print(f"Deleted: {f.name}")

print("\nReady for fresh ingestion of Struggling College only!")
