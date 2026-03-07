# Accreditation Copilot - Project Structure

## Overview
This is a Multimodal RAG system for NAAC and NBA accreditation compliance assistance.

## Directory Structure

```
accreditation_copilot/
│
├── .env                          # Environment variables (API keys)
├── .env.example                  # Example environment file
├── .gitignore                    # Git ignore rules
├── README.md                     # Project overview and setup
├── requirements.txt              # Python dependencies
├── main.py                       # Main application entry point
├── baseline_metrics.json         # Baseline performance metrics
├── PROJECT_STRUCTURE.md          # This file
│
├── data/                         # Data storage
│   ├── metadata.db              # SQLite database for chunk metadata
│   ├── raw_docs/                # Source PDF documents
│   │   ├── naac/               # NAAC accreditation documents
│   │   └── nba/                # NBA accreditation documents
│   ├── raw_images/             # Extracted images from PDFs
│   ├── processed_chunks/       # Processed text chunks
│   └── metric_maps/            # Metric mapping files
│
├── indexes/                      # Vector and sparse indices
│   ├── *.index                  # FAISS vector indices
│   ├── *_bm25.pkl              # BM25 sparse indices
│   └── *_mapping.pkl           # ID to chunk mappings
│
├── ingestion/                    # Phase 1: Document ingestion
│   ├── __init__.py
│   ├── pdf_processor.py        # PDF text extraction
│   ├── semantic_chunker.py     # Token-based chunking (300-400 tokens)
│   └── run_ingestion.py        # Ingestion orchestrator
│
├── retrieval/                    # Phase 2: Hybrid retrieval
│   ├── __init__.py
│   ├── framework_router.py     # NAAC/NBA framework detection
│   ├── query_expander.py       # Query expansion (6 variants)
│   ├── hybrid_retriever.py     # Dense + Sparse retrieval
│   ├── hyde_retriever.py       # Hypothetical Document Embeddings
│   ├── score_fusion.py         # Reciprocal Rank Fusion
│   ├── reranker.py             # Cross-encoder reranking
│   ├── parent_expander.py      # Parent-child context expansion
│   ├── retrieval_pipeline.py   # Main retrieval orchestrator
│   ├── index_builder.py        # FAISS index builder
│   ├── bm25_builder.py         # BM25 index builder
│   └── index_loader.py         # Index loading utilities
│
├── synthesis/                    # Phase 3: Answer generation (TODO)
│   └── __init__.py
│
├── evaluation/                   # Phase 4: Evaluation (TODO)
│   └── __init__.py
│
├── scoring/                      # Scoring utilities (TODO)
│   └── __init__.py
│
├── utils/                        # Utility modules
│   ├── __init__.py
│   ├── metadata_store.py       # SQLite database interface
│   └── groq_pool.py            # Groq API key rotation
│
├── scripts/                      # Utility scripts
│   └── rebuild_ingestion.py    # Rebuild database and indices
│
├── tests/                        # Test files
│   ├── test_phase2.py          # Phase 2 retrieval tests
│   ├── test_phase2_1.py        # Phase 2.1 precision tests
│   ├── test_phase2_2*.py       # Phase 2.2 parent expansion tests
│   ├── test_groq_keys.py       # Groq API key rotation tests
│   ├── check_chunks.py         # Chunk inspection utility
│   ├── check_token_counts.py  # Token count verification
│   └── test_parent_debug.py    # Parent expansion debugging
│
└── docs/                         # Documentation
    ├── README.md                # Detailed project documentation
    ├── COMPLETE_IMPLEMENTATION_GUIDE.md  # Full implementation guide
    ├── PHASE2_OUTPUT_EXAMPLES.md         # Phase 2 output examples
    ├── PHASE1_CORRECTION_SUMMARY.md      # Phase 1 summary
    ├── PHASE1_1_COMPLETE.md              # Phase 1.1 summary
    ├── PHASE2_SUMMARY.md                 # Phase 2 summary
    ├── PHASE2_1_SUMMARY.md               # Phase 2.1 summary
    ├── PHASE2_2_SUMMARY.md               # Phase 2.2 summary
    ├── PHASE2_2_CLEAN_VERIFICATION.md    # Phase 2.2 verification
    ├── PHASE2_2_EXPLANATION.md           # Phase 2.2 explanation
    ├── PHASE2_2_FINAL_RESULTS.md         # Phase 2.2 results
    ├── PHASE2_2_TEST_RESULTS.md          # Phase 2.2 test results
    ├── PROJECT_STRUCTURE.md              # This file (copy)
    └── *.txt, *.log                      # Output logs and results
```

## Module Descriptions

