"""
Upload Router - Handles file uploads for institution documents
"""
import sys
from pathlib import Path
import shutil
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

router = APIRouter()

class UploadResponse(BaseModel):
    filename: str
    size: int
    status: str
    message: str

@router.post("/", response_model=List[UploadResponse])
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload institution documents (PDF, PNG, JPG).
    Files are saved to data/raw_docs/ for ingestion.
    """
    responses = []
    upload_dir = Path(__file__).parent.parent.parent / "data" / "raw_docs"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        try:
            # Validate file type
            allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg"}
            file_ext = Path(file.filename).suffix.lower()
            
            if file_ext not in allowed_extensions:
                responses.append(UploadResponse(
                    filename=file.filename,
                    size=0,
                    status="error",
                    message=f"Invalid file type: {file_ext}"
                ))
                continue
            
            # Save file
            file_path = upload_dir / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = file_path.stat().st_size
            
            responses.append(UploadResponse(
                filename=file.filename,
                size=file_size,
                status="success",
                message=f"Uploaded successfully"
            ))
            
        except Exception as e:
            responses.append(UploadResponse(
                filename=file.filename,
                size=0,
                status="error",
                message=str(e)
            ))
    
    return responses

@router.post("/ingest")
async def ingest_uploaded_files():
    """
    Trigger ingestion pipeline for uploaded files.
    Runs PDF processing, chunking, and indexing.
    """
    try:
        # Import ingestion modules
        from ingestion.run_ingestion import main as run_ingestion
        
        # Run ingestion
        # Note: This is a simplified version
        # In production, use background tasks or queue
        result = run_ingestion()
        
        return {
            "status": "success",
            "message": "Ingestion completed",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
