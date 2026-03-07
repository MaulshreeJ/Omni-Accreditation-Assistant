"""
D5 - Audit Trail Enricher
Attaches source metadata for page-level traceability.
"""

import sqlite3
from typing import List, Dict, Any
from pathlib import Path


class AuditEnricher:
    """Enrich evidence with audit trail metadata."""
    
    def __init__(self, db_path: str = "data/metadata.db"):
        """Initialize enricher with database path."""
        self.db_path = Path(db_path)
    
    def enrich_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich source information with full metadata.
        
        Args:
            results: Retrieval results
            
        Returns:
            Enriched source entries with audit trail
        """
        enriched_sources = []
        
        for result in results:
            chunk_id = result.get('chunk_id')
            
            if not chunk_id:
                continue
            
            # Query metadata
            metadata = self._get_chunk_metadata(chunk_id)
            
            # Get text content from result
            text_content = result.get('text') or result.get('child_text', 'No text available')
            
            if metadata:
                # Get reranker score from result (handle both formats)
                reranker_score = result.get('reranker_score', 0.0)
                if reranker_score == 0.0:
                    # Try nested format
                    reranker_score = result.get('scores', {}).get('reranker', 0.0)
                
                enriched_sources.append({
                    'chunk_id': chunk_id,
                    'source': metadata['source'],  # Frontend expects 'source'
                    'page': metadata['page'],  # Frontend expects 'page'
                    'source_type': metadata['source_type'],
                    'criterion': metadata.get('criterion', 'N/A'),
                    'framework': metadata['framework'],
                    'text': text_content,  # Include text content
                    'reranker_score': round(reranker_score, 3),
                    'strength': self._determine_strength(reranker_score)
                })
        
        return enriched_sources
    
    def _determine_strength(self, reranker_score: float) -> str:
        """
        Determine evidence strength based on reranker score.
        
        Args:
            reranker_score: Reranker score (0-1)
            
        Returns:
            'Strong', 'Moderate', or 'Weak'
        """
        if reranker_score >= 0.7:
            return 'Strong'
        elif reranker_score >= 0.4:
            return 'Moderate'
        else:
            return 'Weak'
    
    def _get_chunk_metadata(self, chunk_id: str) -> Dict[str, Any]:
        """
        Get metadata for a chunk from database.
        
        Args:
            chunk_id: Chunk identifier
            
        Returns:
            Metadata dict or None
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                '''SELECT chunk_id, source, page, criterion, framework, doc_type
                   FROM chunks WHERE chunk_id = ?''',
                (chunk_id,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                metadata = dict(row)
                
                # FIXED: Determine source_type from doc_type
                # Current doc_types: 'metric', 'policy', 'prequalifier' are all framework
                # In Phase 4, institutional documents will have doc_type = 'institutional'
                doc_type = metadata.get('doc_type', 'policy')
                metadata['source_type'] = 'institution' if doc_type == 'institutional' else 'framework'
                
                return metadata
            
            return None
            
        except Exception as e:
            print(f"Error fetching metadata for {chunk_id}: {e}")
            return None
