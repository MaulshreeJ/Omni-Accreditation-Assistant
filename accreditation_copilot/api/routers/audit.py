"""
Audit Router - Wraps CriterionAuditor and caching system
"""
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from audit.criterion_auditor import CriterionAuditor
from models.model_manager import get_model_manager
from cache.audit_cache import AuditCache

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
    timestamp: str
    cached: bool = False

@router.post("/run", response_model=AuditResponse)
async def run_audit(request: AuditRequest):
    """
    Run audit for a specific criterion.
    Uses caching automatically.
    """
    try:
        auditor, cache = get_auditor()
        
        # Run audit with caching enabled
        result = auditor.audit_criterion(
            framework=request.framework,
            criterion=request.criterion,
            enable_cache=True
        )
        
        # Check if result was cached
        cached = result.get("cached", False)
        
        return AuditResponse(
            criterion=request.criterion,
            framework=request.framework,
            compliance_status=result.get("compliance_status", "unknown"),
            confidence_score=result.get("confidence_score", 0.0),
            coverage_ratio=result.get("coverage_ratio", 0.0),
            evidence_count=result.get("evidence_count", 0),
            evidence=result.get("evidence", []),
            gaps=result.get("gaps", []),
            grounding=result.get("grounding", {}),
            timestamp=datetime.now().isoformat(),
            cached=cached
        )
        
    except Exception as e:
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
