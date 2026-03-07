"""
FIX 5: Evidence Field Normalization
Ensures every chunk has required fields with defaults.
"""
from typing import Dict, Any


def normalize_evidence_fields(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure every chunk has required fields with defaults.
    
    Args:
        chunk: Raw chunk data
        
    Returns:
        Normalized chunk with all required fields
    """
    normalized = {
        "chunk_id": chunk.get("chunk_id", "unknown"),
        "text": chunk.get("text", ""),
        "source_path": chunk.get("source_path", "unknown"),
        "page_number": chunk.get("page_number", 0),
        "source_type": chunk.get("source_type", "framework"),
        "reranker_score": chunk.get("reranker_score", 0.0),
        "dense_score": chunk.get("dense_score", 0.0),
        "bm25_score": chunk.get("bm25_score", 0.0),
        "fused_score": chunk.get("fused_score", 0.0),
        "final_score": chunk.get("final_score", 0.0)
    }
    
    # Preserve additional fields that might exist
    for key, value in chunk.items():
        if key not in normalized:
            normalized[key] = value
    
    return normalized
