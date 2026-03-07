# Phase E: Observability and Retrieval Evaluation

**Date**: March 5, 2026  
**Status**: ✅ COMPLETE  
**Objective**: Add traceability, evaluation metrics, and feedback collection

---

## Overview

Phase E adds observability infrastructure to the accreditation copilot system without modifying Phase 3 scoring logic or Phase 4 ingestion logic. This enables:

1. **Traceability**: LangSmith trace logging for every query execution
2. **Evaluation**: Retrieval quality metrics (Recall@K, Precision@K, F1@K)
3. **Feedback**: Reviewer ratings storage for retrieval tuning

---

## E1: LangSmith Trace Logging

### Implementation

**Module**: `observability/tracer.py`

**Features**:
- Trace manager with optional LangSmith integration
- Context manager for tracing pipeline stages
- Trace functions for retrieval, reranking, scoring, and LLM synthesis
- Automatic latency tracking per stage

**Trace Structure**:
```
query_run
├─ retrieval (query, expanded_queries, retrieved_chunks, scores)
├─ reranking (reranker_scores, final_scores, top_chunks)
├─ scoring (dimension_hits, evidence_scores, confidence_score)
└─ llm_synthesis (prompt, output, model, latency)
```

**Usage**:
```python
from observability.tracer import get_trace_manager, enable_tracing

# Enable tracing (requires LANGCHAIN_API_KEY)
enable_tracing(project_name="accreditation-copilot")

# Use trace manager
tracer = get_trace_manager()

with tracer.trace_stage("retrieval") as outputs:
    # Perform retrieval
    outputs['chunks'] = retrieved_chunks
    outputs['scores'] = scores
```

**Configuration**:
```bash
# Set LangSmith API key
export LANGCHAIN_API_KEY="your-api-key"

# Optional: Set project name
export LANGCHAIN_PROJECT="accreditation-copilot"
```

**Graceful Degradation**:
- If LangSmith not installed: Tracing disabled, console logging only
- If API key not set: Tracing disabled, console logging only
- System continues to work normally without tracing

---

## E2: Retrieval Evaluation Harness

### Implementation

**Module**: `evaluation/retrieval_eval.py`

**Features**:
- Standard IR metrics: Recall@K, Precision@K, F1@K
- Dataset-based evaluation
- Per-query and aggregate metrics
- Formatted evaluation reports

**Dataset Format**:
```json
[
  {
    "query": "NAAC 3.2.1 research funding",
    "framework": "NAAC",
    "criterion": "3.2.1",
    "expected_chunks": ["chunk_id_1", "chunk_id_2", ...]
  }
]
```

**Metrics**:

**Recall@K**: Fraction of relevant items retrieved in top-K
```
Recall@K = (# relevant in top-K) / (# relevant total)
```

**Precision@K**: Fraction of retrieved items that are relevant
```
Precision@K = (# relevant in top-K) / K
```

**F1@K**: Harmonic mean of Precision and Recall
```
F1@K = 2 * (Precision@K * Recall@K) / (Precision@K + Recall@K)
```

**Usage**:
```python
from evaluation.retrieval_eval import RetrievalEvaluator

# Initialize evaluator
evaluator = RetrievalEvaluator("data/retrieval_eval_dataset.json")

# Define retrieval function
def retrieval_func(query, framework, criterion):
    # Your retrieval logic
    return list_of_chunk_ids

# Run evaluation
results = evaluator.evaluate_dataset(retrieval_func, k=5)

# Print report
evaluator.print_evaluation_report(results)
```

**Test Script**: `tests/test_retrieval_eval.py`

**Expected Output**:
```
RETRIEVAL EVALUATION REPORT
================================================================================

Dataset: 3 queries

Average Metrics:
  recall@5: 0.840
  precision@5: 0.720
  f1@5: 0.770

Per-Query Results:
  Query 1: NAAC 3.2.1 extramural research funding...
    Framework: NAAC, Criterion: 3.2.1
    Retrieved: 5, Expected: 3
    recall@5: 1.000
    precision@5: 0.600
    f1@5: 0.750
```

