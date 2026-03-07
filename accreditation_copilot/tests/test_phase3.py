"""
Phase 3 Complete Pipeline Test
Tests compliance reasoning engine with NAAC and NBA queries.
"""

import sys
import os
import json
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from retrieval.retrieval_pipeline import RetrievalPipeline
from scoring.scoring_pipeline import ScoringPipeline


def test_naac_321():
    """Test NAAC 3.2.1 compliance analysis."""
    print("\n" + "="*80)
    print("TEST 1: NAAC 3.2.1 COMPLIANCE ANALYSIS")
    print("="*80)
    
    # Phase 2: Retrieval
    print("\n[Phase 2] Running retrieval...")
    retrieval = RetrievalPipeline()
    query = "What are the requirements for NAAC 3.2.1?"
    
    # Run async retrieval
    results = asyncio.run(retrieval.run_retrieval(query, verbose=False, enable_parent_expansion=True))
    print(f"Retrieved {len(results)} chunks")
    
    # Transform results to match expected format for scoring pipeline
    transformed_results = []
    for r in results:
        transformed_results.append({
            'chunk_id': r['chunk_id'],
            'framework': r['framework'],
            'criterion': r.get('criterion'),
            'source': r['source'],
            'page': r['page'],
            'child_text': r.get('child_text', r.get('text', '')),
            'parent_context': r.get('parent_context', ''),
            'scores': r['scores']
        })
    
    # Phase 3: Compliance reasoning
    print("\n[Phase 3] Running compliance analysis...")
    scoring = ScoringPipeline()
    
    report = scoring.process(
        query=query,
        framework='NAAC',
        criterion='3.2.1',
        retrieval_results=transformed_results
    )
    
    # Display report
    print("\n" + "-"*80)
    print("COMPLIANCE REPORT")
    print("-"*80)
    print(f"Run ID: {report['run_id']}")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Query: {report['query']}")
    print(f"Framework: {report['framework']}")
    print(f"Criterion: {report['criterion']} - {report['metric_name']}")
    print()
    print(f"Confidence Score: {report['confidence_score']:.3f}")
    print(f"Compliance Status: {report['compliance_status']}")
    print()
    print(f"Dimensions Covered: {', '.join(report['dimensions_covered']) if report['dimensions_covered'] else 'None'}")
    print(f"Dimensions Missing: {', '.join(report['dimensions_missing']) if report['dimensions_missing'] else 'None'}")
    print(f"Coverage Ratio: {report['coverage_ratio']:.3f}")
    print()
    print("Evidence Summary:")
    print(f"  {report['evidence_summary']}")
    print()
    print("Gaps:")
    for gap in report['gaps']:
        print(f"  - {gap}")
    print()
    print("Recommendation:")
    print(f"  {report['recommendation']}")
    print()
    print("Sources:")
    for i, source in enumerate(report['evidence_sources'], 1):
        print(f"  {i}. {source['source_path']} (Page {source['page_number']}, Score: {source['reranker_score']:.3f})")
    print()
    print("Scoring Signals:")
    print(f"  Detected: {', '.join(report['scoring_signals']['signals_detected'])}")
    print(f"  Average Values: {report['scoring_signals']['average_values']}")
    print()
    print(f"Performance:")
    print(f"  Base Score: {report['base_score']:.3f}")
    print(f"  Avg Evidence Score: {report['avg_evidence_score']:.3f}")
    print(f"  Avg Retrieval Score: {report['avg_retrieval_score']:.3f}")
    print(f"  Latency: {report['latency_ms']:.2f} ms")
    print(f"  Chunks Analyzed: {report['num_chunks_analyzed']}")
    print("-"*80)
    
    # Validation
    assert report['framework'] == 'NAAC'
    assert report['criterion'] == '3.2.1'
    assert 'confidence_score' in report
    assert 'compliance_status' in report
    assert report['latency_ms'] < 5000  # Should be under 5 seconds
    
    print("\n[PASS] NAAC 3.2.1 test completed successfully")
    
    return report


