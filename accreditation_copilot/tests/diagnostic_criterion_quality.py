"""
Diagnostic Script - Phase 1 Criterion Quality Check
Validates criterion extraction quality after Phase 1 fix.

Checks:
1. Criterion distribution (flag any with count=1 as suspicious)
2. Content-label alignment for 3.2.x chunks
3. Find '3.2.1' keyword regardless of label
"""

import sqlite3
from collections import Counter
from pathlib import Path


def check_criterion_distribution(db_path: str):
    """Check distribution of criteria across chunks."""
    print("=" * 80)
    print("CRITERION DISTRIBUTION CHECK")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all criteria
    cursor.execute("""
        SELECT criterion, COUNT(*) as count
        FROM chunks
        WHERE criterion IS NOT NULL
        GROUP BY criterion
        ORDER BY count DESC
    """)
    
    results = cursor.fetchall()
    
    print(f"\nTotal unique criteria: {len(results)}")
    print("\nCriterion distribution:")
    print(f"{'Criterion':<15} {'Count':<10} {'Status'}")
    print("-" * 50)
    
    suspicious = []
    for criterion, count in results:
        status = "⚠️ SUSPICIOUS" if count == 1 else "✓"
        print(f"{criterion:<15} {count:<10} {status}")
        if count == 1:
            suspicious.append(criterion)
    
    if suspicious:
        print(f"\n⚠️ Found {len(suspicious)} criteria with only 1 chunk (may indicate mislabeling)")
    else:
        print("\n✓ No suspicious single-chunk criteria found")
    
    conn.close()
    return suspicious


def check_321_content_alignment(db_path: str):
    """Check if chunks labeled 3.2.x actually contain that content."""
    print("\n" + "=" * 80)
    print("3.2.X CONTENT-LABEL ALIGNMENT CHECK")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all 3.2.x labeled chunks
    cursor.execute("""
        SELECT chunk_id, criterion, text, page
        FROM chunks
        WHERE criterion LIKE '3.2.%'
        ORDER BY criterion, page
    """)
    
    results = cursor.fetchall()
    
    print(f"\nFound {len(results)} chunks labeled with 3.2.x criteria")
    
    misaligned = []
    for chunk_id, criterion, text, page in results:
        # Check if the criterion actually appears in the text
        if criterion not in text:
            print(f"\n⚠️ MISALIGNMENT DETECTED:")
            print(f"  Chunk ID: {chunk_id}")
            print(f"  Label: {criterion}")
            print(f"  Page: {page}")
            print(f"  Criterion '{criterion}' NOT found in text")
            print(f"  Text preview: {text[:200]}...")
            misaligned.append((chunk_id, criterion, page))
        else:
            print(f"✓ {criterion} (page {page}): Label matches content")
    
    if misaligned:
        print(f"\n⚠️ Found {len(misaligned)} misaligned chunks")
    else:
        print("\n✓ All 3.2.x chunks have aligned labels")
    
    conn.close()
    return misaligned


def find_321_keyword(db_path: str):
    """Find all chunks containing '3.2.1' keyword regardless of label."""
    import re
    
    print("\n" + "=" * 80)
    print("3.2.1 KEYWORD SEARCH (REGARDLESS OF LABEL)")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all chunks
    cursor.execute("""
        SELECT chunk_id, criterion, text, page
        FROM chunks
        ORDER BY page
    """)
    
    results = cursor.fetchall()
    
    # Use word boundary regex to avoid substring matches
    pattern = re.compile(r'\b3\.2\.1\b')
    
    matched_chunks = []
    for chunk_id, criterion, text, page in results:
        if pattern.search(text):
            matched_chunks.append((chunk_id, criterion, text, page))
    
    print(f"\nFound {len(matched_chunks)} chunks containing '3.2.1' keyword")
    
    for chunk_id, criterion, text, page in matched_chunks:
        print(f"\n{'='*60}")
        print(f"Chunk ID: {chunk_id}")
        print(f"Label: {criterion}")
        print(f"Page: {page}")
        
        # Find context around '3.2.1'
        match = pattern.search(text)
        if match:
            idx = match.start()
            start = max(0, idx - 100)
            end = min(len(text), idx + 200)
            context = text[start:end]
            print(f"Context: ...{context}...")
        
        # Check if label matches content
        if criterion == '3.2.1':
            print("✓ Label matches keyword")
        else:
            print(f"⚠️ Label mismatch: labeled as '{criterion}' but contains '3.2.1'")
    
    conn.close()
    return matched_chunks


def run_full_diagnostic():
    """Run all diagnostic checks."""
    db_path = "data/metadata.db"
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        print("Please run ingestion first: python ingestion/run_ingestion.py")
        return
    
    print("\n" + "=" * 80)
    print("PHASE 1 CRITERION QUALITY DIAGNOSTIC")
    print("=" * 80)
    
    # Run checks
    suspicious = check_criterion_distribution(db_path)
    misaligned = check_321_content_alignment(db_path)
    keyword_results = find_321_keyword(db_path)
    
    # Summary
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    if suspicious:
        print(f"⚠️ {len(suspicious)} suspicious single-chunk criteria")
    else:
        print("✓ No suspicious single-chunk criteria")
    
    if misaligned:
        print(f"⚠️ {len(misaligned)} misaligned 3.2.x chunks")
    else:
        print("✓ All 3.2.x chunks properly aligned")
    
    print(f"ℹ️ {len(keyword_results)} chunks contain '3.2.1' keyword")
    
    # Final verdict
    if not suspicious and not misaligned:
        print("\n✅ PASS: Criterion extraction quality looks good!")
        print("You can proceed with Phase 2 precision tests.")
    else:
        print("\n❌ FAIL: Issues detected in criterion extraction")
        print("Do NOT proceed with Phase 2 tests until these are resolved.")


if __name__ == "__main__":
    run_full_diagnostic()
