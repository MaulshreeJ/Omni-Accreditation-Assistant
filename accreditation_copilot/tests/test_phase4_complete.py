"""
Phase 4 Complete Validation Suite
Tests all Phase 4 components and integration with Phase 3.

Run this to validate Phase 4 implementation:
    python tests/test_phase4_complete.py
"""

import sys
from pathlib import Path
import time

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent))

from retrieval.dual_retrieval import DualRetriever
from retrieval.index_loader import IndexLoader
from scoring.dimension_checker import DimensionChecker


def print_header(title):
    """Print formatted header."""
    print("\n" + "="*80)
    print(title)
    print("="*80)


def print_subheader(title):
    """Print formatted subheader."""
    print(f"\n{title}")
    print("-" * len(title))


def test_milestone_2_ingestion():
    """Test Milestone 2: Institution PDF Ingestion."""
    print_header("TEST 1: MILESTONE 2 - INSTITUTION PDF INGESTION")
    
    try:
        from ingestion.institution.row_chunker import RowChunker
        
        # Mock table data
        table_data = {
            'headers': ['S.No', 'Year', 'Project Title', 'Funding Agency', 'Amount (INR Lakhs)', 'Duration'],
            'rows': [
                ['1', '2022-23', 'AI in Education Research', 'DST', '24.5', '2 years'],
                ['2', '2023-24', 'Data Science for Agriculture', 'DBT', '32.0', '2 years'],
            ],
            'table_id': 'test_table'
        }
        
        # Test row chunker
        chunker = RowChunker()
        chunks = chunker.chunk_table(
            table=table_data,
            page_number=45,
            source_path='SSR_Evidence.pdf'
        )
        
        print(f"\n✓ Created {len(chunks)} table row chunks")
        
        # Validate chunk structure
        first_chunk = chunks[0]
        
        validations = [
            ('source_type', 'institution', first_chunk.get('source_type')),
            ('doc_type', 'institutional', first_chunk.get('doc_type')),
            ('evidence_type', 'table_row', first_chunk.get('evidence_type')),
            ('evidence_weight', 1.2, first_chunk.get('evidence_weight')),
        ]
        
        all_valid = True
        for field, expected, actual in validations:
            if actual == expected:
                print(f"✓ {field}: {actual}")
            else:
                print(f"✗ {field}: expected {expected}, got {actual}")
                all_valid = False
        
        # Check text normalization
        text = first_chunk['text']
        if 'S.No' not in text and '₹' in text and 'Agency: DST' in text:
            print("✓ Text normalization: S.No removed, currency normalized, agency normalized")
        else:
            print("✗ Text normalization failed")
            all_valid = False
        
        # Check structured data
        structured = first_chunk.get('structured_data', {})
        if 'agency' in structured and 'funding_lakhs' in structured:
            print("✓ Structured data: canonical schema applied")
        else:
            print("✗ Structured data: canonical schema missing")
            all_valid = False
        
        if all_valid:
            print("\n[PASS] Milestone 2 validation passed")
            return True
        else:
            print("\n[FAIL] Milestone 2 validation failed")
            return False
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] Milestone 2 validation failed")
        return False


def test_milestone_3_indexing():
    """Test Milestone 3: Institution Index Building."""
    print_header("TEST 2: MILESTONE 3 - INSTITUTION INDEX BUILDING")
    
    try:
        # Check if institution index exists
        index_loader = IndexLoader()
        institution_index_path = index_loader.institution_index_dir / 'institution.index'
        
        if not institution_index_path.exists():
            print("✗ Institution index not found")
            print(f"  Expected: {institution_index_path}")
            print("\n[FAIL] Milestone 3 validation failed")
            return False
        
        print(f"✓ Institution index found: {institution_index_path}")
        
        # Load index
        faiss_index, chunk_ids = index_loader.load_faiss_index_institution('institution')
        print(f"✓ FAISS index loaded: {faiss_index.ntotal} vectors")
        
        # Load BM25 index
        bm25, bm25_chunk_ids, tokenized = index_loader.load_bm25_index_institution('institution')
        print(f"✓ BM25 index loaded: {len(bm25_chunk_ids)} documents")
        
        # Check metadata
        if chunk_ids:
            chunk = index_loader.get_chunk_metadata(chunk_ids[0])
            if chunk:
                source_type = chunk.get('source_type', 'unknown')
                print(f"✓ Metadata loaded: source_type={source_type}")
                
                if source_type == 'institution':
                    print("✓ Source type correctly set to 'institution'")
                else:
                    print(f"✗ Source type incorrect: expected 'institution', got '{source_type}'")
                    index_loader.close()
                    print("\n[FAIL] Milestone 3 validation failed")
                    return False
            else:
                print("✗ Metadata not found for chunk")
                index_loader.close()
                print("\n[FAIL] Milestone 3 validation failed")
                return False
        
        index_loader.close()
        print("\n[PASS] Milestone 3 validation passed")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] Milestone 3 validation failed")
        return False


