"""
Test NBA C5 (Faculty) retrieval precision.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from retrieval.retrieval_pipeline import RetrievalPipeline


def main():
    print("=" * 80)
    print("NBA C5 FACULTY RETRIEVAL TEST")
    print("=" * 80)
    print()
    
    pipeline = RetrievalPipeline()
    
    query = "What are the NBA Tier-II faculty requirements for Criterion 5?"
    
    print(f"Query: {query}")
    print()
    
    # Run async retrieval
    import asyncio
    results = asyncio.run(pipeline.run_retrieval(query))
    
    print("=" * 80)
    print("TOP-5 RESULTS")
    print("=" * 80)
    print()
    
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. [{result['framework']}] {result['source']} (Page {result['page']})")
        print(f"   Type: {result['doc_type']}, Criterion: {result.get('criterion', 'None')}")
        print(f"   Reranker Score: {result.get('reranker_score', 0):.3f}")
        text = result.get('expanded_text', result.get('text', ''))
        print(f"   Text: {text[:150]}...")
        print()
    
    # Check if C5 is at rank 1
    if results and results[0].get('criterion') == 'C5':
        print("[PASS] C5 at rank 1")
    else:
        print(f"[FAIL] C5 not at rank 1. Got: {results[0].get('criterion') if results else 'No results'}")


if __name__ == "__main__":
    main()
