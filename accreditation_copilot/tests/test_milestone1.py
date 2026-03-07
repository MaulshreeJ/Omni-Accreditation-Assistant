"""
Milestone 1 Validation - Test that framework indexes load from new location.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from retrieval.index_loader import IndexLoader

print("="*80)
print("MILESTONE 1 VALIDATION - INDEX INFRASTRUCTURE")
print("="*80)

try:
    # Initialize index loader
    loader = IndexLoader()
    
    print("\n1. Testing Framework Index Loading...")
    print(f"   Framework index dir: {loader.framework_index_dir}")
    print(f"   Institution index dir: {loader.institution_index_dir}")
    
    # Test loading NAAC metric index
    print("\n2. Loading NAAC metric index...")
    faiss_index, chunk_ids = loader.load_faiss_index('naac_metric')
    print(f"   PASS - Loaded FAISS index with {faiss_index.ntotal} vectors")
    print(f"   PASS - Loaded {len(chunk_ids)} chunk IDs")
    
    # Test loading BM25 index
    print("\n3. Loading NAAC metric BM25 index...")
    bm25, bm25_chunk_ids, tokenized = loader.load_bm25_index('naac_metric')
    print(f"   PASS - Loaded BM25 index")
    print(f"   PASS - Loaded {len(bm25_chunk_ids)} chunk IDs")
    
    # Test loading NBA index
    print("\n4. Loading NBA policy index...")
    faiss_index_nba, chunk_ids_nba = loader.load_faiss_index('nba_policy')
    print(f"   PASS - Loaded FAISS index with {faiss_index_nba.ntotal} vectors")
    print(f"   PASS - Loaded {len(chunk_ids_nba)} chunk IDs")
    
    print("\n" + "="*80)
    print("MILESTONE 1 VALIDATION: PASS")
    print("="*80)
    print("All framework indexes load correctly from new location")
    print("Phase 3 pipeline should work unchanged")
    
except Exception as e:
    print(f"\nMILESTONE 1 VALIDATION: FAIL")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