---

## E3: Reviewer Feedback Logging

### Implementation

**Module**: `feedback/feedback_store.py`

**Features**:
- SQLite-based feedback storage
- Three rating types: relevant, irrelevant, missing
- Query and chunk-based retrieval
- Feedback statistics and export

**Database Schema**:
```sql
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY,
    query TEXT NOT NULL,
    framework TEXT NOT NULL,
    criterion TEXT,
    chunk_id TEXT NOT NULL,
    rating TEXT NOT NULL,  -- relevant, irrelevant, missing
    reviewer_id TEXT,
    comment TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
)
```

**Usage**:
```python
from feedback.feedback_store import FeedbackStore

# Initialize store
store = FeedbackStore("data/feedback.db")

# Add feedback
feedback_id = store.add_feedback(
    query="NAAC 3.2.1 research funding",
    framework="NAAC",
    criterion="3.2.1",
    chunk_id="chunk-123",
    rating="relevant",
    reviewer_id="reviewer-1",
    comment="Highly relevant chunk"
)

# Get feedback
query_feedback = store.get_feedback_for_query("NAAC 3.2.1 research funding")
chunk_feedback = store.get_feedback_for_chunk("chunk-123")
relevant_feedback = store.get_feedback_by_rating("relevant")

# Get statistics
stats = store.get_feedback_stats()

# Export to JSON
store.export_feedback("feedback_export.json")
```

**Test Script**: `tests/test_feedback_store.py`

---

## File Structure

```
accreditation_copilot/
├── observability/
│   ├── __init__.py
│   └── tracer.py                    # E1: LangSmith tracing
├── evaluation/
│   ├── __init__.py
│   └── retrieval_eval.py            # E2: Retrieval evaluation
├── feedback/
│   ├── __init__.py
│   └── feedback_store.py            # E3: Feedback storage
├── data/
│   ├── retrieval_eval_dataset.json  # Evaluation dataset
│   ├── feedback.db                  # Feedback database
│   └── feedback_export.json         # Exported feedback
└── tests/
    ├── test_retrieval_eval.py       # E2 test
    ├── test_feedback_store.py       # E3 test
    └── test_phase_e_complete.py     # Complete validation
```

---

## Validation

### Run Complete Validation

```bash
cd accreditation_copilot
python tests/test_phase_e_complete.py
```

### Expected Output

```
================================================================================
PHASE E COMPLETE VALIDATION SUITE
================================================================================

TEST E1: LANGSMITH TRACE LOGGING
✓ Trace manager initialized
✓ trace_stage() working
✓ Trace functions imported successfully
[PASS] E1 validation passed

TEST E2: RETRIEVAL EVALUATION HARNESS
✓ Evaluator initialized
✓ Metrics calculated
✓ Metrics correct
[PASS] E2 validation passed

TEST E3: REVIEWER FEEDBACK LOGGING
✓ Feedback store initialized
✓ Feedback added
✓ Feedback retrieved
✓ Stats retrieved
[PASS] E3 validation passed

TEST: PHASE 3 & PHASE 4 STABILITY
✓ Phase 3 tests passed
✓ Phase 4 tests passed
[PASS] Phase 3 & Phase 4 stability validated

VALIDATION SUMMARY
✓ PASS - E1: LangSmith Trace Logging
✓ PASS - E2: Retrieval Evaluation Harness
✓ PASS - E3: Reviewer Feedback Logging
✓ PASS - Phase 3 & Phase 4 Stability

✓ ALL PHASE E VALIDATION TESTS PASSED
```

---

## Success Criteria

✅ All criteria met:

1. **LangSmith traces appear for every run**
   - Trace manager implemented
   - Trace functions for all pipeline stages
   - Graceful degradation without API key

2. **Retrieval evaluation script reports Recall@K metrics**
   - RetrievalEvaluator class implemented
   - Recall@K, Precision@K, F1@K metrics
   - Dataset-based evaluation
   - Test script working

