"""
Quick test to verify institution retrieval is working
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from retrieval.dual_retrieval import DualRetriever
from models.model_manager import get_model_manager

# Initialize
model_manager = get_model_manager()
retriever = DualRetriever(model_manager=model_manager)

# Test query
query = "How can our university move from NAAC B+ to A1?"
query_variants = [query]

# Retrieve
results, inst_available = retriever.retrieve(
    query=query,
    query_variants=query_variants,
    framework="NAAC",
    query_type="metric",
    top_k_framework=3,
    top_k_institution=7
)

print(f"\nInstitution evidence available: {inst_available}")
print(f"Total results: {len(results)}")
print("\nResults breakdown:")

framework_count = 0
institution_count = 0

for i, result in enumerate(results[:10], 1):
    chunk_id = result['chunk_id']
    source_type = result.get('source_type', 'unknown')
    score = result.get('reranker_score', result.get('fused_score', 0))
    
    # Get metadata
    from retrieval.index_loader import IndexLoader
    loader = IndexLoader()
    chunk = loader.get_chunk_metadata(chunk_id)
    
    if chunk:
        source = chunk.get('source', 'unknown')
        page = chunk.get('page', '?')
        text_preview = chunk.get('text', '')[:100]
        
        print(f"\n{i}. Source Type: {source_type}")
        print(f"   Source: {source}, Page: {page}")
        print(f"   Score: {score:.4f}")
        print(f"   Text: {text_preview}...")
        
        if source_type == 'institution':
            institution_count += 1
        else:
            framework_count += 1

print(f"\n\nSummary:")
print(f"Framework chunks: {framework_count}")
print(f"Institution chunks: {institution_count}")
