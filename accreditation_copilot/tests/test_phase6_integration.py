"""Phase 6 Integration Test - Full end-to-end validation."""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from audit.criterion_auditor import CriterionAuditor

print("="*80)
print("PHASE 6 INTEGRATION TEST")
print("="*80)

print("\nRunning full criterion audit with Phase 6 enhancements...")

auditor = CriterionAuditor()

try:
    # Run audit for NAAC 3.2.1
    result = auditor.audit_criterion(
        criterion_id='3.2.1',
        framework='NAAC',
        query_template='What is the extramural funding for research?',
        description='Extramural funding for research'
    )
    
    print("\n" + "="*80)
    print("AUDIT RESULT SUMMARY")
    print("="*80)
    
    # Core metrics
    print(f"\nCriterion: {result['criterion']}")
    print(f"Framework: {result['framework']}")
    print(f"Compliance Status: {result['compliance_status']}")
    print(f"Confidence Score: {result['confidence_score']:.1%}")
    print(f"Coverage Ratio: {result['coverage_ratio']:.1%}")
    
    # Evidence counts
    print(f"\nEvidence:")
    print(f"  Total chunks: {result['evidence_count']}")
    print(f"  Institution chunks: {result['institution_evidence_count']}")
    print(f"  Institution evidence available: {result['institution_evidence_available']}")
    
    # Phase 6: Evidence Strength
    strength = result.get('evidence_strength', {})
    print(f"\nEvidence Strength (Phase 6):")
    print(f"  Overall: {strength.get('overall_strength', 'N/A')}")
    print(f"  Strong: {strength.get('strong_count', 0)}")
    print(f"  Moderate: {strength.get('moderate_count', 0)}")
    print(f"  Weak: {strength.get('weak_count', 0)}")
    
    # Phase 6: Gaps Identified
    gaps = result.get('gaps_identified', [])
    print(f"\nGaps Identified (Phase 6): {len(gaps)}")
    if gaps:
        for i, gap in enumerate(gaps[:3], 1):
            print(f"  {i}. [{gap['severity'].upper()}] {gap['gap_type']}")
            print(f"     {gap['description']}")
    
    # Phase 6: Dimension Grounding
    grounding = result.get('dimension_grounding', [])
    print(f"\nDimension Grounding (Phase 6): {len(grounding)} chunks")
    if grounding:
        for i, entry in enumerate(grounding[:3], 1):
            dims = entry.get('dimensions_supported', [])
            print(f"  {i}. Chunk {entry.get('chunk_id', 'N/A')[:20]}...")
            print(f"     Dimensions: {', '.join(dims)}")
            print(f"     Source: {entry.get('source_type', 'N/A')}")
    
    # Dimensions
    print(f"\nDimensions:")
    print(f"  Covered: {result['dimensions_covered']}")
    print(f"  Missing: {result['dimensions_missing']}")
    
    print("\n" + "="*80)
    print("PHASE 6 INTEGRATION TEST COMPLETE")
    print("="*80)
    
    # Save full result to file for inspection
    output_file = Path(__file__).parent.parent / 'docs' / 'phase6_integration_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nFull result saved to: {output_file}")
    
    # Validation checks
    print("\n" + "="*80)
    print("VALIDATION CHECKS")
    print("="*80)
    
    checks = []
    
    # Check 1: Evidence strength present
    if 'evidence_strength' in result:
        print("[PASS] Evidence strength analysis present")
        checks.append(True)
    else:
        print("[FAIL] Evidence strength analysis missing")
        checks.append(False)
    
    # Check 2: Gaps identified present
    if 'gaps_identified' in result:
        print("[PASS] Gap detection present")
        checks.append(True)
    else:
        print("[FAIL] Gap detection missing")
        checks.append(False)
    
    # Check 3: Dimension grounding present
    if 'dimension_grounding' in result:
        print("[PASS] Dimension grounding present")
        checks.append(True)
    else:
        print("[FAIL] Dimension grounding missing")
        checks.append(False)
    
    # Check 4: Institution evidence count >= 0
    if result['institution_evidence_count'] >= 0:
        print(f"[PASS] Institution evidence count valid: {result['institution_evidence_count']}")
        checks.append(True)
    else:
        print(f"[FAIL] Institution evidence count invalid: {result['institution_evidence_count']}")
        checks.append(False)
    
    # Check 5: Core Phase 3/4/5 fields present
    required_fields = ['confidence_score', 'coverage_ratio', 'compliance_status', 
                      'institution_evidence_available', 'explanation']
    all_present = all(field in result for field in required_fields)
    if all_present:
        print("[PASS] All core fields present (Phase 3/4/5 stable)")
        checks.append(True)
    else:
        missing = [f for f in required_fields if f not in result]
        print(f"[FAIL] Missing core fields: {missing}")
        checks.append(False)
    
    # Summary
    passed = sum(checks)
    total = len(checks)
    print(f"\nValidation: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n[SUCCESS] Phase 6 integration test PASSED")
        exit(0)
    else:
        print(f"\n[FAILURE] Phase 6 integration test FAILED ({total - passed} checks failed)")
        exit(1)

except Exception as e:
    print(f"\n[ERROR] Integration test failed with exception:")
    print(f"  {e}")
    import traceback
    traceback.print_exc()
    exit(1)

finally:
    auditor.close()
