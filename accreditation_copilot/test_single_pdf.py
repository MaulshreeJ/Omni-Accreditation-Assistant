"""
Test script to ingest a single PDF and run audit
"""
import sys
import os
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def clear_institution_data():
    """Clear all institution data from database"""
    db_path = Path(__file__).parent / "data" / "metadata.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM chunks WHERE source_type="institution"')
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"[CLEAR] Deleted {deleted} institution chunks from database")
    return deleted

def ingest_pdf(pdf_path):
    """Ingest a single PDF"""
    from ingestion.institution.institution_indexer import InstitutionIndexer
    
    print(f"\n[INGEST] Processing: {pdf_path}")
    
    indexer = InstitutionIndexer()
    result = indexer.ingest_pdf(pdf_path)
    
    print(f"[INGEST] Created {result.get('chunks_created', 0)} chunks")
    return result

def run_audit():
    """Run audit for criterion 3.2.1"""
    from audit.criterion_auditor import CriterionAuditor
    from criteria import criterion_registry
    
    print(f"\n[AUDIT] Running audit for NAAC 3.2.1...")
    
    auditor = CriterionAuditor(enable_cache=False)
    criterion_def = criterion_registry.get_criterion("NAAC", "3.2.1")
    
    result = auditor.audit_criterion(
        criterion_id="3.2.1",
        framework="NAAC",
        query_template=criterion_def['query_template'],
        description=criterion_def['description']
    )
    
    print(f"\n[RESULT] Confidence: {result['confidence_score'] * 100:.1f}%")
    print(f"[RESULT] Coverage: {result['coverage_ratio'] * 100:.0f}%")
    print(f"[RESULT] Status: {result['compliance_status']}")
    print(f"[RESULT] Dimensions Covered: {result['dimensions_covered']}")
    print(f"[RESULT] Dimensions Missing: {result['dimensions_missing']}")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_single_pdf.py <path_to_pdf>")
        print("\nExample:")
        print('  python test_single_pdf.py "D:/NAAC_Test_PDFs/Good_College_B+_SSR.pdf"')
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF not found: {pdf_path}")
        sys.exit(1)
    
    print("="*80)
    print("SINGLE PDF TEST")
    print("="*80)
    
    # Step 1: Clear old data
    clear_institution_data()
    
    # Step 2: Ingest PDF
    ingest_pdf(pdf_path)
    
    # Step 3: Run audit
    result = run_audit()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
