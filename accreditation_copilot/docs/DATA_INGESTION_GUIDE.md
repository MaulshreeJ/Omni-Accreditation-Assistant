# Data Ingestion Guide

## Problem: 0% Confidence and Coverage

If you see audit results showing:
- 0% Confidence
- 0% Coverage  
- "Weak" status
- Evidence showing "Unknown Source" or "No text available"

This means **institutional evidence has not been ingested yet**.

## Solution: Ingest Your Documents

### Step 1: Upload Files
You've already uploaded `Riverton_Bplus_SSR.pdf` - great!

### Step 2: Trigger Ingestion

The uploaded files need to be processed and indexed. You have two options:

#### Option A: Use the API Endpoint (Recommended)
```bash
curl -X POST http://localhost:8000/api/upload/ingest
```

#### Option B: Run Ingestion Script Manually
```bash
cd accreditation_copilot
python ingestion/run_ingestion.py
```

### What Ingestion Does
1. **PDF Processing**: Extracts text and tables from PDFs
2. **Semantic Chunking**: Breaks content into meaningful chunks
3. **Embedding**: Creates vector embeddings for each chunk
4. **Indexing**: Adds chunks to the FAISS index for fast retrieval
5. **Metadata Storage**: Stores source information in SQLite database

### After Ingestion
Once ingestion completes, run the audit again:
- Confidence and Coverage scores will be calculated
- Evidence will show actual text from your documents
- Source information will be accurate
- Gap analysis will be meaningful

## Current System State

### Framework Evidence (Always Available)
- ✅ NAAC guidelines indexed
- ✅ NBA guidelines indexed
- ✅ Ready for retrieval

### Institution Evidence (Needs Ingestion)
- ⚠️ Files uploaded but not yet processed
- ⚠️ Run ingestion to make them searchable

## Expected Results After Ingestion

For NAAC Criterion 3.2.1:
- Confidence: 40-80% (depending on evidence quality)
- Coverage: 50-90% (depending on dimension coverage)
- Status: "Partial" or "Compliant"
- Evidence: 5-8 chunks with actual text
- Gaps: Specific missing dimensions identified

## Troubleshooting

### Issue: Ingestion Fails
**Check:**
- PDF files are in `data/raw_docs/`
- Files are valid PDFs (not corrupted)
- Sufficient disk space available

### Issue: Still 0% After Ingestion
**Check:**
- Ingestion completed successfully (check logs)
- Institution index files exist in `indexes/institution/`
- Metadata database has entries: `sqlite3 data/metadata.db "SELECT COUNT(*) FROM chunks WHERE doc_type='institutional'"`

### Issue: Evidence Shows But Scores Are Low
**This is normal!** It means:
- Your institution documents don't have strong evidence for this criterion
- The gap analysis will tell you what's missing
- You need to add more relevant documentation

## Quick Test

After ingestion, test with a simple query:
```bash
curl -X POST http://localhost:8000/api/audit/run \
  -H "Content-Type: application/json" \
  -d '{"framework":"NAAC","criterion":"3.2.1"}'
```

You should see:
- `confidence_score` > 0
- `coverage_ratio` > 0
- `evidence_count` > 0
- `evidence` array with actual text content

## Next Steps

1. Run ingestion (see Step 2 above)
2. Wait for completion (may take 1-5 minutes depending on file size)
3. Run audit again from the UI
4. Review evidence and gaps
5. Upload additional documents if needed
6. Re-run ingestion and audit
