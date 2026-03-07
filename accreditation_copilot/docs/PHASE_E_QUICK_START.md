# Phase E Quick Start Guide

Quick reference for using Phase E observability features.

---

## Run Validation

```bash
cd accreditation_copilot
python tests/test_phase_e_complete.py
```

Expected: All tests pass ✅

---

## E1: Enable Tracing

### Setup
```bash
# Install LangSmith (optional)
pip install langsmith

# Set API key
export LANGCHAIN_API_KEY="your-api-key"
```

### Usage
```python
from observability.tracer import get_trace_manager

tracer = get_trace_manager()

# Trace a stage
with tracer.trace_stage("retrieval") as outputs:
    results = retriever.retrieve(...)
    outputs['num_chunks'] = len(results)
```

---

## E2: Evaluate Retrieval

### Run Evaluation
```bash
python tests/test_retrieval_eval.py
```

### Update Dataset
Edit `data/retrieval_eval_dataset.json`:
```json
[
  {
    "query": "NAAC 3.2.1 research funding",
    "framework": "NAAC",
    "criterion": "3.2.1",
    "expected_chunks": ["chunk_id_1", "chunk_id_2"]
  }
]
```

### Custom Evaluation
```python
from evaluation.retrieval_eval import RetrievalEvaluator

evaluator = RetrievalEvaluator("data/retrieval_eval_dataset.json")

def my_retrieval(query, framework, criterion):
    # Your retrieval logic
    return list_of_chunk_ids

results = evaluator.evaluate_dataset(my_retrieval, k=5)
evaluator.print_evaluation_report(results)
```

---

## E3: Collect Feedback

### Add Feedback
```python
from feedback.feedback_store import FeedbackStore

store = FeedbackStore()

store.add_feedback(
    query="NAAC 3.2.1 research funding",
    framework="NAAC",
    criterion="3.2.1",
    chunk_id="chunk-123",
    rating="relevant",  # or "irrelevant", "missing"
    reviewer_id="reviewer-1",
    comment="Highly relevant"
)
```

### Query Feedback
```python
# By query
feedback = store.get_feedback_for_query("NAAC 3.2.1 research funding")

# By chunk
feedback = store.get_feedback_for_chunk("chunk-123")

# By rating
relevant = store.get_feedback_by_rating("relevant")

# Statistics
stats = store.get_feedback_stats()
print(stats)
```

### Export Feedback
```python
store.export_feedback("feedback_export.json")
```

---

## Test Individual Components

```bash
# Test retrieval evaluation
python tests/test_retrieval_eval.py

# Test feedback store
python tests/test_feedback_store.py

# Test complete Phase E
python tests/test_phase_e_complete.py
```

---

## Troubleshooting

### LangSmith Not Working
- Check `LANGCHAIN_API_KEY` is set
- Install: `pip install langsmith`
- System works without tracing (graceful degradation)

### Evaluation Metrics are 0
- Update `expected_chunks` in dataset with real chunk IDs
- Sample dataset has placeholder IDs

### Feedback Database Locked
- Close all connections: `store.close()`
- Delete test database: `rm data/test_feedback.db`

---

## Documentation

- **Complete Guide**: `docs/PHASE_E_OBSERVABILITY.md`
- **Summary**: `docs/PHASE_E_SUMMARY.md`
- **This Guide**: `PHASE_E_QUICK_START.md`

---

**Status**: ✅ All Phase E components working
