"""
Metrics Router - Exposes retrieval evaluation metrics
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class MetricsResponse(BaseModel):
    precision: float
    recall: float
    f1: float
    mrr: float
    num_queries: int
    top_k: int

@router.get("/", response_model=MetricsResponse)
async def get_metrics():
    """
    Get retrieval evaluation metrics.
    Returns Precision@k, Recall@k, F1 Score, and MRR.
    """
    try:
        from evaluation.compute_metrics import compute_metrics
        
        # Compute metrics
        metrics = compute_metrics(top_k=8)
        
        return MetricsResponse(
            precision=metrics['precision'],
            recall=metrics['recall'],
            f1=metrics['f1'],
            mrr=metrics['mrr'],
            num_queries=metrics['num_queries'],
            top_k=metrics['top_k']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
