"""
Phase 2 Test Script
Tests the complete retrieval pipeline.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from retrieval.retrieval_pipeline import RetrievalPipeline


async def test_retrieval():
    """Test retrieval pipeline with sample queries."""
    
    pipeline = RetrievalPipeline()
    
    test_queries = [
        {
            'query': "Are we compliant with NAAC 3.2.1?",
            'expected_framework': 'NAAC',
            'expected_type': 'metric'
        },
        {
            'query': "What are the minimum faculty requirements for NBA Tier-II?",
            'expected_framework': 'NBA',
            'expected_type': 'prequalifier'
        },
        {
            'query': "How long is NBA accreditation valid?",
            'expected_framework': 'NBA',
            'expected_type': 'policy'
        }
    ]
    
    print("="*80)
    print("PHASE 2 - RETRIEVAL PIPELINE TEST")
    print("="*80)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}")
        print(f"{'='*80}")
        
        query = test_case['query']
        
        try:
            results = await pipeline.run_retrieval(query, verbose=True)
            
            # Validation
            print(f"\n{'='*80}")
            print(f"VALIDATION")
            print(f"{'='*80}")
            
            if results:
                print(f"✓ Retrieved {len(results)} results")
                
                # Check framework
                frameworks = set(r['framework'] for r in results)
                print(f"✓ Frameworks: {frameworks}")
                
                # Check scores
                has_reranker = all('reranker' in r['scores'] for r in results)
                print(f"✓ Reranker scores present: {has_reranker}")
                
                # Check sorting
                reranker_scores = [r['scores']['reranker'] for r in results]
                is_sorted = all(reranker_scores[i] >= reranker_scores[i+1] 
                               for i in range(len(reranker_scores)-1))
                print(f"✓ Results sorted by reranker: {is_sorted}")
                
                # Check metadata
                has_metadata = all(
                    r.get('source') and r.get('page') and r.get('text')
                    for r in results
                )
                print(f"✓ Full metadata present: {has_metadata}")
                
                print(f"\n✓ TEST CASE {i} PASSED")
            else:
                print(f"✗ No results returned")
                print(f"✗ TEST CASE {i} FAILED")
                
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            print(f"✗ TEST CASE {i} FAILED")
            import traceback
            traceback.print_exc()
    
    pipeline.close()
    
    print(f"\n{'='*80}")
    print(f"PHASE 2 TEST COMPLETE")
    print(f"{'='*80}")


if __name__ == "__main__":
    asyncio.run(test_retrieval())
