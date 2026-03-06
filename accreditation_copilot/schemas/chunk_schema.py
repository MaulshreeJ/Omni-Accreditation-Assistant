"""
Chunk Schema - Standard structure for evidence chunks
Ensures consistent data propagation through the pipeline.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class EvidenceChunk:
    """
    Standard structure for evidence chunks throughout the pipeline.
    
    This ensures that all required fields are present and properly typed,
    preventing data loss during pipeline transformations.
    """
    
    # Core identification
    chunk_id: str
    text: str
    
    # Source metadata
    source_path: str
    page_number: int
    source_type: str  # 'institution' or 'framework'
    framework: str  # 'NAAC', 'NBA', or 'INSTITUTION'
    
    # Retrieval scores
    dense_score: float = 0.0
    bm25_score: float = 0.0
    fused_score: float = 0.0
    reranker_score: float = 0.0
    final_score: float = 0.0
    
    # Context fields (for dimension checking)
    child_text: Optional[str] = None
    parent_context: Optional[str] = None
    
    # Criterion metadata (for framework chunks)
    criterion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'chunk_id': self.chunk_id,
            'text': self.text,
            'source_path': self.source_path,
            'page_number': self.page_number,
            'source_type': self.source_type,
            'framework': self.framework,
            'dense_score': self.dense_score,
            'bm25_score': self.bm25_score,
            'fused_score': self.fused_score,
            'reranker_score': self.reranker_score,
            'final_score': self.final_score,
            'child_text': self.child_text,
            'parent_context': self.parent_context,
            'criterion': self.criterion
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvidenceChunk':
        """Create from dictionary."""
        return cls(
            chunk_id=data.get('chunk_id', ''),
            text=data.get('text', ''),
            source_path=data.get('source_path', ''),
            page_number=data.get('page_number', 0),
            source_type=data.get('source_type', 'framework'),
            framework=data.get('framework', 'NAAC'),
            dense_score=data.get('dense_score', 0.0),
            bm25_score=data.get('bm25_score', 0.0),
            fused_score=data.get('fused_score', 0.0),
            reranker_score=data.get('reranker_score', 0.0),
            final_score=data.get('final_score', 0.0),
            child_text=data.get('child_text'),
            parent_context=data.get('parent_context'),
            criterion=data.get('criterion')
        )


# Type alias for dictionary-based chunks (for backward compatibility)
ChunkDict = Dict[str, Any]


def validate_chunk(chunk: ChunkDict) -> bool:
    """
    Validate that a chunk dictionary has all required fields.
    
    Args:
        chunk: Chunk dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        'chunk_id',
        'text',
        'source_path',
        'page_number',
        'source_type',
        'framework'
    ]
    
    for field in required_fields:
        if field not in chunk:
            return False
    
    return True


def ensure_chunk_scores(chunk: ChunkDict) -> ChunkDict:
    """
    Ensure all score fields are present in chunk.
    
    Args:
        chunk: Chunk dictionary
        
    Returns:
        Chunk with all score fields present
    """
    score_fields = {
        'dense_score': 0.0,
        'bm25_score': 0.0,
        'fused_score': 0.0,
        'reranker_score': 0.0,
        'final_score': 0.0
    }
    
    for field, default_value in score_fields.items():
        if field not in chunk:
            chunk[field] = default_value
    
    return chunk


def ensure_chunk_text_fields(chunk: ChunkDict) -> ChunkDict:
    """
    Ensure text-related fields are present in chunk.
    
    Args:
        chunk: Chunk dictionary
        
    Returns:
        Chunk with text fields present
    """
    # Ensure child_text and parent_context exist
    if 'child_text' not in chunk:
        chunk['child_text'] = chunk.get('text', '')
    
    if 'parent_context' not in chunk:
        chunk['parent_context'] = ''
    
    return chunk
