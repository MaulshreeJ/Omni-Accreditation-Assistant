# Next Step: Click "Ingest Files" Button

## What You See Now ✅
- ✅ File uploaded: `Riverton_Bplus_SSR.pdf`
- ✅ "Ingest Files" button is visible (pink button in top right)
- ✅ Audit ran but shows 0% scores
- ✅ Evidence shows "Unknown Source"

## What To Do Next

### Click the "Ingest Files" Button
1. Look for the pink "Ingest Files" button in the top right corner (next to uploaded files)
2. Click it
3. Wait 1-5 minutes (you'll see "Processing..." message)
4. You'll get an alert: "Files ingested successfully!"

### Then Run Audit Again
1. Click "Run Audit" button again
2. This time you'll see:
   - ✅ Confidence: 40-80%
   - ✅ Coverage: 50-90%
   - ✅ Status: "Partial" or "Compliant"
   - ✅ Evidence with actual text from your PDF
   - ✅ Real source names and page numbers

## What Ingestion Does

The ingestion process:
1. **Reads your PDF** - Extracts all text and tables
2. **Creates chunks** - Breaks content into semantic chunks
3. **Generates embeddings** - Creates vector representations
4. **Builds index** - Adds to FAISS search index
5. **Stores metadata** - Saves source info to database

This takes 1-5 minutes depending on PDF size.

## Troubleshooting

### If Button Doesn't Work
Try manual ingestion:
```bash
cd accreditation_copilot
python ingestion/run_ingestion.py
```

### If Still Shows 0% After Ingestion
Check if ingestion completed:
```bash
# Check institution index exists
ls accreditation_copilot/indexes/institution/

# Should see:
# - institution.index
# - institution_bm25.pkl
# - institution_mapping.pkl
```

### If You Get an Error
Check backend logs in the terminal where you ran:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Look for error messages during ingestion.

## Expected Timeline

- **Click "Ingest Files"**: Immediate
- **Processing time**: 1-5 minutes
- **Success alert**: "Files ingested successfully!"
- **Run audit again**: Immediate
- **See real results**: Immediate

## Why This Is Needed

The system has two types of evidence:
1. **Framework evidence** (NAAC/NBA guidelines) - Always available ✅
2. **Institution evidence** (your documents) - Needs ingestion ⚠️

Without ingestion, the system can only compare against framework guidelines, which gives 0% scores because there's no institutional evidence to evaluate.

After ingestion, the system can:
- Find relevant evidence in your documents
- Calculate confidence based on evidence quality
- Measure coverage of criterion dimensions
- Identify specific gaps in your documentation

## What You'll See After Ingestion

### Audit Results
- Confidence: Actual percentage (not 0%)
- Coverage: Actual percentage (not 0%)
- Status: "Compliant", "Partial", or "Weak" (not just "Weak")

### Evidence Section
- Source: "Riverton_Bplus_SSR.pdf" (not "Unknown Source")
- Page: Actual page numbers (not empty)
- Text: Real content from your PDF (not "No text available")
- Strength: "Strong", "Moderate", or "Weak" indicators

### Gap Analysis
- Specific missing dimensions
- Actionable recommendations
- Severity levels (High/Medium/Low)

## Ready?

**Just click the "Ingest Files" button and wait!** 🚀

The button is in the top right corner of the uploaded files section (pink/gradient colored).
