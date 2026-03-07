"""
Reviewer Feedback Store - Phase E3
Stores and retrieves reviewer ratings for retrieval quality tuning.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class FeedbackStore:
    """
    Stores reviewer feedback on retrieved chunks.
    
    Ratings:
    - relevant: Chunk is relevant to the query
    - irrelevant: Chunk is not relevant to the query
    - missing: Expected chunk was not retrieved
    """
    
    def __init__(self, db_path: str = "data/feedback.db"):
        """
        Initialize feedback store.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create tables."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                framework TEXT NOT NULL,
                criterion TEXT,
                chunk_id TEXT NOT NULL,
                rating TEXT NOT NULL,
                reviewer_id TEXT,
                comment TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Create indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_query ON feedback(query)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chunk_id ON feedback(chunk_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rating ON feedback(rating)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON feedback(timestamp)')
        
        self.conn.commit()
    
    def add_feedback(self, query: str, framework: str, criterion: str,
                    chunk_id: str, rating: str, reviewer_id: str = None,
                    comment: str = None, metadata: Dict = None) -> int:
        """
        Add reviewer feedback for a chunk.
        
        Args:
            query: Original query
            framework: NAAC or NBA
            criterion: Criterion ID
            chunk_id: Chunk ID being rated
            rating: Rating (relevant, irrelevant, missing)
            reviewer_id: Optional reviewer identifier
            comment: Optional comment
            metadata: Optional additional metadata
            
        Returns:
            Feedback ID
        """
        # Validate rating
        valid_ratings = ['relevant', 'irrelevant', 'missing']
        if rating not in valid_ratings:
            raise ValueError(f"Invalid rating: {rating}. Must be one of {valid_ratings}")
        
        cursor = self.conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO feedback (query, framework, criterion, chunk_id, rating, 
                                reviewer_id, comment, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (query, framework, criterion, chunk_id, rating, reviewer_id, 
              comment, metadata_json))
        
        self.conn.commit()
        
        return cursor.lastrowid
    
    def get_feedback_for_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Get all feedback for a specific query.
        
        Args:
            query: Query text
            
        Returns:
            List of feedback records
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM feedback WHERE query = ? ORDER BY timestamp DESC
        ''', (query,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_feedback_for_chunk(self, chunk_id: str) -> List[Dict[str, Any]]:
        """
        Get all feedback for a specific chunk.
        
        Args:
            chunk_id: Chunk ID
            
        Returns:
            List of feedback records
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM feedback WHERE chunk_id = ? ORDER BY timestamp DESC
        ''', (chunk_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_feedback_by_rating(self, rating: str) -> List[Dict[str, Any]]:
        """
        Get all feedback with a specific rating.
        
        Args:
            rating: Rating (relevant, irrelevant, missing)
            
        Returns:
            List of feedback records
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM feedback WHERE rating = ? ORDER BY timestamp DESC
        ''', (rating,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """
        Get feedback statistics.
        
        Returns:
            Dictionary with statistics
        """
        cursor = self.conn.cursor()
        
        # Total feedback count
        cursor.execute('SELECT COUNT(*) FROM feedback')
        total = cursor.fetchone()[0]
        
        # Count by rating
        cursor.execute('''
            SELECT rating, COUNT(*) as count 
            FROM feedback 
            GROUP BY rating
        ''')
        by_rating = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Count by framework
        cursor.execute('''
            SELECT framework, COUNT(*) as count 
            FROM feedback 
            GROUP BY framework
        ''')
        by_framework = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Recent feedback
        cursor.execute('''
            SELECT * FROM feedback 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        recent = [dict(row) for row in cursor.fetchall()]
        
        return {
            'total_feedback': total,
            'by_rating': by_rating,
            'by_framework': by_framework,
            'recent_feedback': recent
        }
    
    def export_feedback(self, output_path: str) -> None:
        """
        Export all feedback to JSON file.
        
        Args:
            output_path: Path to output file
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM feedback ORDER BY timestamp DESC')
        
        rows = cursor.fetchall()
        feedback_list = [dict(row) for row in rows]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(feedback_list, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✓ Exported {len(feedback_list)} feedback records to {output_path}")
    
    def clear_all(self):
        """Clear all feedback from database."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM feedback')
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# Helper function to add batch feedback
def add_batch_feedback(store: FeedbackStore, feedback_list: List[Dict[str, Any]]) -> int:
    """
    Add multiple feedback records at once.
    
    Args:
        store: FeedbackStore instance
        feedback_list: List of feedback dictionaries
        
    Returns:
        Number of records added
    """
    count = 0
    for feedback in feedback_list:
        try:
            store.add_feedback(
                query=feedback['query'],
                framework=feedback['framework'],
                criterion=feedback.get('criterion', ''),
                chunk_id=feedback['chunk_id'],
                rating=feedback['rating'],
                reviewer_id=feedback.get('reviewer_id'),
                comment=feedback.get('comment'),
                metadata=feedback.get('metadata')
            )
            count += 1
        except Exception as e:
            print(f"Error adding feedback: {e}")
    
    return count


# Test function
if __name__ == "__main__":
    # Create test feedback store
    store = FeedbackStore("test_feedback.db")
    
    # Add sample feedback
    feedback_id = store.add_feedback(
        query="NAAC 3.2.1 research funding",
        framework="NAAC",
        criterion="3.2.1",
        chunk_id="test-chunk-123",
        rating="relevant",
        reviewer_id="reviewer-1",
        comment="Highly relevant chunk with funding details"
    )
    
    print(f"Added feedback with ID: {feedback_id}")
    
    # Get stats
    stats = store.get_feedback_stats()
    print(f"\nFeedback stats: {stats}")
    
    store.close()
