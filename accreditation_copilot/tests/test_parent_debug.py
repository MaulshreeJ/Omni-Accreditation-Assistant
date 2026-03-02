"""
Debug script to understand why siblings aren't being added.
"""

import sqlite3
from pathlib import Path

# Connect to database
db_path = Path("data/metadata.db")
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get chunks for NAAC 3.3.1 (the top result from test)
cursor.execute('''
    SELECT chunk_id, text, page, criterion, chunk_order, LENGTH(text) as text_len
    FROM chunks 
    WHERE framework = 'NAAC' 
    AND source = 'NAAC_SSR_Manual_Universities.pdf'
    AND criterion = '3.3.1'
    ORDER BY page, chunk_order
''')

chunks_3_3_1 = cursor.fetchall()

print("="*80)
print("Chunks with criterion 3.3.1:")
print("="*80)
for chunk in chunks_3_3_1:
    print(f"Page: {chunk['page']}, Order: {chunk['chunk_order']}, Text Len: {chunk['text_len']}, ID: {chunk['chunk_id'][:8]}...")

# Get all chunks from the same parent section (3.3)
cursor.execute('''
    SELECT chunk_id, text, page, criterion, chunk_order, LENGTH(text) as text_len
    FROM chunks 
    WHERE framework = 'NAAC' 
    AND source = 'NAAC_SSR_Manual_Universities.pdf'
    AND page BETWEEN 63 AND 67
    ORDER BY page, chunk_order
''')

parent_chunks = cursor.fetchall()

print("\n" + "="*80)
print("All chunks in parent section 3.3 (or nearby pages):")
print("="*80)
for i, chunk in enumerate(parent_chunks):
    marker = " <-- TARGET" if chunk['chunk_id'] == chunks_3_3_1[0]['chunk_id'] else ""
    crit = chunk['criterion'] if chunk['criterion'] else 'NULL'
    print(f"{i:2d}. Page: {chunk['page']:3d}, Order: {chunk['chunk_order']:2d}, Criterion: {crit:>6s}, Text Len: {chunk['text_len']:4d}, ID: {chunk['chunk_id'][:8]}...{marker}")

# Simulate token estimation
def estimate_tokens(text):
    return int(len(text.split()) * 1.3)

# Find target chunk index
target_id = chunks_3_3_1[0]['chunk_id']
target_idx = None
for i, chunk in enumerate(parent_chunks):
    if chunk['chunk_id'] == target_id:
        target_idx = i
        break

if target_idx is not None:
    print("\n" + "="*80)
    print(f"Sibling Expansion Simulation (target at index {target_idx}):")
    print("="*80)
    
    target_chunk = parent_chunks[target_idx]
    target_tokens = estimate_tokens(target_chunk['text'])
    print(f"Target chunk tokens: {target_tokens}")
    
    # Try adding before
    if target_idx > 0:
        before_chunk = parent_chunks[target_idx - 1]
        before_tokens = estimate_tokens(before_chunk['text'])
        combined_tokens = target_tokens + before_tokens
        print(f"\nBefore sibling (index {target_idx-1}):")
        print(f"  Tokens: {before_tokens}")
        print(f"  Combined: {combined_tokens} ({'OK' if combined_tokens <= 1200 else 'EXCEEDS LIMIT'})")
    
    # Try adding after
    if target_idx < len(parent_chunks) - 1:
        after_chunk = parent_chunks[target_idx + 1]
        after_tokens = estimate_tokens(after_chunk['text'])
        combined_tokens = target_tokens + after_tokens
        print(f"\nAfter sibling (index {target_idx+1}):")
        print(f"  Tokens: {after_tokens}")
        print(f"  Combined: {combined_tokens} ({'OK' if combined_tokens <= 1200 else 'EXCEEDS LIMIT'})")

conn.close()
