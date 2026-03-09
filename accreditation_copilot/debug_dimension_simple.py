"""
Simple debug script to test dimension checker with sample text
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scoring.dimension_checker import DimensionChecker

def main():
    print("\n" + "="*80)
    print("DIMENSION CHECKER SIMPLE DEBUG")
    print("="*80 + "\n")
    
    # Initialize checker
    checker = DimensionChecker()
    
    # Sample text from Excellence University PDF (what should be in chunks)
    sample_text = """
    Grants received from Government and non-governmental agencies for research projects during the last five years.
    Total number of projects funded: 127 projects
    Total funds received: INR 4580 Lakhs
    Funding agencies: DST, SERB, DBT, ICSSR, Industry, Corporate partners
    
    Year 2019-20: 22 projects, 785 Lakhs funding from DST, SERB, DBT, Industry
    Year 2020-21: 28 projects, 920 Lakhs funding from SERB, DBT, ICSSR, DST
    Year 2021-22: 31 projects, 1150 Lakhs funding from DST, SERB, Industry, Corporate
    """.lower()
    
    print("Sample Text:")
    print("-" * 80)
    print(sample_text[:300])
    print("-" * 80)
    
    # Test dimensions for criterion 3.2.1
    dimensions = [
        {
            'id': 'funding_amount',
            'keywords': ["inr", "lakhs", "crore", "grant", "funds"]
        },
        {
            'id': 'project_count',
            'keywords': ["number of projects", "projects funded", "total"]
        },
        {
            'id': 'funding_agencies',
            'keywords': ["dst", "serb", "dbt", "icssr", "industry", "corporate"]
        }
    ]
    
    print("\n" + "="*80)
    print("TESTING EACH DIMENSION")
    print("="*80 + "\n")
    
    for dim in dimensions:
        print(f"\nDimension: {dim['id']}")
        print(f"Keywords: {dim['keywords']}")
        print("\nKeyword matches:")
        
        matches = []
        for keyword in dim['keywords']:
            if keyword.lower() in sample_text:
                matches.append(keyword)
                # Find context around keyword
                idx = sample_text.find(keyword.lower())
                context_start = max(0, idx - 30)
                context_end = min(len(sample_text), idx + len(keyword) + 30)
                context = sample_text[context_start:context_end].replace('\n', ' ')
                print(f"  ✓ '{keyword}' FOUND - Context: ...{context}...")
            else:
                print(f"  ✗ '{keyword}' NOT FOUND")
        
        print(f"\nTotal keyword matches: {len(matches)}/{len(dim['keywords'])}")
        
        # Test the actual checker method
        result = checker._check_dimension_match(sample_text, dim['keywords'])
        print(f"Checker _check_dimension_match result: {'✓ DETECTED' if result else '✗ NOT DETECTED'}")
        print("-" * 80)
    
    # Now test with mock retrieval results
    print("\n" + "="*80)
    print("TESTING FULL COVERAGE CHECK")
    print("="*80 + "\n")
    
    # Create mock retrieval results
    mock_results = [
        {
            'chunk_id': 'test_chunk_1',
            'source_type': 'institution',
            'child_text': sample_text[:len(sample_text)//2],
            'parent_context': sample_text[len(sample_text)//2:]
        }
    ]
    
    coverage = checker.check(mock_results, 'NAAC', '3.2.1')
    
    print(f"Dimensions covered: {coverage['dimensions_covered']}")
    print(f"Dimensions missing: {coverage['dimensions_missing']}")
    print(f"Coverage ratio: {coverage['coverage_ratio']}")
    print(f"Required dimensions: {coverage['required_dimensions']}")
    print(f"Per-chunk hits: {coverage['per_chunk_hits']}")
    print(f"Institution evidence available: {coverage.get('institution_evidence_available', False)}")
    
    if coverage['coverage_ratio'] == 0.0:
        print("\n⚠️  WARNING: Coverage is 0% even though keywords are present!")
        print("This is the bug causing 0% confidence scores.")
    elif coverage['coverage_ratio'] < 1.0:
        print(f"\n⚠️  WARNING: Coverage is only {coverage['coverage_ratio']*100}%")
        print(f"Missing dimensions: {coverage['dimensions_missing']}")
    else:
        print("\n✓ SUCCESS: All dimensions detected!")
    
    print("\n" + "="*80)
    print("DEBUG COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
