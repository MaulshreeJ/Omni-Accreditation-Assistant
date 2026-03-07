"""
Test script to verify audit response structure includes all necessary fields.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from audit.criterion_auditor import CriterionAuditor
from models.model_manager import get_model_manager
import json

def test_audit_response():
    """Test that audit response includes all fields needed by frontend."""
    print("=" * 60)
    print("Testing Audit Response Structure")
    print("=" * 60)
    
    # Initialize auditor
    model_manager = get_model_manager()
    auditor = CriterionAuditor(model_manager=model_manager)
    
    # Run a test audit for NAAC 3.2.1
    result = auditor.audit_criterion(
        criterion_id="3.2.1",
        framework="NAAC",
        query_template="What is the total amount of research funding received from external agencies?",
        description="Extramural research funding"
    )
    
    # Check required fields
    required_fields = [
        'criterion',
        'framework',
        'compliance_status',
        'confidence_score',
        'coverage_ratio',
        'dimensions_covered',
        'dimensions_missing',
        'evidence_count',
        'explanation',
        'gaps',
        'recommendations'
    ]
    
    print("\n✓ Checking required fields:")
    missing_fields = []
    for field in required_fields:
        if field in result:
            value = result[field]
            print(f"  ✓ {field}: {type(value).__name__} = {value if not isinstance(value, (list, dict)) else f'{len(value)} items'}")
        else:
            print(f"  ✗ {field}: MISSING")
            missing_fields.append(field)
    
    if missing_fields:
        print(f"\n❌ Missing fields: {missing_fields}")
        return False
    
    # Print key metrics
    print("\n" + "=" * 60)
    print("Key Metrics:")
    print("=" * 60)
    print(f"Criterion: {result['criterion']}")
    print(f"Framework: {result['framework']}")
    print(f"Status: {result['compliance_status']}")
    print(f"Confidence: {result['confidence_score']:.1%}")
    print(f"Coverage: {result['coverage_ratio']:.1%}")
    print(f"Dimensions Covered: {result['dimensions_covered']}")
    print(f"Dimensions Missing: {result['dimensions_missing']}")
    print(f"Evidence Count: {result['evidence_count']}")
    
    # Print recommendations
    print("\n" + "=" * 60)
    print("Recommendations:")
    print("=" * 60)
    recommendations = result.get('recommendations', [])
    if isinstance(recommendations, list):
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print(f"1. {recommendations}")
    
    # Print gaps
    print("\n" + "=" * 60)
    print("Gaps:")
    print("=" * 60)
    gaps = result.get('gaps', [])
    for i, gap in enumerate(gaps, 1):
        print(f"{i}. {gap}")
    
    print("\n" + "=" * 60)
    print("✅ All required fields present!")
    print("=" * 60)
    
    # Save full result to file for inspection
    output_file = Path(__file__).parent / "test_audit_response_output.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nFull result saved to: {output_file}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_audit_response()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