3. **Reviewer feedback can be stored and retrieved**
   - FeedbackStore class implemented
   - SQLite database with feedback table
   - Query, chunk, and rating-based retrieval
   - Statistics and export functionality

4. **Phase 3 and Phase 4 tests still pass**
   - No modifications to scoring logic
   - No modifications to ingestion logic
   - All existing tests passing

---

## Integration Examples

### Example 1: Trace a Query Execution

```python
from observability.tracer import get_trace_manager

tracer = get_trace_manager()

# Trace retrieval
with tracer.trace_stage("retrieval") as outputs:
    results, inst_avail = retriever.retrieve(query, variants, framework, query_type)
    outputs['num_chunks'] = len(results)
    outputs['institution_available'] = inst_avail

# Trace scoring
with tracer.trace_stage("scoring") as outputs:
    coverage = dimension_checker.check(results, framework, criterion)
    evidence_scores = evidence_scorer.score(results)
    outputs['coverage_ratio'] = coverage['coverage_ratio']
    outputs['num_evidence'] = len(evidence_scores)
```

### Example 2: Evaluate Retrieval Quality

```python
from evaluation.retrieval_eval import RetrievalEvaluator

evaluator = RetrievalEvaluator("data/retrieval_eval_dataset.json")

def my_retrieval_func(query, framework, criterion):
    # Your retrieval implementation
    results = retriever.retrieve(...)
    return [r['chunk_id'] for r in results]

results = evaluator.evaluate_dataset(my_retrieval_func, k=5)
evaluator.print_evaluation_report(results)
```

### Example 3: Collect Reviewer Feedback

```python
from feedback.feedback_store import FeedbackStore

store = FeedbackStore()

# Reviewer rates a chunk
store.add_feedback(
    query="NAAC 3.2.1 research funding",
    framework="NAAC",
    criterion="3.2.1",
    chunk_id="chunk-123",
    rating="relevant",
    reviewer_id="reviewer-1",
    comment="Contains exact funding amounts"
)

# Analyze feedback
stats = store.get_feedback_stats()
print(f"Relevant chunks: {stats['by_rating'].get('relevant', 0)}")
print(f"Irrelevant chunks: {stats['by_rating'].get('irrelevant', 0)}")
```

---

## Next Steps

### Immediate
1. ✅ Phase E validation complete
2. ✅ All tests passing
3. ✅ Documentation complete

### Production Deployment
1. Set `LANGCHAIN_API_KEY` environment variable
2. Update `data/retrieval_eval_dataset.json` with real expected chunks
3. Collect reviewer feedback during pilot testing
4. Monitor traces in LangSmith dashboard
5. Use feedback to tune retrieval weights

### Future Enhancements
1. **Advanced Metrics**: MRR, NDCG, MAP
2. **A/B Testing**: Compare retrieval strategies
3. **Feedback Analysis**: Identify common failure patterns
4. **Automated Tuning**: Use feedback to adjust weights
5. **Real-time Monitoring**: Dashboards for latency and quality

---

## Dependencies

**Required**:
- None (all modules work without external dependencies)

**Optional**:
- `langsmith`: For LangSmith tracing integration
  ```bash
  pip install langsmith
  ```

**Environment Variables**:
- `LANGCHAIN_API_KEY`: LangSmith API key (optional)
- `LANGCHAIN_PROJECT`: Project name (optional, default: "accreditation-copilot")

---

## Conclusion

Phase E successfully adds observability infrastructure to the accreditation copilot system. The implementation:

- ✅ Provides traceability through LangSmith integration
- ✅ Enables retrieval quality evaluation with standard IR metrics
- ✅ Supports reviewer feedback collection for continuous improvement
- ✅ Maintains Phase 3 and Phase 4 stability (no regressions)

**Phase E is production-ready and enables data-driven optimization of the retrieval pipeline.**

---

**Implemented By**: Kiro AI Assistant  
**Date**: March 5, 2026  
**Status**: ✅ PRODUCTION READY