def test_milestone_4_dual_retrieval():
    """Test Milestone 4: Dual Retrieval."""
    print_header("TEST 3: MILESTONE 4 - DUAL RETRIEVAL")
    
    try:
        retriever = DualRetriever()
        
        # Test query
        query = "What are the requirements for NAAC 3.2.1?"
        query_variants = [
            query,
            "NAAC 3.2.1 extramural funding research",
            "research grants external funding"
        ]
        
        print(f"\nQuery: '{query}'")
        print(f"Framework: NAAC")
        print(f"Query type: metric")
        
        # Retrieve
        start_time = time.time()
        results, institution_evidence_available = retriever.retrieve(
            query=query,
            query_variants=query_variants,
            framework='NAAC',
            query_type='metric',
            top_k_framework=3,
            top_k_institution=7
        )
        elapsed = time.time() - start_time
        
        print(f"\n✓ Retrieved {len(results)} chunks in {elapsed:.2f}s")
        print(f"✓ Institution evidence available: {institution_evidence_available}")
        
        # Count framework vs institution chunks
        index_loader = IndexLoader()
        framework_count = 0
        institution_count = 0
        
        for result in results:
            chunk_id = result['chunk_id']
            chunk = index_loader.get_chunk_metadata(chunk_id)
            if chunk:
                source_type = chunk.get('source_type', 'framework')
                if source_type == 'institution':
                    institution_count += 1
                else:
                    framework_count += 1
        
        print(f"\nResult breakdown:")
        print(f"  Framework chunks: {framework_count} (context)")
        print(f"  Institution chunks: {institution_count} (evidence)")
        
        # Validate slot allocation
        if framework_count <= 3 and institution_count <= 7:
            print("✓ Slot allocation correct (3 framework + 7 institution)")
        else:
            print(f"✗ Slot allocation incorrect: {framework_count} framework, {institution_count} institution")
        
        # Show top results
        print(f"\nTop 3 results:")
        for i, result in enumerate(results[:3], 1):
            chunk_id = result['chunk_id']
            chunk = index_loader.get_chunk_metadata(chunk_id)
            if chunk:
                source_type = chunk.get('source_type', 'framework')
                source = chunk.get('source', 'unknown')
                score = result.get('reranker_score', 0)
                final_score = result.get('final_score', score)
                evidence_weight = chunk.get('evidence_weight', 1.0)
                print(f"  {i}. [{source_type.upper()}] {source[:40]}... (rerank: {score:.4f}, weight: {evidence_weight}, final: {final_score:.4f})")
        
        # Validate that institution chunks appear in top 3
        top_3_source_types = []
        for result in results[:3]:
            chunk_id = result['chunk_id']
            chunk = index_loader.get_chunk_metadata(chunk_id)
            if chunk:
                source_type = chunk.get('source_type', 'framework')
                top_3_source_types.append(source_type)
        
        institution_in_top_3 = sum(1 for st in top_3_source_types if st == 'institution')
        
        if institution_in_top_3 > 0:
            print(f"\n✓ Institution chunks in top 3: {institution_in_top_3}")
        else:
            print(f"\n✗ No institution chunks in top 3 (expected at least 1)")
            index_loader.close()
            retriever.close()
            print("\n[FAIL] Milestone 4 validation failed")
            return False
        
        index_loader.close()
        retriever.close()
        
        print("\n[PASS] Milestone 4 validation passed")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] Milestone 4 validation failed")
        return False


