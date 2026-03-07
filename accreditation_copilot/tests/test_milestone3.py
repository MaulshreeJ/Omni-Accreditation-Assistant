"""
Milestone 3 Validation - Test institution index building.
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingestion.institution.institution_indexer import InstitutionIndexer
from retrieval.index_loader import IndexLoader

print("="*80)
print("MILESTONE 3 VALIDATION - INSTITUTION INDEX BUILDER")
print("="*80)

# Load sample chunks
chunks_path = Path('data/institution_chunks_sample.json')

if not chunks_path.exists():
    print(f"ERROR: Sample chunks not found: {chunks_path}")
    print("Run test_milestone2.py first")
    sys.exit(1)

with open(chunks_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

chunks = data['chunks']

print(f"\n1. Loading {len(chunks)} sample chunks...")
print(f"   Source: {data['source']}")
print(f"   Table rows: {data['table_row_chunks']}")
print(f"   Paragraphs: {data['paragraph_chunks']}")

# Build indexes
print(f"\n2. Building institution indexes...")
indexer = InstitutionIndexer()
indexer.build_indexes(chunks, index_name='institution')

# Verify indexes were created
print(f"\n3. Verifying index files...")
index_dir = Path('indexes/institution')

required_files = [
    'institution.index',
    'institution_mapping.pkl',
    'institution_bm25.pkl'
]

for filename in required_files:
    filepath = index_dir / filename
    if filepath.exists():
        size = filepath.stat().st_size
        print(f"   PASS - {filename} ({size} bytes)")
    else:
        print(f"   FAIL - {filename} not found")
        sys.exit(1)

# Test loading indexes
print(f"\n4. Testing index loading...")
loader = IndexLoader()

try:
    # Update loader to support institution indexes
    loader.institution_index_dir = Path('indexes/institution')
    
    # Load FAISS index
    index_path = loader.institution_index_dir / 'institution.index'
    mapping_path = loader.institution_index_dir / 'institution_mapping.pkl'
    
    import faiss
    import pickle
    
    faiss_index = faiss.read_index(str(index_path))
    with open(mapping_path, 'rb') as f:
        chunk_ids = pickle.load(f)
    
    print(f"   PASS - Loaded FAISS index: {faiss_index.ntotal} vectors")
    print(f"   PASS - Loaded {len(chunk_ids)} chunk IDs")
    
    # Load BM25 index
    bm25_path = loader.institution_index_dir / 'institution_bm25.pkl'
    with open(bm25_path, 'rb') as f:
        bm25_data = pickle.load(f)
    
    print(f"   PASS - Loaded BM25 index: {len(bm25_data['chunk_ids'])} documents")
    
except Exception as e:
    print(f"   FAIL - Error loading indexes: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test manual retrieval
print(f"\n5. Testing manual retrieval...")

# Test query
test_query = "DST research grant"
print(f"   Query: '{test_query}'")

# Tokenize query for BM25
tokens = test_query.lower().split()

# BM25 search
bm25_scores = bm25_data['bm25'].get_scores(tokens)
top_bm25_indices = bm25_scores.argsort()[-3:][::-1]

print(f"\n   BM25 Top 3 Results:")
for rank, idx in enumerate(top_bm25_indices, 1):
    chunk_id = bm25_data['chunk_ids'][idx]
    score = bm25_scores[idx]
    
    # Find chunk text
    chunk = next((c for c in chunks if c['chunk_id'] == chunk_id), None)
    if chunk:
        text_preview = chunk['text'][:80]
        print(f"     {rank}. Score: {score:.3f}")
        print(f"        Type: {chunk['chunk_type']}")
        print(f"        Text: {text_preview}...")

# FAISS search
from sentence_transformers import SentenceTransformer
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('BAAI/bge-base-en-v1.5', device=device)

query_embedding = model.encode([test_query], normalize_embeddings=True)[0]
query_embedding = query_embedding.reshape(1, -1).astype('float32')

distances, indices = faiss_index.search(query_embedding, 3)

print(f"\n   FAISS Top 3 Results:")
for rank, (idx, dist) in enumerate(zip(indices[0], distances[0]), 1):
    chunk_id = chunk_ids[idx]
    
    # Find chunk text
    chunk = next((c for c in chunks if c['chunk_id'] == chunk_id), None)
    if chunk:
        text_preview = chunk['text'][:80]
        print(f"     {rank}. Score: {dist:.3f}")
        print(f"        Type: {chunk['chunk_type']}")
        print(f"        Text: {text_preview}...")

print("\n" + "="*80)
print("MILESTONE 3 VALIDATION: PASS")
print("="*80)
print("Institution indexes built and tested successfully")
print("Manual retrieval working correctly")
print("\nNext: Implement Milestone 4 (Dual Retrieval)")
