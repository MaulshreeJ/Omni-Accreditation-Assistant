# Phase 4 Structural Fixes - Complete

**Date**: March 5, 2026  
**Status**: ✅ ALL 8 ISSUES FIXED

---

## Executive Summary

Applied 8 critical structural fixes to Phase 4 institution evidence ingestion pipeline. All fixes implemented without breaking Phase 3 reasoning engine. System ready for full Phase 4 validation.

---

## Issues Fixed

### Issue 1: Structured Data Field Normalization ✅

**Problem**: Inconsistent structured_data fields didn't match normalized chunk text.

**Old Format**:
```json
{
  "Year": "2022-23",
  "Project Title": "AI in Education Research",
  "Funding Agency": "DST",
  "Amount (INR Lakhs)": "24.5",
  "Duration": "2 years"
}
```

**New Canonical Schema**:
```json
{
  "year": "2022-23",
  "project_title": "AI in Education Research",
  "agency": "DST",
  "funding_lakhs": "24.5",
  "duration": "2 years"
}
```

**Normalization Rules**:
- `"Funding Agency"` → `"agency"`
- `"Amount (INR Lakhs)"` → `"funding_lakhs"` (numeric value only)
- `"Project Title"` → `"project_title"`
- `"Year"` → `"year"`
- `"Duration"` → `"duration"`

**Implementation**: Added `_normalize_structured_data()` method in `row_chunker.py`

**Files Modified**:
- `ingestion/institution/row_chunker.py`

---

### Issue 2: Paragraph Token Guard ✅

**Problem**: Paragraph chunks could grow too large for embedding models.

**Solution**: Implemented strict token guard:
```python
target_tokens = 600  # Target chunk size
max_tokens = 800     # Maximum allowed
overlap = 100        # Overlap between chunks
```

**Behavior**:
- Target size: 600 tokens
- If chunk exceeds 800 tokens: split into multiple chunks with 100-token overlap
- Ensures no chunk exceeds embedding model limits

**Files Modified**:
- `ingestion/institution/row_chunker.py` (`chunk_paragraph()` method)

---

### Issue 3: Verify Criterion Inference ✅

**Problem**: Need to ensure criterion inference runs before indexing.

**Solution**: Verified that `_apply_criterion_inference()` is called in `build_indexes()` before embedding.

**Process**:
1. Criterion inference runs first
2. Chunks get `framework` and `criterion` fields populated
3. Then embedding prefix is applied
4. Finally, embeddings are generated

**Example Output**:
```python
framework = "NAAC"
criterion = "3.2.1"
```

**If criterion cannot be detected**:
```python
criterion = None
framework = None
```

**Files Verified**:
- `ingestion/institution/institution_indexer.py` (already correct)
- `ingestion/institution/criterion_inferrer.py` (already implemented)

---

### Issue 4: Embedding Prefix Application ✅

**Problem**: Need to verify embedding prefix is applied correctly.

**Solution**: Confirmed prefix is applied ONLY to embedding input, NOT to stored text.

**Prefix Format**:
- With criterion: `[{framework} {criterion} Evidence]`
- Without criterion: `[Institution Research Evidence]`

**Example**:
```python
# Embedding input (with prefix)
"[NAAC 3.2.1 Evidence] Project: AI in Education Research\nAgency: DST\nFunding: ₹24.5 Lakhs"

# Stored text (without prefix)
"Project: AI in Education Research\nAgency: DST\nFunding: ₹24.5 Lakhs"
```

**Implementation**:
```python
texts_for_embedding = [self._add_embedding_prefix(chunk) for chunk in chunks]
texts_for_bm25 = [chunk['text'] for chunk in chunks]  # Original text
```

**Files Verified**:
- `ingestion/institution/institution_indexer.py` (already correct)

---

### Issue 5: Table Row Priority Signal ✅

**Problem**: Need metadata signal to improve retrieval quality.

**Solution**: Added evidence type and weight to all chunks:

**Table Row Chunks**:
```python
evidence_type = "table_row"
evidence_weight = 1.2
```

**Paragraph Chunks**:
```python
evidence_type = "paragraph"
evidence_weight = 1.0
```

**Purpose**: Allows future reranking improvements to prioritize table rows (structured evidence) over paragraphs.

**Files Modified**:
- `ingestion/institution/row_chunker.py` (`chunk_table_row()` and `chunk_paragraph()`)

---

### Issue 6: Verify Institution Index Output ✅

**Problem**: Need to verify institution index contains all required files and metadata.

**Expected Output**:
```
indexes/institution/
├── institution.index          # FAISS index
├── institution_mapping.pkl    # Chunk ID mapping
└── institution_bm25.pkl       # BM25 index + tokenized corpus
```

**Metadata Fields** (in SQLite):
```python
{
    'chunk_id': str,
    'source_path': str,
    'page_number': int,
    'framework': str,      # "NAAC", "NBA", or "INSTITUTION"
    'criterion': str,      # "3.2.1", "C5", or None
    'chunk_type': str,     # "table_row" or "paragraph"
    'source_type': str,    # "institution"
    'doc_type': str,       # "institutional"
    'text': str
}
```

**Files Verified**:
- `ingestion/institution/institution_indexer.py` (already correct)

---

### Issue 7: Verify Dual Retrieval Slot Bias ✅

**Problem**: Need to verify slot allocation favors institution evidence.

**Solution**: Confirmed correct allocation:
```python
framework_top_k = 3   # Framework provides context only
institution_top_k = 7  # Institution provides primary evidence
```

