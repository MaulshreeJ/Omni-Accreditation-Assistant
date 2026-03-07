# Ingestion Fix Complete ✅

## Problem
The "Ingest Files" button was failing with error: "File ingestion failed. Please check the backend logs."

## Root Cause
The upload router was calling `run_ingestion.py` which is designed for framework documents (NAAC/NBA guidelines), not institution documents (your uploaded PDFs).

## Solution
Created a new institution-specific ingestion runner that:
1. Processes PDFs in `data/raw_docs/`
2. Parses pages and extracts tables
3. Chunks tables into rows
4. Builds FAISS and BM25 indexes
5. Stores metadata in SQLite database

## Files Created/Modified

### New File
- `ingestion/institution/run_institution_ingestion.py` - Institution document ingestion runner

### Modified File
- `api/routers/upload.py` - Updated `/ingest` endpoint to use institution ingestion

## How to Test

### Step 1: Restart Backend
The backend needs to be restarted to load the new code:

```bash
# Stop the current backend (Ctrl+C in the terminal)
# Then restart:
cd accreditation_copilot
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Step 2: Refresh Frontend
Refresh the page at http://localhost:3000

### Step 3: Click "Ingest Files"
1. Click the "Ingest Files" button
2. Wait 1-5 minutes
3. You should see: "Files ingested successfully!"

### Step 4: Run Audit Again
Click "Run Audit" and you'll now see real results!

## What the Ingestion Does

The institution ingestion pipeline:

1. **PDF Parsing** (`pdf_parser.py`)
   - Extracts text from each page
   - Identifies tables and their locations

2. **Table Extraction** (`table_extractor.py`)
   - Extracts structured table data
   - Preserves headers and cell relationships

3. **Row Chunking** (`row_chunker.py`)
   - Converts table rows into searchable chunks
   - Adds metadata (source, page, criterion)

4. **Index Building** (`institution_indexer.py`)
   - Creates FAISS vector index for semantic search
   - Creates BM25 index for keyword search
   - Stores metadata in SQLite database

## Expected Output

After successful ingestion, you'll see in the backend logs:

```
============================================================
INSTITUTION DOCUMENT INGESTION
============================================================
Found 1 PDF file(s) to process

--- Processing: Riverton_Bplus_SSR.pdf ---
  Parsed 50 pages
  Found 25 tables
  Extracted 25 tables
  Created 150 chunks

--- Building Indexes ---
Total chunks to index: 150
  FAISS index built and saved
  BM25 index built and saved
  Metadata saved to database

============================================================
INGESTION COMPLETE
============================================================
Files processed: 1
Chunks created: 150
```

## Verification

Check if ingestion worked:

```bash
# Check institution index files exist
ls accreditation_copilot/indexes/institution/

# Should see:
# - institution.index (FAISS)
# - institution_bm25.pkl (BM25)
# - institution_mapping.pkl (ID mapping)

# Check database
sqlite3 accreditation_copilot/data/metadata.db "SELECT COUNT(*) FROM chunks WHERE doc_type='institutional'"

# Should return a number > 0
```

## Troubleshooting

### Issue: Still getting "File ingestion failed"
**Solution**: Check backend logs for specific error. Common issues:
- Missing dependencies (install with `pip install -r api/requirements.txt`)
- PDF parsing errors (check if PDF is valid)
- Disk space issues

### Issue: Ingestion succeeds but still 0% scores
**Solution**: 
1. Verify indexes exist: `ls indexes/institution/`
2. Check database: `sqlite3 data/metadata.db "SELECT COUNT(*) FROM chunks WHERE doc_type='institutional'"`
3. Restart backend to reload indexes

### Issue: "No PDF files found"
**Solution**: Check that your PDF is in `data/raw_docs/` folder:
```bash
ls accreditation_copilot/data/raw_docs/
```

## Alternative: Manual Ingestion

If the button still doesn't work, run manually:

```bash
cd accreditation_copilot
python ingestion/institution/run_institution_ingestion.py
```

## Next Steps

1. Restart backend (see Step 1 above)
2. Refresh frontend
3. Click "Ingest Files"
4. Wait for success message
5. Run audit again
6. See real results! 🎉

## Files Modified Summary
- ✅ Created: `ingestion/institution/run_institution_ingestion.py`
- ✅ Modified: `api/routers/upload.py`
- ✅ Modified: `audit/audit_enricher.py` (from previous fix)
- ✅ Modified: `frontend/components/QueryPanel.tsx` (from previous fix)
