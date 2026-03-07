"""
Metadata Store - Phase 1
SQLite database for storing chunk metadata.
"""

import sqlite3
from typing import List, Dict, Optional
from pathlib import Path


class MetadataStore:
    """
    SQLite-based metadata store for document chunks.
    """
    
    def __init__(self, db_path: str = "data/metadata.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create tables."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Create chunks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                framework TEXT NOT NULL,
                doc_type TEXT NOT NULL,
                criterion TEXT,
                tier TEXT,
                stage TEXT,
                page INTEGER,
                chunk_order INTEGER DEFAULT 0,
                source TEXT NOT NULL,
                text TEXT NOT NULL,
                source_type TEXT DEFAULT 'framework',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add source_type column if it doesn't exist (migration)
        try:
            cursor.execute('ALTER TABLE chunks ADD COLUMN source_type TEXT DEFAULT "framework"')
            self.conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        # Create indices for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_framework ON chunks(framework)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_doc_type ON chunks(doc_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_criterion ON chunks(criterion)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tier ON chunks(tier)')
        
        self.conn.commit()
    
    def insert_chunk(self, chunk: Dict) -> bool:
        """
        Insert a chunk into the database.
        
        Args:
            chunk: Chunk dict with metadata
            
        Returns:
            True if successful
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO chunks (
                    chunk_id, framework, doc_type, criterion, 
                    tier, stage, page, chunk_order, source, text, source_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                chunk['chunk_id'],
                chunk['framework'],
                chunk['doc_type'],
                chunk.get('criterion'),
                chunk.get('tier', 'general'),
                chunk.get('stage', 'general'),
                chunk['page'],
                chunk.get('chunk_order', 0),
                chunk['source'],
                chunk['text'],
                chunk.get('source_type', 'framework')
            ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error inserting chunk {chunk.get('chunk_id')}: {e}")
            return False
    
    def insert_chunks_batch(self, chunks: List[Dict]) -> int:
        """
        Insert multiple chunks in a batch.
        
        Args:
            chunks: List of chunk dicts
            
        Returns:
            Number of chunks inserted
        """
        inserted = 0
        
        try:
            cursor = self.conn.cursor()
            
            for chunk in chunks:
                try:
                    cursor.execute('''
                        INSERT INTO chunks (
                            chunk_id, framework, doc_type, criterion, 
                            tier, stage, page, chunk_order, source, text, source_type
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        chunk['chunk_id'],
                        chunk['framework'],
                        chunk['doc_type'],
                        chunk.get('criterion'),
                        chunk.get('tier', 'general'),
                        chunk.get('stage', 'general'),
                        chunk['page'],
                        chunk.get('chunk_order', 0),
                        chunk['source'],
                        chunk['text'],
                        chunk.get('source_type', 'framework')
                    ))
                    inserted += 1
                except Exception as e:
                    print(f"Error inserting chunk {chunk.get('chunk_id')}: {e}")
            
            self.conn.commit()
            
        except Exception as e:
            print(f"Batch insert error: {e}")
        
        return inserted
    
    def get_chunk(self, chunk_id: str) -> Optional[Dict]:
        """
        Get a chunk by ID.
        
        Args:
            chunk_id: Chunk ID
            
        Returns:
            Chunk dict or None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM chunks WHERE chunk_id = ?', (chunk_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_chunks_by_framework(self, framework: str) -> List[Dict]:
        """
        Get all chunks for a framework.
        
        Args:
            framework: Framework name (NAAC/NBA)
            
        Returns:
            List of chunk dicts
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM chunks WHERE framework = ?', (framework,))
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_chunks_by_doc_type(self, framework: str, doc_type: str) -> List[Dict]:
        """
        Get chunks by framework and document type.
        
        Args:
            framework: Framework name
            doc_type: Document type
            
        Returns:
            List of chunk dicts
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM chunks WHERE framework = ? AND doc_type = ?',
            (framework, doc_type)
        )
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_chunk_count(self) -> int:
        """Get total number of chunks."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM chunks')
        return cursor.fetchone()[0]
    
    def get_chunk_count_by_framework(self, framework: str) -> int:
        """Get chunk count for a framework."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM chunks WHERE framework = ?', (framework,))
        return cursor.fetchone()[0]
    
    def get_chunk_count_by_doc_type(self, framework: str, doc_type: str) -> int:
        """Get chunk count by framework and doc type."""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT COUNT(*) FROM chunks WHERE framework = ? AND doc_type = ?',
            (framework, doc_type)
        )
        return cursor.fetchone()[0]
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        cursor = self.conn.cursor()
        
        stats = {
            'total_chunks': self.get_chunk_count(),
            'by_framework': {},
            'by_doc_type': {}
        }
        
        # Framework stats
        cursor.execute('SELECT framework, COUNT(*) FROM chunks GROUP BY framework')
        for row in cursor.fetchall():
            stats['by_framework'][row[0]] = row[1]
        
        # Doc type stats
        cursor.execute('SELECT framework, doc_type, COUNT(*) FROM chunks GROUP BY framework, doc_type')
        for row in cursor.fetchall():
            key = f"{row[0]}_{row[1]}"
            stats['by_doc_type'][key] = row[2]
        
        return stats
    
    def clear_all(self):
        """Clear all chunks from database."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM chunks')
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# Test function
if __name__ == "__main__":
    store = MetadataStore("test_metadata.db")
    
    # Test insert
    test_chunk = {
        'chunk_id': 'test-123',
        'framework': 'NAAC',
        'doc_type': 'policy',
        'criterion': 'C1',
        'tier': 'general',
        'stage': 'general',
        'page': 1,
        'source': 'test.pdf',
        'text': 'Test chunk text'
    }
    
    store.insert_chunk(test_chunk)
    
    # Test retrieve
    retrieved = store.get_chunk('test-123')
    print(f"Retrieved chunk: {retrieved}")
    
    # Test stats
    stats = store.get_statistics()
    print(f"Statistics: {stats}")
    
    store.close()
