"""
Check what's actually in the institution index chunks
"""
import sqlite3
from pathlib import Path

def main():
    print("\n" + "="*80)
    print("CHECKING ACTUAL INSTITUTION CHUNKS")
    print("="*80 + "\n")
    
    # Path to database
    db_path = Path(__file__).parent / "data" / "metadata.db"
    
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return
    
    print(f"Database: {db_path}\n")
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check what tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables in database: {[t[0] for t in tables]}\n")
    
    # First check the schema
    cursor.execute("PRAGMA table_info(chunks)")
    schema = cursor.fetchall()
    print("Chunks table schema:")
    for col in schema:
        print(f"  {col[1]} ({col[2]})")
    print()
    
    # Get all institution chunks
    cursor.execute("""
        SELECT chunk_id, source, page, text
        FROM chunks
        WHERE source_type = 'institution'
        ORDER BY chunk_id
        LIMIT 10
    """)
    
    chunks = cursor.fetchall()
    
    if not chunks:
        print("⚠️  WARNING: No institution chunks found in database!")
        print("This means the PDF hasn't been ingested yet.")
        print("\nTo fix:")
        print("1. Upload Excellence_University_A+_SSR.pdf through the UI")
        print("2. Click 'Ingest Files' button")
        print("3. Wait for ingestion to complete")
        print("4. Run this script again")
    else:
        print(f"Found {len(chunks)} institution chunks (showing first 10)\n")
        print("="*80)
        
        for i, (chunk_id, source, page, text) in enumerate(chunks, 1):
            print(f"\nChunk {i}:")
            print(f"  ID: {chunk_id}")
            print(f"  Source: {source}")
            print(f"  Page: {page}")
            print(f"\n  Text (first 300 chars):")
            print(f"  {text[:300] if text else 'None'}...")
            
            # Check for key dimension keywords
            text_lower = (text or '').lower()
            
            keywords_found = []
            if 'inr' in text_lower or 'lakhs' in text_lower:
                keywords_found.append('funding_amount')
            if 'projects' in text_lower or 'number of projects' in text_lower:
                keywords_found.append('project_count')
            if any(agency in text_lower for agency in ['dst', 'serb', 'dbt', 'icssr']):
                keywords_found.append('funding_agencies')
            
            if keywords_found:
                print(f"\n  ✓ Dimensions detected: {keywords_found}")
            else:
                print(f"\n  ✗ No dimension keywords found")
            
            print("-" * 80)
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM chunks WHERE source_type = 'institution'")
    total = cursor.fetchone()[0]
    print(f"\nTotal institution chunks in database: {total}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("CHECK COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
