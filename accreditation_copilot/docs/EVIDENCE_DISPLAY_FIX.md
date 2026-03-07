# Evidence Display Fix - Complete ✅

## Issues Found

### 1. Evidence Shows "Unknown Source" and "No text available"
**Root Cause**: The `audit_enricher.py` was returning field names that didn't match what the frontend expected:
- Backend returned: `source_path`, `page_number`
- Frontend expected: `source`, `page`, `text`
- Text content was missing entirely

**Fix**: Updated `audit_enricher.py` to:
- Use correct field names (`source`, `page`)
- Include text content from retrieval results
- Add strength indicator based on reranker score

### 2. 0% Confidence and 0% Coverage
**Root Cause**: Uploaded files haven't been ingested yet. The system needs to:
1. Process PDFs (extract text and tables)
2. Create semantic chunks
3. Generate embeddings
4. Index in FAISS
5. Store metadata in SQLite

**Fix**: Added "Ingest Files" button to trigger the ingestion pipeline after upload.

## Changes Made

### Backend Fix: `audit/audit_enricher.py`
```python
def enrich_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched_sources = []
    for result in results:
        chunk_id = result.get('chunk_id')
        if not chunk_id:
            continue
        
        metadata = self._get_chunk_metadata(chunk_id)
        text_content = result.get('text') or result.get('child_text', 'No text available')
        
        if metadata:
            enriched_sources.append({
                'chunk_id': chunk_id,
                'source': metadata['source'],  # ✅ Correct field name
                'page': metadata['page'],  # ✅ Correct field name
                'source_type': metadata['source_type'],
                'criterion': metadata.get('criterion', 'N/A'),
                'framework': metadata['framework'],
                'text': text_content,  # ✅ Include text
                'reranker_score': round(result.get('scores', {}).get('reranker', 0.0), 3),
                'strength': self._determine_strength(...)  # ✅ Add strength
            })
    return enriched_sources
```

### Frontend Fix: `frontend/components/QueryPanel.tsx`
Added ingestion functionality:
```typescript
// New function to trigger ingestion
const handleIngestFiles = async () => {
  const response = await fetch('http://localhost:8000/api/upload/ingest', {
    method: 'POST',
  });
  // ... handle response
};

// New button in UI
<button onClick={handleIngestFiles}>Ingest Files</button>
```

## How to Use

### Step 1: Upload Files
1. Click the upload button (📤 icon)
2. Select PDF/PNG/JPG files
3. Files appear in the uploaded files list

### Step 2: Ingest Files
1. Click the "Ingest Files" button (appears after upload)
2. Wait for processing (1-5 minutes depending on file size)
3. You'll see a success message when complete

### Step 3: Run Audit
1. Select framework (NAAC or NBA)
2. Enter criterion (e.g., "3.2.1")
3. Click "Run Audit"
4. View results with actual evidence!

## Expected Results After Ingestion

### Before Ingestion
- ❌ Confidence: 0%
- ❌ Coverage: 0%
- ❌ Status: "Weak"
- ❌ Evidence: "Unknown Source", "No text available"

### After Ingestion
- ✅ Confidence: 40-80% (varies by evidence quality)
- ✅ Coverage: 50-90% (varies by dimension coverage)
- ✅ Status: "Partial" or "Compliant"
- ✅ Evidence: Actual text from your documents
- ✅ Source: Real file names and page numbers
- ✅ Strength: "Strong", "Moderate", or "Weak" indicators

## Alternative: Manual Ingestion

If the button doesn't work, run ingestion manually:

```bash
cd accreditation_copilot
python ingestion/run_ingestion.py
```

Or via API:
```bash
curl -X POST http://localhost:8000/api/upload/ingest
```

## Verification

Check if ingestion worked:

```bash
# Check institution index exists
ls indexes/institution/

# Check metadata database
sqlite3 data/metadata.db "SELECT COUNT(*) FROM chunks WHERE doc_type='institutional'"
```

You should see:
- `institution.index` file
- `institution_bm25.pkl` file
- `institution_mapping.pkl` file
- Non-zero count of institutional chunks

## Files Modified
- `accreditation_copilot/audit/audit_enricher.py` - Fixed field names and added text content
- `accreditation_copilot/frontend/components/QueryPanel.tsx` - Added ingestion button
- `accreditation_copilot/DATA_INGESTION_GUIDE.md` - Created comprehensive guide (NEW)
- `accreditation_copilot/EVIDENCE_DISPLAY_FIX.md` - This file (NEW)

## Next Steps
1. Restart backend if running: `uvicorn api.main:app --host 0.0.0.0 --port 8000`
2. Refresh frontend: http://localhost:3000
3. Upload files
4. Click "Ingest Files"
5. Run audit
6. See real evidence! 🎉
