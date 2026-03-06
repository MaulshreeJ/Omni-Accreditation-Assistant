"""
Evidence Grounder - Phase 6 Capability 1
Maps evidence chunks to specific compliance dimensions with source metadata.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.metadata_store import MetadataStore


class EvidenceGrounder:
    """Ground evidence to specific compliance dimensions."""
    
    def __init__(self):
        """Initialize evidence grounder."""
        self.metadata_store = MetadataStore()
    
    def ground_evidence(
        self,
        retrieval_results: List[Dict[str, Any]],
        per_chunk_hits: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Map evidence chunks to dimensions they support.
        
        Args:
            retrieval_results: Retrieved evidence chunks (with text field)
            per_chunk_hits: Mapping of chunk_id -> dimensions covered
            
        Returns:
            List of grounded evidence with dimension mappings
        """
        grounded = []
        
        for result in retrieval_results:
            chunk_id = result.get('chunk_id', '')
            
            # Get dimensions this chunk supports
            dimensions_supported = per_chunk_hits.get(chunk_id, [])
            
            # Skip if no dimensions supported
            if not dimensions_supported:
                continue
            
            # Get text from result (added by dual_retrieval) or fallback to metadata
            text = result.get('text', '') or result.get('child_text', '')
            
            if not text:
                # Fallback: try to get from metadata store
                chunk = self.metadata_store.get_chunk(chunk_id)
                if chunk:
                    text = chunk.get('text', '')
                else:
                    continue
            
            # Get source metadata from result or metadata store
            source_type = result.get('source_type', 'unknown')
            if source_type == 'unknown':
                chunk = self.metadata_store.get_chunk(chunk_id)
                if chunk:
                    source_type = chunk.get('source_type', 'unknown')
            
            # Build grounded evidence entry
            grounded_entry = {
                'chunk_id': chunk_id,
                'dimensions_supported': dimensions_supported,
                'source_type': source_type,
                'source_file': result.get('source_path', 'unknown'),
                'text_preview': text[:200] + '...' if len(text) > 200 else text,
                'confidence_score': result.get('reranker_score', 0.0),
                'final_score': result.get('final_score', 0.0)
            }
            
            grounded.append(grounded_entry)
        
        # Sort by number of dimensions supported (most comprehensive first)
        grounded.sort(key=lambda x: len(x['dimensions_supported']), reverse=True)
        
        return grounded
    
    def close(self):
        """Close resources."""
        self.metadata_store.close()
