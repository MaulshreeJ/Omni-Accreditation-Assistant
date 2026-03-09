"""
Debug script to check why Struggling_College_C_SSR.pdf shows 0% confidence
"""
import sqlite3
from pathlib import Path

# Connect to database
db_path = Path(__file__).parent / "data" / "metadata.db"
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("="*60)
print("DEBUGGING C GRADE PDF - 0% CONFIDENCE ISSUE")
print("="*60)

# Check if institution chunks exist
cursor.execute("SELECT COUNT(*) FROM chunks WHERE source_type='institution'")
count = cursor.fetchone()[0]
print(f"\n1. Total institution chunks in database: {count}")

if count == 0:
    print("\n❌ NO INSTITUTION CHUNKS FOUND!")
    print("   The PDF was not ingested properly.")
    print("   Solution: Re-upload and re-ingest the PDF")
    conn.close()
    exit()

# Check chunk content
cursor.execute("""
    SELECT chunk_id, text
    FROM chunks 
    WHERE source_type='institution' 
    LIMIT 5
""")
chunks = cursor.fetchall()

print(f"\n2. Sample chunks from database:")
for i, (chunk_id, text) in enumerate(chunks, 1):
    print(f"\n   Chunk {i}:")
    print(f"   - ID: {chunk_id}")
    print(f"   - Text length: {len(text)} chars")
    print(f"   - Text preview: {text[:200]}...")

# Check for research-related keywords
cursor.execute("""
    SELECT chunk_id, text 
    FROM chunks 
    WHERE source_type='institution'
    AND (
        LOWER(text) LIKE '%research%'
        OR LOWER(text) LIKE '%project%'
        OR LOWER(text) LIKE '%funding%'
        OR LOWER(text) LIKE '%grant%'
    )
""")
research_chunks = cursor.fetchall()

print(f"\n3. Chunks with research keywords: {len(research_chunks)}")
if research_chunks:
    for i, (chunk_id, text) in enumerate(research_chunks[:3], 1):
        print(f"\n   Research chunk {i}:")
        print(f"   - ID: {chunk_id}")
        print(f"   - Text: {text[:300]}...")

# Check for numeric data (SQLite doesn't support REGEXP by default, use LIKE)
cursor.execute("""
    SELECT chunk_id, text 
    FROM chunks 
    WHERE source_type='institution'
    AND (text LIKE '%0%' OR text LIKE '%1%' OR text LIKE '%2%' OR text LIKE '%3%' 
         OR text LIKE '%4%' OR text LIKE '%5%' OR text LIKE '%6%' OR text LIKE '%7%'
         OR text LIKE '%8%' OR text LIKE '%9%')
    LIMIT 5
""")
numeric_chunks = cursor.fetchall()

print(f"\n4. Chunks with numeric data: {len(numeric_chunks)}")
if numeric_chunks:
    for i, (chunk_id, text) in enumerate(numeric_chunks[:3], 1):
        print(f"\n   Numeric chunk {i}:")
        print(f"   - ID: {chunk_id}")
        print(f"   - Text: {text[:300]}...")

conn.close()

print("\n" + "="*60)
print("NEXT STEPS:")
print("="*60)
print("1. If no chunks found → Re-upload and re-ingest the PDF")
print("2. If chunks exist but no research keywords → PDF content is too vague")
print("3. If chunks exist with keywords → Check retrieval system")