### Ingestion (`ingestion/`)
Handles PDF processing and chunking:
- **pdf_processor.py**: Extracts text from PDFs using PyMuPDF
- **semantic_chunker.py**: Creates 300-400 token chunks with BGE tokenizer
- **run_ingestion.py**: Orchestrates the complete ingestion pipeline

### Retrieval (`retrieval/`)
Implements hybrid retrieval with parent-child expansion:
- **framework_router.py**: Detects NAAC vs NBA queries
- **query_expander.py**: Generates 6 query variants
- **hybrid_retriever.py**: Combines FAISS (dense) + BM25 (sparse)
- **hyde_retriever.py**: Hypothetical Document Embeddings
- **score_fusion.py**: Reciprocal Rank Fusion (RRF)
- **reranker.py**: Cross-encoder reranking (BGE reranker)
- **parent_expander.py**: Adds sibling chunks for context
- **retrieval_pipeline.py**: Main orchestrator
- **index_builder.py**: Builds FAISS indices
- **bm25_builder.py**: Builds BM25 indices
- **index_loader.py**: Loads indices from disk

### Utils (`utils/`)
Utility modules:
- **metadata_store.py**: SQLite database interface for chunk metadata
- **groq_pool.py**: Round-robin API key rotation for Groq

### Scripts (`scripts/`)
Utility scripts:
- **rebuild_ingestion.py**: Rebuilds database and indices with new chunking

### Tests (`tests/`)
Test files for each phase:
- **test_phase2*.py**: Retrieval pipeline tests
- **check_*.py**: Inspection and debugging utilities

## Key Files

### Configuration
- `.env`: API keys and configuration (not in git)
- `.env.example`: Example configuration template
- `requirements.txt`: Python package dependencies

### Data
- `data/metadata.db`: SQLite database with chunk metadata
- `indexes/*.index`: FAISS vector indices
- `indexes/*_bm25.pkl`: BM25 sparse indices

### Documentation
- `docs/COMPLETE_IMPLEMENTATION_GUIDE.md`: Full technical guide
- `docs/PHASE2_OUTPUT_EXAMPLES.md`: Retrieval output examples
- `docs/PHASE*_SUMMARY.md`: Phase-specific summaries

## Development Phases

### ✅ Phase 0: Environment Setup
- Python 3.12.10 with CUDA support
- PyTorch 2.5.1+cu121
- GPU: RTX 4060 (8GB VRAM)

### ✅ Phase 1: Ingestion Pipeline
- PDF processing (14 PDFs, 574 pages)
- Initial chunking (122 chunks, 800-1500 tokens)
- FAISS + BM25 index building

### ✅ Phase 1.1: Chunk Granularity Optimization
- Token-based chunking (300-400 tokens)
- BGE tokenizer integration
- Rebuilt: 442 chunks, 88.7% in target range

### ✅ Phase 2: Hybrid Retrieval Layer
- Framework routing (NAAC/NBA)
- Query expansion (6 variants)
- Hybrid retrieval (FAISS + BM25)
- Score fusion (RRF)
- Cross-encoder reranking

### ✅ Phase 2.1: Retrieval Precision Upgrade
- Metric ID detection
- Metadata filtering
- Criterion score boosting
- Exact match guarantee

### ✅ Phase 2.2: Parent-Child Hierarchical Expansion
- Parent section ID computation
- Sibling chunk fetching
- Incremental sibling addition (1-3 siblings)
- Token limit enforcement (1200 max)
- 100% sibling addition success rate

### 🔄 Phase 3: Synthesis & Generation (TODO)
- Answer generation with LLM
- Citation tracking
- Confidence scoring

### 🔄 Phase 4: Evaluation (TODO)
- Retrieval metrics
- Answer quality evaluation
- End-to-end testing

## Getting Started

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run ingestion** (if needed):
   ```bash
   cd accreditation_copilot
   python scripts/rebuild_ingestion.py
   ```

4. **Run tests**:
   ```bash
   python tests/test_phase2_2_verification.py
   ```

5. **Start application**:
   ```bash
   python main.py
   ```

## Performance Metrics

- **Ingestion**: ~2 minutes for 14 PDFs
- **Retrieval**: ~900ms per query
- **GPU Memory**: 1.2GB / 8GB (15% utilization)
- **Chunk Size**: 300-400 tokens (88.7% in range)
- **Sibling Addition**: 100% success rate
- **Context Expansion**: 2.8x average

## Technology Stack

- **Python**: 3.12.10
- **PyTorch**: 2.5.1+cu121
- **Embeddings**: BAAI/bge-base-en-v1.5
- **Reranker**: BAAI/bge-reranker-base
- **Vector Store**: FAISS
- **Sparse Retrieval**: BM25 (rank-bm25)
- **Database**: SQLite
- **LLM API**: Groq
- **PDF Processing**: PyMuPDF (fitz)

## License

[Add your license here]

## Contributors

[Add contributors here]
