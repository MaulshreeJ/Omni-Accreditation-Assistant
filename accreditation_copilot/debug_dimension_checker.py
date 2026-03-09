"""
Debug script to test dimension checker with actual chunk text
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scoring.dimension_checker import DimensionChecker
from retrieval.index_loader import IndexLoader
from retrieval.hybrid_retriever import HybridRetriever
from models.model_manager import ModelManager

def main():
    print("\n" + "="*80)
    print("DIMENSION CHECKER DEBUG")
    print("="*80 + "\n")
    
    # Initialize components
    checker = DimensionChecker()
    loader = IndexLoader()
    model_manager = ModelManager()
    retriever = HybridRetriever(model_manager, loader)
    
    # Test query for 3.2.1
    query = "What is the total extramural funding received for research projects and from which agencies?"
    framework = "NAAC"
    criterion = "3.2.1"
    
    print(f"Query: {query}")
    print(f"Framework: {framework}")
    print(f"Criterion: {criterion}\n")
    
    # Retrieve chunks
    print("Retrieving chunks...")
    results = retriever.retrieve(query, framework, top_k=10)
    
    # Filter to institution chunks
    institution_chunks = [r for r in results if r.get('source_type') == 'institution']
    print(f"Found {len(institution_chunks)} institution chunks\n")
    
    if not institution_chunks:
        print("ERROR: No institution chunks found!")
        return
    
    # Print first chunk details
    print("="*80)
    print("FIRST CHUNK ANALYSIS")
    print("="*80)
    chunk = institution_chunks[0]
    text = (chunk.get('child_text', '') + ' ' + chunk.get('parent_context', '')).lower()
    
    print(f"\nChunk ID: {chunk.get('chunk_id', 'unknown')}")
    print(f"Source: {chunk.get('source', 'unknown')}")
    print(f"\nChunk Text (first 500 chars):")
    print("-" * 80)
    print(text[:500])
    print("-" * 80)
    
    # Check each dimension manually
    print("\n" + "="*80)
    print("DIMENSION KEYWORD MATCHING")
    print("="*80 + "\n")
    
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
    
    for dim in dimensions:
        print(f"\nDimension: {dim['id']}")
        print(f"Keywords: {dim['keywords']}")
        print("Matches found:")
        
        matches = []
        for keyword in dim['keywords']:
            if keyword.lower() in text:
                matches.append(keyword)
                print(f"  ✓ '{keyword}' FOUND")
            else:
                print(f"  ✗ '{keyword}' NOT FOUND")
        
        print(f"Total matches: {len(matches)}")
        
        # Test the actual checker method
        result = checker._check_dimension_match(text, dim['keywords'])
        print(f"Checker result: {'DETECTED' if result else 'NOT DETECTED'}")
    
    # Run full coverage check
    print("\n" + "="*80)
    print("FULL COVERAGE CHECK")
    print("="*80 + "\n")
    
    coverage = checker.check(results, framework, criterion)
    
    print(f"Dimensions covered: {coverage['dimensions_covered']}")
    print(f"Dimensions missing: {coverage['dimensions_missing']}")
    print(f"Coverage ratio: {coverage['coverage_ratio']}")
    print(f"Per-chunk hits: {coverage['per_chunk_hits']}")
    print(f"Institution evidence available: {coverage.get('institution_evidence_available', False)}")
    
    print("\n" + "="*80)
    print("DEBUG COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
