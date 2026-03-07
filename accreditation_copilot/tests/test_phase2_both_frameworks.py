"""
Phase 2 Complete Test - Both NAAC and NBA
Tests retrieval precision for both frameworks.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from retrieval.retrieval_pipeline import RetrievalPipeline


async def test_naac_query():
    """Test NAAC 3.2.1 query."""
    print("\n" + "="*80)
    print("TEST 1: NAAC 3.2.1 QUERY")
    print("="*80)
    
    pipeline = RetrievalPipeline()
    query = "What are the requirements for NAAC 3.2.1?"
    
    print(f"\nQuery: {query}")
    results = await pipeline.run_retrieval(query, verbose=False)
    
    print("\nTOP-5 RESULTS:")
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. [{result['framework']}] {result['source']} (Page {result['page']})")
        reranker_score = result.get('scores', {}).get('reranker', 0.0)
        print(f"   Criterion: {result.get('criterion', 'None')}, Reranker: {reranker_score:.3f}")
    
    # Check if 3.2.1 at rank 1
    if results and results[0].get('criterion') == '3.2.1':
        print("\n[PASS] NAAC 3.2.1 at rank 1")
        return True
    else:
        print(f"\n[FAIL] NAAC 3.2.1 not at rank 1. Got: {results[0].get('criterion') if results else 'No results'}")
        return False


async def test_nba_query():
    """Test NBA C5 query."""
    print("\n" + "="*80)
    print("TEST 2: NBA C5 (FACULTY) QUERY")
    print("="*80)
    
    pipeline = RetrievalPipeline()
    query = "What are the NBA Tier-II faculty requirements for Criterion 5?"
    
    print(f"\nQuery: {query}")
    results = await pipeline.run_retrieval(query, verbose=False)
    
    print("\nTOP-5 RESULTS:")
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. [{result['framework']}] {result['source']} (Page {result['page']})")
        reranker_score = result.get('scores', {}).get('reranker', 0.0)
        print(f"   Criterion: {result.get('criterion', 'None')}, Reranker: {reranker_score:.3f}")
    
    # Check if C5 at rank 1
    if results and results[0].get('criterion') == 'C5':
        print("\n[PASS] NBA C5 at rank 1")
        return True
    else:
        print(f"\n[FAIL] NBA C5 not at rank 1. Got: {results[0].get('criterion') if results else 'No results'}")
        return False


async def main():
    """Run both tests."""
    print("\n" + "="*80)
    print("PHASE 2 COMPLETE TEST - BOTH FRAMEWORKS")
    print("="*80)
    
    naac_pass = await test_naac_query()
    nba_pass = await test_nba_query()
    
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    print(f"NAAC 3.2.1 Test: {'PASS' if naac_pass else 'FAIL'}")
    print(f"NBA C5 Test: {'PASS' if nba_pass else 'FAIL'}")
    
    if naac_pass and nba_pass:
        print("\n[PASS] ALL TESTS PASSED")
        print("Phase 2 precision working for both NAAC and NBA")
    else:
        print("\n[FAIL] Some tests failed")
    
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
