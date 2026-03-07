# Retrieval Metrics Evaluation Guide

## Overview

The `evaluation/compute_metrics.py` script computes standard Information Retrieval (IR) metrics for the accreditation copilot's retrieval pipeline:

- **Precision@k**: Proportion of retrieved results that are relevant
- **Recall@k**: Proportion of relevant documents that are retrieved
- **F1 Score@k**: Harmonic mean of precision and recall
- **MRR (Mean Reciprocal Rank)**: Average of reciprocal ranks of first relevant result

## Usage

### Basic Usage

```bash
cd accreditation_copilot
python evaluation/compute_metrics.py
```

### What It Does

1. Initializes the existing retrieval pipeline (no modifications)
2. Runs 8 evaluation queries across different topics
3. Retrieves top-5 results for each query
4. Computes metrics based on keyword-based relevance matching
5. Prints formatted results suitable for screenshots

## Evaluation Queries

The script includes 8 diverse queries covering:

1. Extramural funding for research
2. Research publications and journals
3. Faculty qualifications and credentials
4. Student support services and facilities
5. Infrastructure and learning resources
6. Curriculum design and development
7. Student performance and outcomes
8. Quality assurance mechanisms

Each query has associated relevant keywords used for matching.

## Metrics Explanation

### Precision@k

```
Precision@k = (# of relevant items in top-k) / k
```

**Interpretation**:
- High precision (≥0.7): Most retrieved results are relevant
- Medium precision (0.5-0.7): About half of results are relevant
- Low precision (<0.5): Many irrelevant results

**Example**: If 4 out of 5 retrieved documents are relevant, Precision@5 = 0.8

### Recall@k

```
Recall@k = (# of relevant items in top-k) / (total # of relevant items)
```

**Interpretation**:
- High recall (≥0.7): Most relevant documents are retrieved
- Medium recall (0.5-0.7): About half of relevant documents retrieved
- Low recall (<0.5): Many relevant documents missed

**Example**: If 4 out of 6 relevant documents are retrieved, Recall@5 = 0.67

### F1 Score@k

```
F1@k = 2 * (Precision@k * Recall@k) / (Precision@k + Recall@k)
```

**Interpretation**:
- High F1 (≥0.7): Good balance between precision and recall
- Medium F1 (0.5-0.7): Moderate balance
- Low F1 (<0.5): Poor balance

**Example**: With Precision=0.8 and Recall=0.67, F1 = 0.73

### MRR (Mean Reciprocal Rank)

```
MRR = Average of (1 / rank of first relevant result)
```

**Interpretation**:
- High MRR (≥0.7): Relevant results appear early (ranks 1-2)
- Medium MRR (0.5-0.7): Relevant results in middle (ranks 2-3)
- Low MRR (<0.5): Relevant results appear late (ranks 4-5+)

**Example**: If first relevant result is at rank 2, RR = 1/2 = 0.5

## Output Format

The script produces three output sections:

### 1. Per-Query Results

Shows metrics for each individual query:

```
[1/8] Query: extramural funding for research
     Framework: NAAC, Type: metric
     Retrieved: 5 chunks
     Relevant found: 4/6
     Precision@5: 0.800
     Recall@5: 0.667
     F1@5: 0.727
     MRR: 1.000
```

### 2. Average Metrics

Shows overall performance across all queries:

```
AVERAGE METRICS
----------------
Precision@5 : 0.750
Recall@5    : 0.625
F1 Score@5  : 0.681
MRR         : 0.812
```

### 3. Screenshot-Friendly Summary

Formatted box for easy screenshot submission:

```
╔════════════════════════════════════════╗
║       RETRIEVAL METRICS RESULTS        ║
╠════════════════════════════════════════╣
║  Precision@5 : 0.750                   ║
║  Recall@5    : 0.625                   ║
║  F1 Score@5  : 0.681                   ║
║  MRR         : 0.812                   ║
╠════════════════════════════════════════╣
║  Queries     : 8                       ║
║  Top-K       : 5                       ║
╚════════════════════════════════════════╝
```

## Implementation Details

### Pipeline Components Used

The script uses the existing retrieval pipeline without modifications:

1. **DualRetriever**: Retrieves from both framework and institution indexes
2. **QueryExpander**: Expands queries with variants
3. **HybridRetriever**: Combines FAISS (dense) and BM25 (sparse) retrieval
4. **Reranker**: Re-ranks results using cross-encoder

### Relevance Matching

The script uses keyword-based relevance matching:

- Each query has a list of relevant keywords
- A retrieved chunk is considered relevant if it contains any keyword
- This is a simple but effective proxy for true relevance

### Customization

To customize the evaluation:

1. **Change top_k**: Modify the `top_k` parameter in `compute_metrics()`
2. **Add queries**: Add entries to the `EVAL_QUERIES` list
3. **Change frameworks**: Modify `framework` field in queries (NAAC/NBA)
4. **Adjust keywords**: Update `relevant_keywords` for each query

## Example Customization

```python
EVAL_QUERIES = [
    {
        "query": "your custom query here",
        "framework": "NAAC",  # or "NBA"
        "query_type": "metric",  # or "policy"
        "relevant_keywords": ["keyword1", "keyword2", "keyword3"]
    },
    # Add more queries...
]
```

## Limitations

1. **Keyword-based matching**: Uses simple keyword matching instead of labeled ground truth
2. **No chunk ID validation**: Doesn't validate against specific chunk IDs
3. **Framework-specific**: Currently focused on NAAC framework queries

## Future Enhancements

For production use, consider:

1. Creating a labeled dataset with explicit chunk IDs
2. Using human relevance judgments
3. Adding more diverse queries
4. Testing across both NAAC and NBA frameworks
5. Evaluating with different top_k values (1, 3, 5, 10)

## Troubleshooting

### Models Not Loading

If models fail to load:
- Ensure HuggingFace token is set: `HF_TOKEN` in `.env`
- Check GPU availability (CUDA)
- Verify model cache directory has space

### No Results Retrieved

If no results are retrieved:
- Verify indexes exist in `indexes/framework/` directory
- Check that framework name matches (NAAC/NBA)
- Ensure query_type is valid (metric/policy)

### Low Metrics

If metrics are unexpectedly low:
- Review relevant keywords for each query
- Check if retrieved chunks contain expected content
- Verify retrieval pipeline is working correctly

## References

- **Precision and Recall**: Standard IR metrics for retrieval quality
- **F1 Score**: Harmonic mean balancing precision and recall
- **MRR**: Measures ranking quality of relevant results

## Command Summary

```bash
# Run evaluation
python evaluation/compute_metrics.py

# Expected runtime: 30-60 seconds (depending on model loading)
# Expected output: Metrics for 8 queries with formatted summary
```

## Screenshot Submission

For project submission, take a screenshot of the final metrics summary box:

```
╔════════════════════════════════════════╗
║       RETRIEVAL METRICS RESULTS        ║
╠════════════════════════════════════════╣
║  Precision@5 : X.XXX                   ║
║  Recall@5    : X.XXX                   ║
║  F1 Score@5  : X.XXX                   ║
║  MRR         : X.XXX                   ║
╠════════════════════════════════════════╣
║  Queries     : 8                       ║
║  Top-K       : 5                       ║
╚════════════════════════════════════════╝
```

This provides a clear, professional summary of retrieval performance.
