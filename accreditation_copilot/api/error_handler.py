"""
FIX 3: UI-Friendly Error Handling
Catches errors from pipeline components and returns structured JSON responses.
"""
import sys
from pathlib import Path
import traceback
from typing import Dict, Any, Callable
from functools import wraps

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.evidence_normalizer import normalize_evidence_fields


def safe_audit_execution(func: Callable) -> Callable:
    """
    Decorator to catch errors during audit execution and return structured responses.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function that returns structured error responses
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            
            # Log full traceback for debugging
            print(f"[ERROR HANDLER] {error_type}: {error_message}")
            print(traceback.format_exc())
            
            # Return structured error response
            return {
                "status": "error",
                "error_type": error_type,
                "error_message": error_message,
                "compliance_status": "Error",
                "confidence_score": 0.0,
                "coverage_ratio": 0.0,
                "evidence_count": 0,
                "evidence": [],
                "gaps": ["System error occurred during audit"],
                "recommendations": ["Please check system logs and retry"],
                "grounding": {}
            }
    
    return wrapper


def handle_query_expansion_error(query: str, error: Exception) -> list:
    """
    Handle query expansion errors gracefully.
    
    Args:
        query: Original query
        error: Exception that occurred
        
    Returns:
        Fallback query list (original query only)
    """
    error_str = str(error).lower()
    
    if '429' in error_str or 'rate limit' in error_str:
        print(f"[ERROR HANDLER] Query expansion rate limit hit, using original query")
    else:
        print(f"[ERROR HANDLER] Query expansion failed: {error}")
    
    return [query]


def handle_retrieval_error(error: Exception) -> list:
    """
    Handle retrieval errors gracefully.
    
    Args:
        error: Exception that occurred
        
    Returns:
        Empty list (no results)
    """
    print(f"[ERROR HANDLER] Retrieval failed: {error}")
    return []


def handle_reranker_error(results: list, error: Exception) -> list:
    """
    Handle reranker errors gracefully.
    
    Args:
        results: Original retrieval results
        error: Exception that occurred
        
    Returns:
        Original results without reranking
    """
    print(f"[ERROR HANDLER] Reranker failed, returning original results: {error}")
    return results


def handle_pdf_ingestion_error(filename: str, error: Exception) -> Dict[str, Any]:
    """
    Handle PDF ingestion errors gracefully.
    
    Args:
        filename: Name of file being processed
        error: Exception that occurred
        
    Returns:
        Structured error response
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    print(f"[ERROR HANDLER] PDF ingestion failed for {filename}: {error_type} - {error_message}")
    
    return {
        "filename": filename,
        "status": "error",
        "error_type": error_type,
        "error_message": error_message,
        "chunks_created": 0
    }


def normalize_evidence_fields_wrapper(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """
    FIX 5: Wrapper for evidence normalization (delegates to utils module).
    
    Args:
        chunk: Raw chunk data
        
    Returns:
        Normalized chunk with all required fields
    """
    return normalize_evidence_fields(chunk)


def standardize_audit_response(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    FIX 6: Ensure audit response follows consistent JSON schema.
    
    Args:
        result: Raw audit result
        
    Returns:
        Standardized audit response
    """
    return {
        "status": "success",
        "framework": result.get("framework", "unknown"),
        "criterion": result.get("criterion", "unknown"),
        "compliance_status": result.get("compliance_status", "unknown"),
        "confidence_score": result.get("confidence_score", 0.0),
        "coverage_ratio": result.get("coverage_ratio", 0.0),
        "gaps": result.get("gaps", []),
        "recommendations": result.get("recommendations", []),
        "evidence_sources": result.get("evidence_sources", []),
        "evidence_count": result.get("evidence_count", 0),
        "institution_evidence_count": result.get("institution_evidence_count", 0),
        "dimension_grounding": result.get("dimension_grounding", []),
        "gaps_identified": result.get("gaps_identified", []),
        "evidence_strength": result.get("evidence_strength", {}),
        "timestamp": result.get("timestamp", None)
    }
