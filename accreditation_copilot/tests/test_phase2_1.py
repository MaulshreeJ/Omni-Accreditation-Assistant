"""
Phase 2.1 Test Script
Tests retrieval precision improvements.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from retrieval.retrieval_pipeline import RetrievalPipeline


async def test_phase2_1():
    """Test Phase 2.1 improvements."""
    
    pipeline = RetrievalPipeline()
    
    test_cases = [
        {
            'name': 'Test 1: Explicit NAAC Metric',
            'query': "Are we compliant with NAAC 3.2.1?",
            'expected_criterion': '3.2.1',
            'expected_framework': 'NAAC',
            'check': 'Top-5 must contain chunk with criterion = 3.2.1'
        },
        {
            'name': 'Test 2: NBA Prequalifier',
            'query': "What are the minimum faculty requirements for NBA Tier-II?",
            'expected_framework': 'NBA',
            'expected_types': ['prequalifier', 'metric'],
            'check': 'Results from NBA only, no NAAC chunks'
        },
        {
            'name': 'Test 3: NBA Policy',
            'query': "How long is NBA accreditation valid?",
            'expected_framework': 'NBA',
            'expected_type': 'policy',
            'check': 'Policy chunk from NBA General Manual'
        }
    ]
    
    print("="*80)
    print("PHASE 2.1 - RETRIEVAL PRECISION TEST")
    print("="*80)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"{test_case['name']}")
        print(f"{'='*80}")
        print(f"Query: {test_case['query']}")
        print(f"Expected: {test_case['check']}\n")
        
        try:
            results = await pipeline.run_retrieval(test_case['query'], verbose=True)
            
            # Validation
            print(f"\n{'='*80}")
            print(f"VALIDATION")
            print(f"{'='*80}")
            
            if not results:
                print(f"[FAIL] No results returned")
                all_passed = False
                continue
            
            # Check reranker score range
            reranker_scores = [r['scores']['reranker'] for r in results]
            min_score = min(reranker_scores)
            max_score = max(reranker_scores)
            print(f"Reranker score range: [{min_score:.3f}, {max_score:.3f}]")
            
            if min_score >= 0 and max_score <= 1:
                print(f"[OK] Reranker scores normalized (0-1 range)")
            else:
                print(f"[FAIL] Reranker scores NOT normalized")
                all_passed = False
            
            # Test-specific validation
            if test_case['name'] == 'Test 1: Explicit NAAC Metric':
                # Check if any result has criterion 3.2.1
                has_exact_match = any(
                    r.get('criterion') == test_case['expected_criterion']
                    for r in results
                )
                
                if has_exact_match:
                    print(f"[OK] Found chunk with criterion = {test_case['expected_criterion']}")
                    # Show which position
                    for idx, r in enumerate(results, 1):
                        if r.get('criterion') == test_case['expected_criterion']:
                            print(f"  Position: {idx}, Source: {r['source']}, Page: {r['page']}")
                else:
                    print(f"[FAIL] No chunk with criterion = {test_case['expected_criterion']} found")
                    all_passed = False
            
            elif test_case['name'] == 'Test 2: NBA Prequalifier':
                # Check all results are NBA
                frameworks = set(r['framework'] for r in results)
                if frameworks == {'NBA'}:
                    print(f"[OK] All results from NBA (no NAAC chunks)")
                else:
                    print(f"[FAIL] Found non-NBA chunks: {frameworks}")
                    all_passed = False
                
                # Check doc types
                doc_types = set(r['doc_type'] for r in results)
                print(f"  Document types: {doc_types}")
            
            elif test_case['name'] == 'Test 3: NBA Policy':
                # Check framework
                frameworks = set(r['framework'] for r in results)
                if 'NBA' in frameworks:
                    print(f"[OK] Found NBA results")
                else:
                    print(f"[FAIL] No NBA results found")
                    all_passed = False
                
                # Check for policy chunks
                has_policy = any(r['doc_type'] == 'policy' for r in results)
                if has_policy:
                    print(f"[OK] Found policy chunks")
                    for idx, r in enumerate(results, 1):
                        if r['doc_type'] == 'policy':
                            print(f"  Position: {idx}, Source: {r['source']}")
                else:
                    print(f"[FAIL] No policy chunks found")
                    all_passed = False
            
            print(f"\n{'='*80}")
            print(f"Top-5 Results Summary:")
            print(f"{'='*80}")
            for idx, r in enumerate(results, 1):
                print(f"{idx}. [{r['framework']}] {r['doc_type']} - {r['source']} (Page {r['page']})")
                print(f"   Criterion: {r.get('criterion', 'N/A')}")
                print(f"   Scores: Dense={r['scores']['dense']:.3f}, "
                      f"BM25={r['scores']['bm25']:.3f}, "
                      f"Fused={r['scores']['fused']:.3f}, "
                      f"Reranker={r['scores']['reranker']:.3f}")
            
        except Exception as e:
            print(f"\n[FAIL] ERROR: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    pipeline.close()
    
    print(f"\n{'='*80}")
    if all_passed:
        print("[OK] ALL TESTS PASSED")
    else:
        print("[FAIL] SOME TESTS FAILED")
    print(f"{'='*80}")


if __name__ == "__main__":
    asyncio.run(test_phase2_1())