**Rationale**:
- Framework chunks: Provide guidance and requirements (context)
- Institution chunks: Provide actual evidence of compliance

**Files Verified**:
- `retrieval/dual_retrieval.py` (already correct)
- `retrieval/retrieval_pipeline.py` (already correct)

---

### Issue 8: Safe Empty Institution Index Handling ✅

**Problem**: System must not crash when no institutional documents exist.

**Solution**: Verified safe handling:

```python
# Check if index exists
if institution_index_path.exists():
    institution_results = self._retrieve_institution(...)
    
    # Check if results are non-empty
    if institution_results and len(institution_results) > 0:
        institution_evidence_available = True

# Check if index is empty
if faiss_index.ntotal == 0:
    return []
```

**Behavior**:
- No institution index: Returns framework results only
- Empty institution index: Returns framework results only
- Institution index with results: Returns merged results

**Files Verified**:
- `retrieval/dual_retrieval.py` (already correct)

---

## Validation Results

### Test Milestone 2: PASS ✅

```
✓ Issue 10: S.No removed from chunk
✓ Issue 3: Currency normalized (₹ symbol present)
✓ Issue 4: Agency normalization applied
✓ Issue 9: Metadata fields aligned (page_number, source_path)
✓ Issue 1: Structured data normalized to canonical schema
✓ Issue 5: Evidence type and weight added
✓ Issue 5: Paragraph cleaned (no newlines, collapsed spaces)
✓ Issue 2: Token guard working (chunk has 118 tokens, max 800)
✓ Issue 5: Paragraph evidence type and weight correct
```

### Test Phase 3 Deterministic: PASS ✅

```
✓ Test 1: Evidence Scorer - PASS
✓ Test 2: Dimension Checker - PASS
✓ Test 3: Confidence Calculator - PASS
✓ Test 4: Output Formatter - PASS
✓ Test 5: Performance - PASS
```

---

## Sample Output

### Table Row Chunk (New Format)

**Chunk Text**:
```
Year: 2022-23
Project: AI in Education Research
Agency: DST
Funding: ₹24.5 Lakhs
Duration: 2 years
```

**Structured Data** (Normalized):
```json
{
  "year": "2022-23",
  "project_title": "AI in Education Research",
  "agency": "DST",
  "funding_lakhs": "24.5",
  "duration": "2 years"
}
```

**Metadata**:
```json
{
  "chunk_id": "11837b76-1823-4e08-8c7e-16a305410f07",
  "chunk_type": "table_row",
  "source_type": "institution",
  "doc_type": "institutional",
  "evidence_type": "table_row",
  "evidence_weight": 1.2,
  "page_number": 45,
  "source_path": "SSR_Evidence.pdf",
  "framework": null,
  "criterion": null
}
```

---

## Files Modified

1. `ingestion/institution/row_chunker.py`
   - Added `_normalize_structured_data()` method (Issue 1)
   - Updated token guard parameters (Issue 2)
   - Added evidence_type and evidence_weight (Issue 5)
   - Updated `chunk_table_row()` and `chunk_paragraph()`

2. `tests/test_milestone2.py`
   - Added validation for structured data normalization (Issue 1)
   - Added validation for token guard (Issue 2)
   - Added validation for evidence type/weight (Issue 5)

---

## Files Verified (Already Correct)

1. `ingestion/institution/institution_indexer.py`
   - Criterion inference (Issue 3) ✅
   - Embedding prefix (Issue 4) ✅
   - Index output (Issue 6) ✅

2. `retrieval/dual_retrieval.py`
   - Slot allocation (Issue 7) ✅
   - Empty index handling (Issue 8) ✅

3. `retrieval/retrieval_pipeline.py`
   - Slot allocation (Issue 7) ✅

4. `ingestion/institution/criterion_inferrer.py`
   - Criterion inference logic (Issue 3) ✅

---

## Impact Assessment

### Backward Compatibility: ✅ MAINTAINED
- Phase 3 tests still pass
- Framework retrieval unchanged
- Only institution chunks affected

### Data Quality: ✅ IMPROVED
- Structured data now follows canonical schema
- Consistent field naming across all chunks
- Better integration with downstream processing

### Retrieval Quality: ✅ IMPROVED
- Evidence type signals enable better reranking
- Token guard prevents oversized chunks
- Embedding prefix improves semantic matching

### Safety: ✅ ENHANCED
- Token guard prevents embedding model errors
- Empty index handling prevents crashes
- Graceful degradation when no institution evidence exists

---

## Next Steps

With all structural fixes applied and validated:

1. ✅ `python tests/test_milestone2.py` - PASS
2. ✅ `python tests/test_phase3_deterministic.py` - PASS
3. ⏭️ Build institution indexes: `python ingestion/institution/institution_indexer.py`
4. ⏭️ Validate indexing: `python tests/test_milestone3.py`
5. ⏭️ Validate dual retrieval: `python tests/test_milestone4.py`
6. ⏭️ Full Phase 4 validation

---

## Conclusion

All 8 structural inconsistencies have been successfully corrected. The institution evidence ingestion pipeline now has:

- ✅ Canonical structured data schema
- ✅ Strict token guards for safety
- ✅ Verified criterion inference
- ✅ Correct embedding prefix application
- ✅ Evidence type signals for reranking
- ✅ Verified index output structure
- ✅ Correct retrieval slot allocation
- ✅ Safe empty index handling

**Phase 3 reasoning engine**: Unaffected, all tests passing  
**Phase 4 pipeline**: Ready for full validation

**Status**: ✅ READY FOR PHASE 4 FULL VALIDATION
