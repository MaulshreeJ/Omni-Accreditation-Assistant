"""
Check what fields are in retrieval results
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
query = "What are the requirements for NAAC A+?"
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

print(f"\nTotal results: {len(results)}")
print(f"Institution available: {inst_available}")

if results:
    print("\n=== FIRST RESULT FIELDS ===")
    first = results[0]
    for key in sorted(first.keys()):
        value = first[key]
        if isinstance(value, str) and len(value) > 100:
            print(f"{key}: {value[:100]}...")
        else:
            print(f"{key}: {value}")
    
    # Check institution results
    inst_results = [r for r in results if r.get('source_type') == 'institution']
    print(f"\n=== INSTITUTION RESULTS: {len(inst_results)} ===")
    if inst_results:
        inst = inst_results[0]
        print(f"Has child_text: {'child_text' in inst}")
        print(f"Has text: {'text' in inst}")
        print(f"Has parent_context: {'parent_context' in inst}")
        if 'child_text' in inst:
            print(f"child_text length: {len(inst['child_text'])}")
            print(f"child_text preview: {inst['child_text'][:200]}")
