"""
Test the full audit flow to see where 0% confidence comes from
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit.criterion_auditor import CriterionAuditor
from criteria import criterion_registry

def main():
    print("\n" + "="*80)
    print("TESTING FULL AUDIT FLOW FOR 3.2.1")
    print("="*80 + "\n")
    
    # Initialize components
    auditor = CriterionAuditor(enable_cache=False)
    
    # Get criterion details
    framework = "NAAC"
    criterion = "3.2.1"
    
    criterion_def = criterion_registry.get_criterion(framework, criterion)
    if not criterion_def:
        print(f"ERROR: Criterion {framework} {criterion} not found in registry")
        return
    
    print(f"Criterion: {criterion_def['description']}")
    print(f"Query: {criterion_def['query_template']}")
    print()
    
    print(f"Running audit...")
    print()
    
    result = auditor.audit_criterion(
        criterion_id=criterion,
        framework=framework,
        query_template=criterion_def['query_template'],
        description=criterion_def['description']
    )
    
    print("="*80)
    print("AUDIT RESULT")
    print("="*80)
    print(f"\nCriterion: {result.get('criterion', 'unknown')}")
    print(f"Confidence Score: {result.get('confidence_score', 0)}%")
    print(f"Compliance Status: {result.get('compliance_status', 'unknown')}")
    
    # Print all keys to see what's available
    print(f"\nAvailable keys in result: {list(result.keys())}")
    
    print(f"\nEvidence Count: {result.get('evidence_count', 0)}")
    print(f"Institution Evidence Count: {result.get('institution_evidence_count', 0)}")
    
    # Check coverage
    print(f"\nCoverage Ratio: {result.get('coverage_ratio', 0)}")
    print(f"Dimensions Covered: {result.get('dimensions_covered', [])}")
    print(f"Dimensions Missing: {result.get('dimensions_missing', [])}")
    print(f"Institution Evidence Available: {result.get('institution_evidence_available', False)}")
    
    # Check full_report for detailed scores
    if 'full_report' in result:
        full_report = result['full_report']
        print(f"\nFull Report Scores:")
        print(f"  Confidence Score: {full_report.get('confidence_score', 'N/A')}")
        print(f"  Base Score: {full_report.get('base_score', 'N/A')}")
        print(f"  Avg Evidence Score: {full_report.get('avg_evidence_score', 'N/A')}")
        print(f"  Avg Retrieval Score: {full_report.get('avg_retrieval_score', 'N/A')}")
        print(f"  Coverage Ratio: {full_report.get('coverage_ratio', 'N/A')}")
        
        # Check if there are evidence_scores
        if 'evidence_scores' in full_report:
            evidence_scores = full_report['evidence_scores']
            if isinstance(evidence_scores, list) and len(evidence_scores) > 0:
                print(f"\n  First 3 Evidence Scores:")
                for i, score in enumerate(evidence_scores[:3], 1):
                    print(f"    {i}. {score}")
            elif isinstance(evidence_scores, dict):
                print(f"\n  Evidence Scores Dict: {evidence_scores}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
    
    # Diagnosis
    confidence = result.get('confidence_score', 0)
    if confidence == 0:
        print("DIAGNOSIS: Confidence is 0%")
        print("\nPossible causes:")
        if result.get('coverage_ratio', 0) == 0:
            print("  1. Coverage ratio is 0% - dimensions not detected in chunks")
            print("     This is the root cause!")
        if result.get('institution_evidence_count', 0) == 0:
            print("  2. No institution evidence found")
        if result.get('institution_evidence_available', True) == False:
            print("  3. Institution evidence not available")
    elif confidence < 0.01:  # Less than 1%
        print(f"DIAGNOSIS: Confidence is very low ({confidence * 100:.3f}%)")
        print(f"\nThis is likely a scoring issue, not a dimension detection issue.")
        print(f"Coverage ratio: {result.get('coverage_ratio', 0) * 100}%")
        print(f"Dimensions missing: {result.get('dimensions_missing', [])}")
        print(f"Institution evidence count: {result.get('institution_evidence_count', 0)}")
        
        # Check full_report for clues
        if 'full_report' in result:
            full_report = result['full_report']
            base_score = full_report.get('base_score', 0)
            avg_evidence = full_report.get('avg_evidence_score', 0)
            avg_retrieval = full_report.get('avg_retrieval_score', 0)
            
            print(f"\nDetailed Scores:")
            print(f"  Base Score: {base_score}")
            print(f"  Avg Evidence Score: {avg_evidence}")
            print(f"  Avg Retrieval Score: {avg_retrieval}")
            
            if avg_evidence < 0.01:
                print(f"\n  ROOT CAUSE: Evidence scores are too low ({avg_evidence})")
                print(f"  The evidence scorer is not detecting patterns correctly.")
            elif avg_retrieval < 0.01:
                print(f"\n  ROOT CAUSE: Retrieval scores are too low ({avg_retrieval})")
                print(f"  The reranker scores are not being calculated correctly.")
    else:
        print(f"Confidence is {confidence * 100:.2f}% - system is working!")

if __name__ == "__main__":
    main()
