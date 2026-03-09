"""
FastAPI Backend for Omni Accreditation Copilot UI
Wraps existing Python modules without modifying them.
"""
import sys
from pathlib import Path
import numpy as np
from fastapi.encoders import jsonable_encoder

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from api.routers import audit, upload, metrics, chatbot


# Custom JSON encoder for NumPy types
def custom_jsonable_encoder(obj):
    """Convert NumPy types to Python types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return jsonable_encoder(obj)


# Initialize FastAPI app
app = FastAPI(
    title="Omni Accreditation Copilot API",
    description="API for accreditation audit system",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["chatbot"])

@app.get("/")
async def root():
    return {
        "message": "Omni Accreditation Copilot API",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
