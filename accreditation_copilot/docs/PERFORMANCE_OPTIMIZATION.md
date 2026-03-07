# Performance Optimization - Model Loading Architecture

## Overview
Implemented centralized ModelManager to eliminate redundant model loading and achieve significant performance improvements.

## Problem Statement
**Before optimization:**
- Models (embedder, reranker, Groq client) were loaded separately by each component
- Each audit operation triggered multiple model loads
- Full audit time: 60-90 seconds
- Test suite time: Multiple minutes due to repeated model initialization

## Solution: ModelManager Singleton Pattern

### Architecture
Created `models/model_manager.py` with singleton ModelManager class that:
1. Loads all models once at system startup
2. Provides shared access to models across all components
3. Manages model lifecycle centrally

### Models Managed
- **Embedder**: BAAI/bge-base-en-v1.5 (SentenceTransformer)
- **Reranker**: BAAI/bge-reranker-base (AutoModelForSequenceClassification)
- **Tokenizer**: tiktoken cl100k_base
- **Groq Client**: LLM API client

### Components Updated
1. `retrieval/reranker.py` - Uses ModelManager for reranker model/tokenizer
2. `retrieval/hybrid_retriever.py` - Uses ModelManager for embedder
3. `retrieval/dual_retrieval.py` - Passes ModelManager to components
4. `audit/criterion_auditor.py` - Accepts model_manager parameter
5. `audit/full_audit_runner.py` - Initializes ModelManager at startup

## Performance Results

### Test Results (test_model_loading.py)
```
First audit:  9.85 seconds (includes model loading)
Second audit: 1.82 seconds (models reused)
Performance improvement: 81.6%
```

### Key Metrics
- **Model loading**: Once per system startup (vs. multiple times per operation)
- **Memory efficiency**: Single model instances shared across all operations
- **Audit speed**: ~2 seconds per criterion (vs. ~10 seconds before)
- **Expected full audit time**: 10-15 seconds (vs. 60-90 seconds before)

## HuggingFace Authentication
ModelManager supports optional HuggingFace authentication via `HF_TOKEN` environment variable:
- If `HF_TOKEN` is set, authenticates with HuggingFace Hub
- If not set, uses unauthenticated requests (may have rate limits)
- Token should be added to `.env` file

## Validation
All Phase 6 tests pass with the new architecture:
- ✓ Bug fixes (reranker scoring, evidence counting, dimension coverage)
- ✓ New capabilities (evidence grounding, gap detection, evidence strength)
- ✓ Backward compatibility (Phase 3/4/5 stability)
- ✓ Model loading optimization (singleton pattern, shared instances)

## Usage Example

```python
from models.model_manager import get_model_manager
from audit.criterion_auditor import CriterionAuditor

# Initialize ModelManager once at startup
model_manager = get_model_manager()

# Create auditor with shared models
auditor = CriterionAuditor(model_manager=model_manager)

# Run multiple audits - models are reused
result1 = auditor.audit_criterion(...)
result2 = auditor.audit_criterion(...)
```

## Implementation Details

### Singleton Pattern
```python
class ModelManager:
    _instance = None
    _initialized = False
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ModelManager()
            cls._instance.load_models()
        return cls._instance
```

### Model Access Methods
- `get_embedder()` - Returns SentenceTransformer instance
- `get_reranker_model()` - Returns reranker model
- `get_reranker_tokenizer()` - Returns reranker tokenizer
- `get_tiktoken_tokenizer()` - Returns tiktoken tokenizer
- `get_groq_client()` - Returns Groq API client
- `get_device()` - Returns compute device (cuda/cpu)

## Testing
Created comprehensive test suite in `tests/test_model_loading.py`:
1. **Singleton Pattern Test** - Validates single instance across calls
2. **Shared Models Test** - Confirms components share model instances
3. **Performance Test** - Measures speed improvement from model reuse

All tests pass: 3/3 ✓

## Benefits
1. **Performance**: 81.6% faster on subsequent operations
2. **Memory**: Single model instances vs. multiple copies
3. **Maintainability**: Centralized model management
4. **Scalability**: Easy to add new models to the manager
5. **Testing**: Faster test execution due to model reuse

## Future Enhancements
- Add model caching to disk for even faster startup
- Support model hot-swapping for A/B testing
- Add model version management
- Implement model health checks
