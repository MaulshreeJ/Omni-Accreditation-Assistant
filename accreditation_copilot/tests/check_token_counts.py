"""
Check actual token counts vs character lengths.
"""

import sqlite3
from pathlib import Path
from transformers import AutoTokenizer

# Load BGE tokenizer
print("Loading BGE tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-base-en-v1.5")

# Connect to database
db_path = Path("data/metadata.db")
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get chunks for NAAC 3.3.1
cursor.execute('''
    SELECT chunk_id, text, page, criterion, chunk_order, LENGTH(text) as char_len
    FROM chunks 
    WHERE framework = 'NAAC' 
    AND source = 'NAAC_SSR_Manual_Universities.pdf'
    AND page BETWEEN 63 AND 67
    ORDER BY page, chunk_order
''')

chunks = cursor.fetchall()

print("\n" + "="*80)
print("Token counts for chunks on pages 63-67:")
print("="*80)
print(f"{'Page':<6} {'Order':<6} {'Criterion':<10} {'Chars':<8} {'Tokens':<8} {'Est.Tokens':<12}")
print("-"*80)

for chunk in chunks:
    actual_tokens = len(tokenizer.encode(chunk['text'], add_special_tokens=False))
    estimated_tokens = int(len(chunk['text'].split()) * 1.3)
    crit = chunk['criterion'] if chunk['criterion'] else 'NULL'
    print(f"{chunk['page']:<6} {chunk['chunk_order']:<6} {crit:<10} {chunk['char_len']:<8} {actual_tokens:<8} {estimated_tokens:<12}")

conn.close()
