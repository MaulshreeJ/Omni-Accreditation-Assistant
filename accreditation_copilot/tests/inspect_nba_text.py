"""
Inspect NBA text to understand header format.
"""

import sqlite3


def main():
    db_path = "data/metadata.db"
    
    conn = sqlite3.connect(db_path)
    
    # Get sample NBA chunks
    cursor = conn.execute("""
        SELECT text, page, source
        FROM chunks
        WHERE framework='NBA'
        AND (text LIKE '%Criterion%' OR text LIKE '%C1%' OR text LIKE '%C2%' OR text LIKE '%C3%' OR text LIKE '%C4%' OR text LIKE '%C5%' OR text LIKE '%C6%')
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    
    print("=" * 80)
    print("NBA TEXT SAMPLES (containing 'Criterion' or 'C#')")
    print("=" * 80)
    
    for i, (text, page, source) in enumerate(results):
        print(f"\n--- Sample {i+1} ---")
        print(f"Source: {source}")
        print(f"Page: {page}")
        print(f"Text (first 500 chars):")
        print(text[:500])
        print()
    
    conn.close()


if __name__ == "__main__":
    main()
