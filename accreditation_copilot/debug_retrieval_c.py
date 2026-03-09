"""
Debug retrieval for C grade PDF
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from retrieval.dual_retrieval import DualRetriever

print("="*60)
print("DEBUGGING RETRIEVAL FOR C GRADE PDF")
print("="*60)

# Initialize retriever
retriever = DualRetriever()

# Test query for criterion 3.2.1
query = "research projects funding grants sponsored research financial support external funding agencies government funding industry collaboration research expenditure"
query_variants = [
    query,
    "number of research projects with funding",
    "external funding for research"
]

print(f"\nQuery: {query[:100]}...")

# Retrieve using dual retrieval
print("\n1. Retrieving using dual retrieval...")
framework_results, institution_available = retriever.retrieve(
    query=query,
    query_variants=query_variants,
    framework='NAAC',
    query_type='metric',
    top_k_framework=5,
    top_k_institution=10
)

print(f"   Institution evidence available: {institution_available}")
print(f"   Total results: {len(framework_results)}")

# Filter to institution chunks only
institution_results = [r for r in framework_results if r.get('source_type') == 'institution']
print(f"   Institution chunks: {len(institution_results)}")

if institution_results:
    print("\n2. Institution results:")
    for i, result in enumerate(institution_results[:5], 1):
        print(f"\n   Result {i}:")
        print(f"   - Chunk ID: {result.get('chunk_id', 'unknown')}")
        print(f"   - Source type: {result.get('source_type', 'unknown')}")
        print(f"   - Dense score: {result.get('dense_score', 0.0):.3f}")
        print(f"   - Fused score: {result.get('fused_score', 0.0):.3f}")
        
        # Check if text is loaded
        if 'text' in result:
            print(f"   - Text length: {len(result['text'])} chars")
            print(f"   - Text preview: {result['text'][:150]}...")
        elif 'child_text' in result:
            print(f"   - Child text length: {len(result['child_text'])} chars")
            print(f"   - Text preview: {result['child_text'][:150]}...")
        else:
            print(f"   - ⚠️ NO TEXT LOADED")
else:
    print("\n❌ NO INSTITUTION RESULTS RETRIEVED!")
    print("   This means the retrieval system is not finding the institution chunks.")
    print("   Possible causes:")
    print("   - Institution index not built properly")
    print("   - Query doesn't match chunk content")
    print("   - Chunks too short for embedding")
    print("   - Embedding model not capturing semantic meaning")

print("\n" + "="*60)
