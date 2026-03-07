# Quick Fix Summary - Evidence Display Issue

## What You're Seeing
- ✅ Audit runs successfully
- ❌ Shows 0% confidence and 0% coverage
- ❌ Evidence displays "Unknown Source" and "No text available"
- ❌ Status shows "Weak"

## Why This Happens
Your uploaded file (`Riverton_Bplus_SSR.pdf`) hasn't been **ingested** yet. Uploading just saves the file - ingestion processes it and makes it searchable.

## The Fix (2 Steps)

### Step 1: Restart Backend with Fix
The backend code has been updated. Restart it:

**Terminal 1:**
```bash
cd accreditation_copilot
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Step 2: Ingest Your Files
After the backend restarts, you have two options:

**Option A: Use the New Button (Easiest)**
1. Refresh the UI (http://localhost:3000)
2. You'll see an "Ingest Files" button next to your uploaded files
3. Click it and wait 1-5 minutes
4. Run the audit again

**Option B: Use Command Line**
```bash
cd accreditation_copilot
python ingestion/run_ingestion.py
```

## What Changed

### Backend (`audit/audit_enricher.py`)
- ✅ Fixed field names to match frontend expectations
- ✅ Added text content to evidence
- ✅ Added strength indicators (Strong/Moderate/Weak)

### Frontend (`components/QueryPanel.tsx`)
- ✅ Added "Ingest Files" button
- ✅ Connected to ingestion API endpoint
- ✅ Shows processing status

## After Ingestion, You'll See:
- ✅ Confidence: 40-80% (actual score based on your evidence)
- ✅ Coverage: 50-90% (actual coverage of criterion dimensions)
- ✅ Status: "Partial" or "Compliant" (based on scores)
- ✅ Evidence: Real text from your PDF
- ✅ Source: Actual filename and page numbers
- ✅ Strength: Color-coded indicators

## Troubleshooting

**Q: Ingestion button doesn't appear**
A: Refresh the page after restarting the backend

**Q: Ingestion fails**
A: Check that `Riverton_Bplus_SSR.pdf` is in `data/raw_docs/` folder

**Q: Still shows 0% after ingestion**
A: Check backend logs for errors during ingestion

**Q: How do I know ingestion worked?**
A: Run this command:
```bash
ls accreditation_copilot/indexes/institution/
```
You should see: `institution.index`, `institution_bm25.pkl`, `institution_mapping.pkl`

## Files to Read
- `EVIDENCE_DISPLAY_FIX.md` - Detailed technical explanation
- `DATA_INGESTION_GUIDE.md` - Complete ingestion guide
- `BUTTON_FIX_COMPLETE.md` - Previous button fixes

## Quick Test
After ingestion, test with:
```bash
curl -X POST http://localhost:8000/api/audit/run \
  -H "Content-Type: application/json" \
  -d '{"framework":"NAAC","criterion":"3.2.1"}'
```

Look for `confidence_score` > 0 and `evidence` array with text content.