def test_milestone_5_dimension_coverage():
    """Test Milestone 5: Honest Dimension Coverage."""
    print_header("TEST 4: MILESTONE 5 - HONEST DIMENSION COVERAGE")
    
    try:
        # Create mock results with mixed source types
        mock_results = [
            {
                'chunk_id': 'framework-1',
                'source_type': 'framework',
                'child_text': 'extramural funding research grants',
                'parent_context': ''
            },
            {
                'chunk_id': 'institution-1',
                'source_type': 'institution',
                'child_text': 'DST funding Rs. 24.5 lakhs research project',
                'parent_context': ''
            },
            {
                'chunk_id': 'institution-2',
                'source_type': 'institution',
                'child_text': 'SERB grant 2022-23 external funding',
                'parent_context': ''
            }
        ]
        
        # Test dimension checker
        checker = DimensionChecker()
        coverage = checker.check(mock_results, 'NAAC', '3.2.1')
        
        print(f"\nCoverage analysis:")
        print(f"  Coverage ratio: {coverage['coverage_ratio']}")
        print(f"  Dimensions covered: {len(coverage['dimensions_covered'])}")
        print(f"  Dimensions missing: {len(coverage['dimensions_missing'])}")
        print(f"  Institution evidence available: {coverage.get('institution_evidence_available', False)}")
        
        # Validate that only institution chunks are counted
        per_chunk_hits = coverage.get('per_chunk_hits', {})
        institution_chunks_counted = sum(1 for chunk_id in per_chunk_hits.keys() if 'institution' in chunk_id)
        framework_chunks_counted = sum(1 for chunk_id in per_chunk_hits.keys() if 'framework' in chunk_id)
        
        print(f"\nPer-chunk tracking:")
        print(f"  Institution chunks counted: {institution_chunks_counted}")
        print(f"  Framework chunks counted: {framework_chunks_counted}")
        
        if framework_chunks_counted == 0 and institution_chunks_counted > 0:
            print("✓ Only institution chunks counted as evidence")
        else:
            print("✗ Framework chunks incorrectly counted as evidence")
            print("\n[FAIL] Milestone 5 validation failed")
            return False
        
        # Test with no institution evidence
        framework_only_results = [
            {
                'chunk_id': 'framework-1',
                'source_type': 'framework',
                'child_text': 'extramural funding research grants',
                'parent_context': ''
            }
        ]
        
        coverage_no_inst = checker.check(framework_only_results, 'NAAC', '3.2.1')
        
        if coverage_no_inst['coverage_ratio'] == 0.0 and not coverage_no_inst.get('institution_evidence_available', True):
            print("✓ Coverage ratio = 0 when no institution evidence")
        else:
            print("✗ Coverage ratio should be 0 when no institution evidence")
            print("\n[FAIL] Milestone 5 validation failed")
            return False
        
        print("\n[PASS] Milestone 5 validation passed")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] Milestone 5 validation failed")
        return False


def test_phase3_integration():
    """Test Phase 3 integration (no regressions)."""
    print_header("TEST 5: PHASE 3 INTEGRATION (NO REGRESSIONS)")
    
    try:
        print("\nRunning Phase 3 deterministic tests...")
        
        import subprocess
        result = subprocess.run(
            ['python', 'tests/test_phase3_deterministic.py'],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 and '[PASS] ALL PHASE 3 DETERMINISTIC TESTS PASSED' in result.stdout:
            print("✓ All Phase 3 tests passed")
            print("\n[PASS] Phase 3 integration validation passed")
            return True
        else:
            print("✗ Phase 3 tests failed")
            print("\nOutput:")
            print(result.stdout)
            if result.stderr:
                print("\nErrors:")
                print(result.stderr)
            print("\n[FAIL] Phase 3 integration validation failed")
            return False
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] Phase 3 integration validation failed")
        return False


def main():
    """Run all Phase 4 validation tests."""
    print_header("PHASE 4 COMPLETE VALIDATION SUITE")
    print("Testing all Phase 4 milestones and integration with Phase 3")
    
    results = []
    
    # Run all tests
    results.append(("Milestone 2: Institution PDF Ingestion", test_milestone_2_ingestion()))
    results.append(("Milestone 3: Institution Index Building", test_milestone_3_indexing()))
    results.append(("Milestone 4: Dual Retrieval", test_milestone_4_dual_retrieval()))
    results.append(("Milestone 5: Honest Dimension Coverage", test_milestone_5_dimension_coverage()))
    results.append(("Phase 3 Integration", test_phase3_integration()))
    
    # Print summary
    print_header("VALIDATION SUMMARY")
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("✓ ALL PHASE 4 VALIDATION TESTS PASSED")
        print("="*80)
        print("\nPhase 4 is complete and ready for production use.")
        print("\nKey achievements:")
        print("  • Institution PDF ingestion working")
        print("  • Institution index built with correct metadata")
        print("  • Dual retrieval from framework + institution indexes")
        print("  • Honest dimension coverage (only institution chunks counted)")
        print("  • Phase 3 reasoning engine stable (no regressions)")
        print("\nNext steps:")
        print("  • Upload institutional evidence documents")
        print("  • Run end-to-end compliance checks")
        print("  • Monitor performance and accuracy")
        return 0
    else:
        print("✗ SOME PHASE 4 VALIDATION TESTS FAILED")
        print("="*80)
        print("\nPlease review the failed tests above and fix issues.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
