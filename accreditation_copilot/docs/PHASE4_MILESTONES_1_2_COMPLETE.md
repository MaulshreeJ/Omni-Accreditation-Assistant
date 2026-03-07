# Phase 4 - Milestones 1 & 2 Complete

## Status: ✅ MILESTONES 1 & 2 COMPLETE

**Date**: March 5, 2026  
**Milestones Completed**: 1 (Index Infrastructure) + 2 (Institution PDF Ingestion)

---

## MILESTONE 1 — INDEX INFRASTRUCTURE ✅

### Changes Made

1. **Created new directory structure**:
   ```
   indexes/
   ├── framework/     (all existing framework indexes moved here)
   └── institution/   (empty, ready for Phase 4 indexes)
   ```

2. **Updated index_loader.py**:
   - Added `framework_index_dir` and `institution_index_dir` paths
   - Updated `load_faiss_index()` to look in `framework/` subdirectory
   - Updated `load_bm25_index()` to look in `framework/` subdirectory

3. **Validation**:
   - All framework indexes load correctly from new location
   - Phase 3 pipeline unaffected
   - Test: `test_milestone1.py` - PASS

### Test Results

```
MILESTONE 1 VALIDATION: PASS
- Framework index dir: indexes\framework
- Institution index dir: indexes\institution
- Loaded NAAC metric index: 517 vectors
- Loaded NBA policy index: 145 vectors
- All framework indexes accessible
```

---

## MILESTONE 2 — INSTITUTION PDF INGESTION PIPELINE ✅

### Modules Created

#### 1. `ingestion/institution/pdf_parser.py`
- Extracts text using PyMuPDF (fitz)
- Extracts tables using pdfplumber
- Returns structured page data with text_blocks and tables
- **Note**: Requires `pdfplumber` installation (added to requirements.txt)

#### 2. `ingestion/institution/table_extractor.py`
- Converts raw pdfplumber tables into structured format
- Normalizes whitespace and empty cells
- Extracts headers and data rows
- Filters out empty rows

#### 3. `ingestion/institution/row_chunker.py`
- Converts each table row into searchable chunk
- Chunks paragraphs with 600 token target, 100 token overlap
- Generates UUIDs for each chunk
- Sets `source_type = "institution"` and `doc_type = "institutional"`

### Critical Checkpoint: First Ingestion Output

**Sample chunks saved to**: `data/institution_chunks_sample.json`

**Table Row Chunk Example**:
```json
{
  "chunk_id": "578d07d2-3266-4249-ad9a-482c241de305",
  "text": "S.No: 1 | Year: 2022-23 | Project Title: AI in Education Research | Funding Agency: DST | Amount (INR Lakhs): 24.5 | Duration: 2 years",
  "structured_data": {
    "S.No": "1",
    "Year": "2022-23",
    "Project Title": "AI in Education Research",
    "Funding Agency": "DST",
    "Amount (INR Lakhs)": "24.5",
    "Duration": "2 years"
  },
  "chunk_type": "table_row",
  "source_type": "institution",
  "doc_type": "institutional",
  "table_id": "page45_table2",
  "row_id": 0,
  "page": 45,
  "source": "SSR_Evidence.pdf",
  "framework": null,
  "criterion": null
}
```

**Paragraph Chunk Example**:
```json
{
  "chunk_id": "ae2803b1-f70e-4862-a2f1-1d92b65f30d5",
  "text": "The institution has received significant extramural funding for research projects during the assessment period. The Department of Science and Technology (DST) sanctioned Rs. 24.5 lakhs for AI in Education Research project in 2022-23...",
  "chunk_type": "paragraph",
  "source_type": "institution",
  "doc_type": "institutional",
  "page": 45,
  "source": "SSR_Evidence.pdf",
  "framework": null,
  "criterion": null
}
```

### Validation Results

```
MILESTONE 2 VALIDATION: PASS
- Table Extractor: 4 rows extracted
- Row Chunker: 4 table row chunks created
- Paragraph Chunker: 1 paragraph chunk created
- Total chunks: 5
- All chunks have required fields
- All chunks have correct source_type='institution'
- All chunks have correct doc_type='institutional'
```

### Key Features

1. ✅ **Table rows as independent chunks**: Each row is searchable
2. ✅ **Structured data preserved**: Original table structure maintained
3. ✅ **Readable text format**: "Field: Value | Field: Value..."
4. ✅ **Proper metadata**: source_type, doc_type, page, source all set correctly
5. ✅ **Paragraph chunking**: Long text split with overlap
6. ✅ **UUID generation**: Unique IDs for each chunk

---

## Architecture Impact

### Before Phase 4
```
indexes/
├── naac_metric.index
├── naac_policy.index
├── nba_metric.index
└── ...
```

### After Milestone 1
```
indexes/
├── framework/
│   ├── naac_metric.index
│   ├── naac_policy.index
│   ├── nba_metric.index
│   └── ...
└── institution/
    └── (empty, ready for Milestone 3)
```

### After Milestone 2
```
ingestion/
├── institution/
│   ├── __init__.py
│   ├── pdf_parser.py          (PyMuPDF + pdfplumber)
│   ├── table_extractor.py     (normalize tables)
│   └── row_chunker.py          (chunk rows + paragraphs)
```

---

## Next Steps

### MILESTONE 3 — INSTITUTION INDEX BUILDER

**To Implement**:
1. Create `ingestion/institution/institution_indexer.py`
2. Build FAISS index using BAAI/bge-base-en-v1.5 (same as framework)
3. Build BM25 index
4. Create SQLite metadata database
5. Save indexes to `indexes/institution/`
6. Test retrieval manually

**Expected Output**:
- `indexes/institution/institution.index`
- `indexes/institution/institution_bm25.pkl`
- `indexes/institution/institution_mapping.pkl`
- Metadata in `data/metadata.db` with `source_type='institution'`

---

## Dependencies Added

- `pdfplumber==0.11.0` (added to requirements.txt)
- Requires: `pip install pdfplumber`

---

## Files Created

### Milestone 1
- Modified: `retrieval/index_loader.py`
- Test: `tests/test_milestone1.py`

### Milestone 2
- Created: `ingestion/institution/__init__.py`
- Created: `ingestion/institution/pdf_parser.py`
- Created: `ingestion/institution/table_extractor.py`
- Created: `ingestion/institution/row_chunker.py`
- Test: `tests/test_milestone2.py`
- Output: `data/institution_chunks_sample.json`

---

## Validation Status

| Milestone | Status | Test | Result |
|-----------|--------|------|--------|
| M1 - Index Infrastructure | ✅ PASS | test_milestone1.py | All framework indexes load correctly |
| M2 - Institution Ingestion | ✅ PASS | test_milestone2.py | 5 chunks generated with correct metadata |

---

## Critical Success Factors

1. ✅ **Never flatten tables**: Each row is independent chunk
2. ✅ **Preserve structure**: structured_data field maintains original format
3. ✅ **Correct metadata**: source_type='institution', doc_type='institutional'
4. ✅ **Searchable text**: Readable format for retrieval
5. ✅ **Phase 3 unaffected**: Framework indexes still work

---

**Status**: Ready for Milestone 3 (Institution Index Builder)
