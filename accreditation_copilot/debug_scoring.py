import sqlite3
from pathlib import Path
import re

db_path = Path(__file__).parent / "data" / "metadata.db"
conn = sqlite3.connect(str(db_path))

# Get institution chunks
cursor = conn.execute("SELECT text FROM chunks WHERE source_type='institution' LIMIT 3")
chunks = cursor.fetchall()

print("=== SAMPLE INSTITUTION CHUNKS ===\n")
for i, (text,) in enumerate(chunks, 1):
    print(f"Chunk {i}:")
    print(text[:300])
    print()
    
    # Test patterns
    CURRENCY_PATTERN = re.compile(r'(funding|amount|grant|total):\s*\d+(\.\d+)?\s*(crore|lakh|lakhs|million)|(rs\.?|inr|₹)?\s*\d+(\.\d+)?\s*(crore|lakh|lakhs|million)', re.IGNORECASE)
    PROJECT_COUNT_PATTERN = re.compile(r'(projects?|grants?|proposals?|schemes?):\s*\d+|\d+\s+(projects?|grants?|proposals?|schemes?)', re.IGNORECASE)
    
    currency_matches = CURRENCY_PATTERN.findall(text)
    project_matches = PROJECT_COUNT_PATTERN.findall(text)
    
    print(f"  Currency matches: {len(currency_matches)}")
    print(f"  Project matches: {len(project_matches)}")
    print("-" * 60)

conn.close()