def test_nba_c5():
    """Test NBA C5 compliance analysis."""
    print("\n" + "="*80)
    print("TEST 2: NBA C5 COMPLIANCE ANALYSIS")
    print("="*80)
    
    # Phase 2: Retrieval
    print("\n[Phase 2] Running retrieval...")
    retrieval = RetrievalPipeline()
    query = "What are the NBA Tier-II faculty requirements for Criterion 5?"
    
    # Run async retrieval
    results = asyncio.run(retrieval.run_retrieval(query, verbose=False, enable_parent_expansion=True))
    print(f"Retrieved {len(results)} chunks")
    
    # Transform results to match expected format for scoring pipeline
    transformed_results = []
    for r in results:
        transformed_results.append({
            'chunk_id': r['chunk_id'],
            'framework': r['framework'],
            'criterion': r.get('criterion'),
            'source': r['source'],
            'page': r['page'],
            'child_text': r.get('child_text', r.get('text', '')),
            'parent_context': r.get('parent_context', ''),
            'scores': r['scores']
        })
    
    # Phase 3: Compliance reasoning
    print("\n[Phase 3] Running compliance analysis...")
    scoring = ScoringPipeline()
    
    report = scoring.process(
        query=query,
        framework='NBA',
        criterion='C5',
        retrieval_results=transformed_results
    )
    
    # Display report
    print("\n" + "-"*80)
    print("COMPLIANCE REPORT")
    print("-"*80)
    print(f"Run ID: {report['run_id']}")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Query: {report['query']}")
    print(f"Framework: {report['framework']}")
    print(f"Criterion: {report['criterion']} - {report['metric_name']}")
    print()
    print(f"Confidence Score: {report['confidence_score']:.3f}")
    print(f"Compliance Status: {report['compliance_status']}")
    print()
    print(f"Dimensions Covered: {', '.join(report['dimensions_covered']) if report['dimensions_covered'] else 'None'}")
    print(f"Dimensions Missing: {', '.join(report['dimensions_missing']) if report['dimensions_missing'] else 'None'}")
    print(f"Coverage Ratio: {report['coverage_ratio']:.3f}")
    print()
    print("Evidence Summary:")
    print(f"  {report['evidence_summary']}")
    print()
    print("Gaps:")
    for gap in report['gaps']:
        print(f"  - {gap}")
    print()
    print("Recommendation:")
    print(f"  {report['recommendation']}")
    print()
    print("Sources:")
    for i, source in enumerate(report['evidence_sources'], 1):
        print(f"  {i}. {source['source_path']} (Page {source['page_number']}, Score: {source['reranker_score']:.3f})")
    print()
    print("Scoring Signals:")
    print(f"  Detected: {', '.join(report['scoring_signals']['signals_detected'])}")
    print(f"  Average Values: {report['scoring_signals']['average_values']}")
    print()
    print(f"Performance:")
    print(f"  Base Score: {report['base_score']:.3f}")
    print(f"  Avg Evidence Score: {report['avg_evidence_score']:.3f}")
    print(f"  Avg Retrieval Score: {report['avg_retrieval_score']:.3f}")
    print(f"  Latency: {report['latency_ms']:.2f} ms")
    print(f"  Chunks Analyzed: {report['num_chunks_analyzed']}")
    print("-"*80)
    
    # Validation
    assert report['framework'] == 'NBA'
    assert report['criterion'] == 'C5'
    assert 'confidence_score' in report
    assert 'compliance_status' in report
    assert report['latency_ms'] < 5000
    
    # Check faculty-related dimensions
    faculty_dims = ['faculty_qualifications', 'faculty_count', 'experience']
    covered = report['dimensions_covered']
    assert any(dim in covered for dim in faculty_dims), "No faculty dimensions detected"
    
    print("\n[PASS] NBA C5 test completed successfully")
    
    return report


def save_reports(naac_report, nba_report):
    """Save reports to JSON files."""
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    os.makedirs(output_dir, exist_ok=True)
    
    # Save NAAC report
    naac_path = os.path.join(output_dir, 'phase3_naac_321_report.json')
    with open(naac_path, 'w', encoding='utf-8') as f:
        json.dump(naac_report, f, indent=2)
    print(f"\nNAAC report saved to: {naac_path}")
    
    # Save NBA report
    nba_path = os.path.join(output_dir, 'phase3_nba_c5_report.json')
    with open(nba_path, 'w', encoding='utf-8') as f:
        json.dump(nba_report, f, indent=2)
    print(f"NBA report saved to: {nba_path}")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("PHASE 3 COMPLETE PIPELINE TEST")
    print("Testing: Evidence Scoring -> Dimension Checking -> Confidence -> Synthesis")
    print("="*80)
    
    try:
        # Test NAAC 3.2.1
        naac_report = test_naac_321()
        
        # Test NBA C5
        nba_report = test_nba_c5()
        
        # Save reports
        save_reports(naac_report, nba_report)
        
        # Final summary
        print("\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        print("NAAC 3.2.1 Test: PASS")
        print("NBA C5 Test: PASS")
        print()
        print("[PASS] ALL PHASE 3 TESTS PASSED")
        print("Phase 3 compliance reasoning engine working correctly")
        print("="*80)
        
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
