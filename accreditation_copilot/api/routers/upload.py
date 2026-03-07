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
    
    FIX 4: Validates file type and size before processing.
    """
    responses = []
    upload_dir = Path(__file__).parent.parent.parent / "data" / "raw_docs"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # FIX 4: Validation constants
    ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
    MAX_FILE_SIZE_MB = 20
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    
    for file in files:
        try:
            # FIX 4: Validate file type
            allowed_extensions = ALLOWED_EXTENSIONS
            file_ext = Path(file.filename).suffix.lower()
            
            if file_ext not in allowed_extensions:
                responses.append(UploadResponse(
                    filename=file.filename,
                    size=0,
                    status="error",
                    message=f"Invalid file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
                ))
                continue
            
            # FIX 4: Read file and validate size
            file_content = await file.read()
            file_size = len(file_content)
            
            if file_size > MAX_FILE_SIZE_BYTES:
                responses.append(UploadResponse(
                    filename=file.filename,
                    size=file_size,
                    status="error",
                    message=f"File too large: {file_size / (1024*1024):.1f}MB. Max: {MAX_FILE_SIZE_MB}MB"
                ))
                continue
            
            # Save file
            file_path = upload_dir / file.filename
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            responses.append(UploadResponse(
                filename=file.filename,
                size=file_size,
                status="success",
                message=f"Uploaded successfully ({file_size / 1024:.1f}KB)"
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
    Trigger ingestion pipeline for uploaded institution files.
    Runs PDF processing, chunking, and indexing for institutional documents.
    """
    try:
        # Import institution ingestion runner
        from ingestion.institution.run_institution_ingestion import run_institution_ingestion
        
        # Run ingestion for institution documents in data/raw_docs/
        result = run_institution_ingestion(raw_docs_dir="data/raw_docs")
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[INGESTION ERROR] {error_details}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
