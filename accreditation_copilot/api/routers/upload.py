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
    FIX: Clears old files before uploading new ones to ensure fresh ingestion.
    """
    responses = []
    upload_dir = Path(__file__).parent.parent.parent / "data" / "raw_docs"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # CRITICAL FIX: Delete all existing PDFs before uploading new ones
    # This ensures each audit uses only the newly uploaded file
    print("[UPLOAD] Clearing old institution documents...")
    for old_file in upload_dir.glob("*.pdf"):
        try:
            old_file.unlink()
            print(f"  Deleted: {old_file.name}")
        except Exception as e:
            print(f"  Warning: Could not delete {old_file.name}: {e}")
    
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
    
    CRITICAL: Clears old indexes, database, AND AUDIT CACHE before ingesting to ensure fresh data.
    """
    try:
        # Import institution ingestion runner
        from ingestion.institution.run_institution_ingestion import run_institution_ingestion
        
        # Use absolute path relative to project root
        project_root = Path(__file__).parent.parent.parent
        raw_docs_dir = project_root / "data" / "raw_docs"
        
        print(f"[INGESTION] Starting ingestion from: {raw_docs_dir}")
        print(f"[INGESTION] Directory exists: {raw_docs_dir.exists()}")
        
        # CRITICAL FIX: Clear old institution indexes and database entries
        print("[INGESTION] Clearing old institution data...")
        indexes_dir = project_root / "indexes" / "institution"
        if indexes_dir.exists():
            for index_file in indexes_dir.glob("institution*"):
                try:
                    index_file.unlink()
                    print(f"  Deleted: {index_file.name}")
                except Exception as e:
                    print(f"  Warning: Could not delete {index_file.name}: {e}")
        
        # Clear institution chunks from database
        import sqlite3
        db_path = project_root / "data" / "metadata.db"
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.execute("DELETE FROM chunks WHERE source_type='institution'")
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                print(f"  Deleted {deleted_count} old institution chunks from database")
            except Exception as e:
                print(f"  Warning: Could not clear database: {e}")
        
        # CRITICAL FIX: Clear audit cache to prevent stale results
        print("[INGESTION] Clearing audit cache...")
        from cache.audit_cache import AuditCache
        cache = AuditCache()
        cache.clear_cache()
        print("  Audit cache cleared")
        
        # CRITICAL FIX: Clear IndexLoader cache to force reload of institution indexes
        print("[INGESTION] Clearing IndexLoader cache...")
        from retrieval.index_loader import IndexLoader
        # Create a temporary instance just to clear the cache
        # Note: This won't affect existing instances, but we need to restart
        # the auditor to pick up new indexes
        temp_loader = IndexLoader()
        temp_loader.clear_institution_cache()
        
        # CRITICAL: Reset the global auditor instance to force reload
        # This ensures the next audit uses fresh indexes
        from api.routers.audit import get_auditor
        import api.routers.audit as audit_module
        audit_module.auditor = None
        audit_module.model_manager = None
        audit_module.cache = None
        print("  Auditor instance reset - will reload on next audit")
        
        # Run ingestion for institution documents in data/raw_docs/
        result = run_institution_ingestion(raw_docs_dir=str(raw_docs_dir))
        
        print(f"[INGESTION] Result: {result}")
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[INGESTION ERROR] {error_details}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
