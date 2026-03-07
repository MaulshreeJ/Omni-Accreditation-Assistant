"""
Audit Router - Wraps CriterionAuditor and caching system
FIX 6: Standardized API responses
FIX 7: Structured logging for UI debugging
"""
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from audit.criterion_auditor import CriterionAuditor
from models.model_manager import get_model_manager
from cache.audit_cache import AuditCache
from api.error_handler import standardize_audit_response, safe_audit_execution

# FIX 7: Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize components (singleton pattern)
model_manager = None
auditor = None
cache = None

def get_auditor():
    """Lazy initialization of auditor with ModelManager singleton"""
    global model_manager, auditor, cache
    if auditor is None:
        model_manager = get_model_manager()
        auditor = CriterionAuditor(model_manager=model_manager)
        cache = AuditCache()
    return auditor, cache

class AuditRequest(BaseModel):
    framework: str  # "NAAC" or "NBA"
    criterion: str  # e.g., "3.2.1"
    query: Optional[str] = None  # Optional custom query

class AuditResponse(BaseModel):
    criterion: str
    framework: str
    compliance_status: str
    confidence_score: float
    coverage_ratio: float
    evidence_count: int
    evidence: list
    gaps: list
    grounding: dict
    dimensions_covered: list
    dimensions_missing: list
    recommendations: list
    explanation: str
    timestamp: str
    cached: bool = False

@router.post("/run", response_model=AuditResponse)
async def run_audit(request: AuditRequest):
    """
    Run audit for a specific criterion.
    Uses caching automatically.
    
    FIX 6: Standardized response format
    FIX 7: Structured logging for debugging
    """
    try:
        # FIX 7: Log audit start
        logger.info(f"[AUDIT START] Framework: {request.framework}, Criterion: {request.criterion}")
        
        auditor, cache = get_auditor()
        
        # Get criterion details from registry
        from criteria.criterion_registry import get_criteria
        criteria = get_criteria(request.framework)
        criterion_def = next((c for c in criteria if c['criterion'] == request.criterion), None)
        
        if not criterion_def:
            raise HTTPException(status_code=404, detail=f"Criterion {request.criterion} not found for {request.framework}")
        
        # Use custom query if provided, otherwise use template
        query_template = request.query if request.query else criterion_def['query_template']
        
        # Run audit with caching enabled
        result = auditor.audit_criterion(
            criterion_id=request.criterion,
            framework=request.framework,
            query_template=query_template,
            description=criterion_def['description']
        )
        
        # FIX 7: Log retrieval count
        evidence_count = result.get("evidence_count", 0)
        logger.info(f"[RETRIEVAL] Retrieved {evidence_count} evidence chunks")
        
        # FIX 7: Log compliance scoring complete
        compliance_status = result.get("compliance_status", "unknown")
        confidence_score = result.get("confidence_score", 0.0)
        logger.info(f"[COMPLIANCE] Status: {compliance_status}, Confidence: {confidence_score:.2f}")
        
        # Check if result was cached
        cached = result.get("cached", False)
        
        # FIX 7: Log audit completion
        logger.info(f"[AUDIT COMPLETE] Criterion: {request.criterion}, Cached: {cached}")
        
        # FIX 6: Standardize response
        standardized = standardize_audit_response(result)
        
        return AuditResponse(
            criterion=request.criterion,
            framework=request.framework,
            compliance_status=standardized.get("compliance_status", "unknown"),
            confidence_score=standardized.get("confidence_score", 0.0),
            coverage_ratio=standardized.get("coverage_ratio", 0.0),
            evidence_count=standardized.get("evidence_count", 0),
            evidence=standardized.get("evidence_sources", []),
            gaps=standardized.get("gaps", []),
            grounding={
                "dimension_grounding": standardized.get("dimension_grounding", []),
                "gaps_identified": standardized.get("gaps_identified", []),
                "evidence_strength": standardized.get("evidence_strength", {})
            },
            dimensions_covered=standardized.get("dimensions_covered", []),
            dimensions_missing=standardized.get("dimensions_missing", []),
            recommendations=standardized.get("recommendations", []),
            explanation=standardized.get("explanation", ""),
            timestamp=datetime.now().isoformat(),
            cached=cached
        )
        
    except Exception as e:
        # FIX 7: Log error
        logger.error(f"[AUDIT ERROR] {request.criterion}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache")
async def get_cached_audits():
    """
    Retrieve all cached audit results.
    """
    try:
        _, cache = get_auditor()
        
        # Get cache statistics
        stats = cache.get_stats()
        
        # List cached audits
        cached_audits = []
        # Note: Implement cache listing in AuditCache if needed
        
        return {
            "stats": stats,
            "audits": cached_audits
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache")
async def clear_cache():
    """
    Clear all cached audit results.
    """
    try:
        _, cache = get_auditor()
        cache.clear()
        
        return {"message": "Cache cleared successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
