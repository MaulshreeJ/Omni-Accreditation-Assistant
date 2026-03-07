# Manual Ingestion Guide - Bypass the Button

Since the "Ingest Files" button is still failing, let's run ingestion manually from the command line.

## Quick Fix: Run Ingestion Manually

### Step 1: Open a New Terminal

Open a new terminal/command prompt window (keep the backend and frontend running in their terminals).

### Step 2: Navigate to the Project

```bash
cd accreditation_copilot
```

### Step 3: Run the Ingestion Script

```bash
python ingestion/institution/run_institution_ingestion.py
```

### Step 4: Wait for Completion

You'll see output like:
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
Loading embedding model on cpu...
Model loaded. Embedding dimension: 768
  FAISS index built and saved
  BM25 index built and saved
  Metadata saved to database

============================================================
INGESTION COMPLETE
============================================================
Files processed: 1
Chunks created: 150
```

### Step 5: Run Audit Again

Go back to the UI (http://localhost:3000) and click "Run Audit" again. You should now see real results!

## Why the Button Fails

The button is failing because:
1. The backend might not have been restarted with the new code
2. There might be missing Python dependencies
3. The PDF parsing libraries might need additional setup

## Alternative: Restart Backend with New Code

If you want to fix the button:

### Step 1: Stop the Backend

In the terminal running the backend, press `Ctrl+C`

### Step 2: Restart the Backend

```bash
cd accreditation_copilot
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Step 3: Try the Button Again

Refresh the UI and click "Ingest Files"

## Checking If Ingestion Worked

After running manual ingestion, verify it worked:

```bash
# Check if index files exist
ls indexes/institution/

# Should see:
# institution.index
# institution_bm25.pkl
# institution_mapping.pkl

# Check database
sqlite3 data/metadata.db "SELECT COUNT(*) FROM chunks WHERE doc_type='institutional'"

# Should return a number > 0
```

## Common Issues

### Issue: "No module named 'sentence_transformers'"

**Fix:**
```bash
pip install sentence-transformers
```

### Issue: "No module named 'faiss'"

**Fix:**
```bash
pip install faiss-cpu
```

### Issue: "No module named 'rank_bm25'"

**Fix:**
```bash
pip install rank-bm25
```

### Issue: "No PDF files found"

**Fix:** Check that your PDF is in the right location:
```bash
ls data/raw_docs/
```

If it's not there, the upload didn't work. Re-upload the file.

### Issue: PDF parsing fails

**Fix:** Install PDF parsing dependencies:
```bash
pip install pypdf2 pdfplumber
```

## After Successful Ingestion

Once ingestion completes successfully:

1. Go to http://localhost:3000
2. Click "Run Audit"
3. You'll see:
   - ✅ Confidence: 40-80%
   - ✅ Coverage: 50-90%
   - ✅ Evidence with real text
   - ✅ Proper source names

## Still Having Issues?

If manual ingestion also fails, check:

1. **Python version**: Should be Python 3.8+
   ```bash
   python --version
   ```

2. **Virtual environment**: Make sure you're in the venv
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Dependencies**: Install all requirements
   ```bash
   pip install -r api/requirements.txt
   ```

4. **PDF file**: Make sure it's a valid PDF
   ```bash
   # Check file size
   ls -lh data/raw_docs/Riverton_Bplus_SSR.pdf
   ```

## Success Indicators

You'll know ingestion worked when:
- ✅ Script completes without errors
- ✅ Shows "INGESTION COMPLETE"
- ✅ Index files exist in `indexes/institution/`
- ✅ Database has institutional chunks
- ✅ Audit shows non-zero scores

## Next Steps

After successful manual ingestion:
1. Run audits from the UI
2. See real evidence and scores
3. Analyze gaps and recommendations
4. Upload more documents if needed
5. Re-run ingestion to index new documents
