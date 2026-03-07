"""Quick Phase 6 diagnostic test."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*80)
print("PHASE 6 QUICK DIAGNOSTIC")
print("="*80)

# Test 1: Import all Phase 6 modules
print("\n1. Testing imports...")
try:
    from analysis.evidence_grounder import EvidenceGrounder
    from analysis.gap_detector import GapDetector
    from scoring.evidence_strength import EvidenceStrengthScorer
    print("[PASS] All Phase 6 modules imported successfully")
except Exception as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

# Test 2: Test reranker fix
print("\n2. Testing reranker scoring fix...")
try:
    from retrieval.reranker import Reranker
    reranker = Reranker()
    
    candidates = [
        {'chunk_id': 'naac-metric-3.2.1-0', 'fused_score': 0.8},
        {'chunk_id': 'naac-metric-3.2.1-1', 'fused_score': 0.7}
    ]
    
    results = reranker.rerank("test query", candidates, top_k=2)
    scores = [r.get('reranker_score', 0.0) for r in results]
    
    print(f"  Reranker scores: {scores}")
    
    if any(s > 0 for s in scores):
        print("[PASS] Reranker produces non-zero scores")
    else:
        print("[WARN] Reranker scores are zero (may need real chunks)")
    
    reranker.close()
except Exception as e:
    print(f"[FAIL] Reranker test error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test dimension checker enhancement
print("\n3. Testing dimension coverage enhancement...")
try:
    from scoring.dimension_checker import DimensionChecker
    checker = DimensionChecker()
    
    # Test regex matching
    test_text = "research publications and funding received"
    keywords = ["publication", "funding"]
    
    match = checker._check_dimension_match(test_text, keywords)
    print(f"  Regex match result: {match}")
    
    if match:
        print("[PASS] Enhanced dimension matching works")
    else:
        print("[FAIL] Dimension matching failed")
except Exception as e:
    print(f"[FAIL] Dimension checker test error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test evidence grounder
print("\n4. Testing evidence grounder...")
try:
    grounder = EvidenceGrounder()
    
    # Mock data
    results = [
        {'chunk_id': 'test-1', 'reranker_score': 0.8, 'final_score': 2.4}
    ]
    per_chunk_hits = {'test-1': ['dim1', 'dim2']}
    
    grounded = grounder.ground_evidence(results, per_chunk_hits)
    print(f"  Grounded entries: {len(grounded)}")
    
    if len(grounded) > 0:
        print("[PASS] Evidence grounder works")
    else:
        print("[WARN] No grounded evidence (may need real chunks)")
    
    grounder.close()
except Exception as e:
    print(f"[FAIL] Evidence grounder test error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test gap detector
print("\n5. Testing gap detector...")
try:
    detector = GapDetector()
    
    # Mock coverage and confidence
    coverage = {
        'coverage_ratio': 0.3,
        'dimensions_missing': ['dim1', 'dim2']
    }
    confidence = {
        'overall_confidence': 0.4,
        'evidence_quality': 0.3
    }
    
    gaps = detector.detect_gaps(coverage, confidence, True)
    print(f"  Gaps detected: {len(gaps)}")
    
    if len(gaps) > 0:
        print(f"  Sample gap: {gaps[0]['gap_type']} ({gaps[0]['severity']})")
        print("[PASS] Gap detector works")
    else:
        print("[WARN] No gaps detected")
except Exception as e:
    print(f"[FAIL] Gap detector test error: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Test evidence strength scorer
print("\n6. Testing evidence strength scorer...")
try:
    scorer = EvidenceStrengthScorer()
    
    # Mock data
    results = [
        {
            'chunk_id': 'test-1',
            'source_type': 'institution',
            'reranker_score': 0.8,
            'final_score': 2.4
        }
    ]
    per_chunk_hits = {'test-1': ['dim1', 'dim2']}
    evidence_scores = {}
    
    strength = scorer.score_evidence_strength(results, per_chunk_hits, evidence_scores)
    print(f"  Overall strength: {strength['overall_strength']}")
    print(f"  Strong: {strength['strong_count']}, Moderate: {strength['moderate_count']}, Weak: {strength['weak_count']}")
    
    if strength['overall_strength'] != 'None':
        print("[PASS] Evidence strength scorer works")
    else:
        print("[WARN] No strength calculated")
except Exception as e:
    print(f"[FAIL] Evidence strength scorer test error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("PHASE 6 QUICK DIAGNOSTIC COMPLETE")
print("="*80)
