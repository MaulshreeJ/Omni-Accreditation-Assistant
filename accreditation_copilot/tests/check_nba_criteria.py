"""
Check NBA criterion extraction.
"""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    db_path = "data/metadata.db"
    
    conn = sqlite3.connect(db_path)
    
    # Get distinct NBA criteria
    cursor = conn.execute("""
        SELECT DISTINCT criterion
        FROM chunks
        WHERE framework='NBA'
        AND criterion IS NOT NULL
        ORDER BY criterion
    """)
    
    criteria = [row[0] for row in cursor.fetchall()]
    
    print("=" * 60)
    print("NBA CRITERION EXTRACTION CHECK")
    print("=" * 60)
    print()
    
    if criteria:
        print(f"Found {len(criteria)} distinct NBA criteria:")
        for c in criteria:
            # Count chunks for this criterion
            count_cursor = conn.execute("""
                SELECT COUNT(*)
                FROM chunks
                WHERE framework='NBA'
                AND criterion=?
            """, (c,))
            count = count_cursor.fetchone()[0]
            print(f"  {c}: {count} chunks")
    else:
        print("❌ No NBA criteria found!")
        print("NBA boundary detection may not be working.")
    
    # Check total NBA chunks
    total_cursor = conn.execute("""
        SELECT COUNT(*)
        FROM chunks
        WHERE framework='NBA'
    """)
    total = total_cursor.fetchone()[0]
    
    labeled_cursor = conn.execute("""
        SELECT COUNT(*)
        FROM chunks
        WHERE framework='NBA'
        AND criterion IS NOT NULL
    """)
    labeled = labeled_cursor.fetchone()[0]
    
    print()
    print(f"Total NBA chunks: {total}")
    print(f"Labeled NBA chunks: {labeled}")
    print(f"Unlabeled NBA chunks: {total - labeled}")
    print(f"Labeling rate: {labeled/total*100:.1f}%")
    
    conn.close()


if __name__ == "__main__":
    main()
