"""
Rebuild Ingestion - Phase 1.1
Rebuild database and indexes with new token-based chunking.
"""

import os
import shutil
from pathlib import Path
import sqlite3


def delete_old_data():
    """Delete old database and indexes."""
    print("\n" + "="*70)
    print("STEP 1: Cleaning old data")
    print("="*70)
    
    import time
    
    # Delete metadata.db
    db_path = Path("data/metadata.db")
    if db_path.exists():
        print(f"Deleting {db_path}...")
        max_retries = 5
        for attempt in range(max_retries):
            try:
                db_path.unlink()
                print("✅ Database deleted")
                break
            except PermissionError:
                if attempt < max_retries - 1:
                    print(f"  Database locked, waiting... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)
                else:
                    print("❌ Could not delete database - file is locked by another process")
                    print("   Please close any programs accessing the database and try again")
                    raise
    else:
        print("⚠️  Database not found (already clean)")
    
    # Delete all index files
    indexes_dir = Path("indexes")
    if indexes_dir.exists():
        print(f"\nDeleting all files in {indexes_dir}...")
        for file in indexes_dir.glob("*"):
            if file.is_file():
                print(f"  Deleting {file.name}...")
                try:
                    file.unlink()
                except PermissionError:
                    print(f"  ⚠️  Could not delete {file.name} (file locked)")
        print("✅ Index cleanup complete")
    else:
        print("⚠️  Indexes directory not found")


def run_ingestion():
    """Run the ingestion pipeline."""
    print("\n" + "="*70)
    print("STEP 2: Running ingestion pipeline")
    print("="*70)
    
    from ingestion.run_ingestion import IngestionOrchestrator
    
    # Use the actual PDF locations on D: drive
    naac_dir = "D:/Accreditation Frameworks/NAAC"
    nba_dir = "D:/Accreditation Frameworks/NBA"
    
    print(f"\nUsing PDF directories:")
    print(f"  NAAC: {naac_dir}")
    print(f"  NBA: {nba_dir}")
    
    orchestrator = IngestionOrchestrator()
    orchestrator.run(naac_dir=naac_dir, nba_dir=nba_dir)


def print_chunk_statistics():
    """Print statistics about the new chunks."""
    print("\n" + "="*70)
    print("STEP 3: Chunk Statistics")
    print("="*70)
    
    try:
        conn = sqlite3.connect('data/metadata.db')
        cursor = conn.cursor()
        
        # Total chunks
        cursor.execute('SELECT COUNT(*) FROM chunks')
        total_chunks = cursor.fetchone()[0]
        print(f"\nTotal chunks: {total_chunks}")
        
        # Chunks per framework
        cursor.execute('SELECT framework, COUNT(*) FROM chunks GROUP BY framework')
        for framework, count in cursor.fetchall():
            print(f"  {framework}: {count} chunks")
        
        # Token statistics
        print("\nToken Statistics:")
        
        # Load tokenizer
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-base-en-v1.5")
        
        cursor.execute('SELECT text FROM chunks')
        all_texts = cursor.fetchall()
        
        token_counts = []
        chunks_over_400 = 0
        chunks_over_450 = 0
        
        for (text,) in all_texts:
            tokens = len(tokenizer.encode(text, add_special_tokens=False))
            token_counts.append(tokens)
            if tokens > 400:
                chunks_over_400 += 1
            if tokens > 450:
                chunks_over_450 += 1
        
        if token_counts:
            avg_tokens = sum(token_counts) / len(token_counts)
            max_tokens = max(token_counts)
            min_tokens = min(token_counts)
            
            print(f"  Average tokens per chunk: {avg_tokens:.1f}")
            print(f"  Min tokens: {min_tokens}")
            print(f"  Max tokens: {max_tokens}")
            print(f"  Chunks > 400 tokens: {chunks_over_400} ({'✅ PASS' if chunks_over_400 == 0 else '⚠️  WARNING'})")
            print(f"  Chunks > 450 tokens: {chunks_over_450} ({'✅ PASS' if chunks_over_450 == 0 else '❌ FAIL'})")
            
            # Distribution
            print("\nToken Distribution:")
            ranges = [(0, 250), (250, 300), (300, 350), (350, 400), (400, 450), (450, 1000)]
            for min_t, max_t in ranges:
                count = sum(1 for t in token_counts if min_t <= t < max_t)
                pct = (count / len(token_counts)) * 100
                print(f"  {min_t:3d}-{max_t:3d} tokens: {count:4d} chunks ({pct:5.1f}%)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")


def main():
    """Main rebuild process."""
    print("\n" + "="*70)
    print("PHASE 1.1: INGESTION GRANULARITY REBUILD")
    print("="*70)
    print("\nThis will:")
    print("  1. Delete old database and indexes")
    print("  2. Re-run ingestion with new token-based chunking")
    print("  3. Print chunk statistics")
    print("\nTarget: 300 tokens per chunk")
    print("Hard cap: 400 tokens")
    print("Absolute max: 450 tokens")
    print("\nStarting rebuild...")
    
    # Step 1: Clean old data
    delete_old_data()
    
    # Step 2: Run ingestion
    run_ingestion()
    
    # Step 3: Print statistics
    print_chunk_statistics()
    
    print("\n" + "="*70)
    print("REBUILD COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("  1. Run: python test_phase2_2_verification.py")
    print("  2. Check for siblings_used > 0")
    print("  3. Verify parent expansion is working")


if __name__ == "__main__":
    main()
