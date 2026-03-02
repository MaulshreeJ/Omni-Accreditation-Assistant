# Project Structure

## Overview

```
MultiModal Project/
│
├── accreditation_copilot/          # Main Application
│   ├── data/                       # Data storage
│   │   ├── raw_docs/              # Input PDF documents
│   │   ├── raw_images/            # Input infrastructure images
│   │   ├── processed_chunks/      # Processed chunks
│   │   └── metric_maps/           # NAAC metric maps
│   │
│   ├── ingestion/                 # Phase A - Document ingestion
│   ├── retrieval/                 # Phase B - Hybrid retrieval
│   ├── scoring/                   # Phase C - Deterministic scoring
│   ├── synthesis/                 # Phase D - LLM synthesis
│   ├── evaluation/                # Phase E - Evaluation metrics
│   │
│   ├── utils/                     # Utility functions
│   │   ├── __init__.py
│   │   └── groq_pool.py          # Multi-key Groq wrapper
│   │
│   ├── main.py                    # Application entry point
│   ├── requirements.txt           # Python dependencies
│   ├── baseline_metrics.json     # Performance metrics
│   ├── .env                       # API keys (not in git)
│   ├── .env.example              # Environment template
│   ├── .gitignore                # Git ignore rules
│   └── README.md                 # Application documentation
│
├── docs/                          # Documentation
│   ├── INDEX.md                  # Documentation index
│   ├── START_HERE.md             # Quick start guide
│   ├── SETUP_GUIDE.md            # Detailed setup
│   ├── QUICK_REFERENCE.md        # Quick reference
│   ├── PHASE0_REPORT.md          # Phase 0 validation
│   ├── COMPLETE_SETUP_CONFIRMATION.md
│   ├── ENVIRONMENT_REPORT.md     # Technical details
│   ├── INSTALLATION_SUMMARY.txt  # Installation log
│   ├── FINAL_STATUS.md           # Current status
│   └── README.md                 # Original docs
│
├── testing/                       # Validation Scripts
│   ├── README.md                 # Testing documentation
│   ├── validate_phase0.py        # Main validation script
│   ├── verify_cuda.py            # CUDA verification
│   ├── verify_faiss.py           # FAISS verification
│   ├── verify_groq.py            # Groq API verification
│   ├── verify_ollama.py          # Ollama verification
│   ├── test_llava.py             # LLaVA inference test
│   ├── verify_all.py             # Quick all-in-one check
│   └── run_all_verifications.py  # Complete test suite
│
├── venv/                          # Python virtual environment
│
├── .env                           # Root environment variables
├── .env.example                   # Root environment template
├── README.md                      # Project README
└── PROJECT_STRUCTURE.md           # This file
```

## Folder Purposes

### accreditation_copilot/
Main application code following the specified architecture:
- **data/** - All data storage (documents, images, chunks, metrics)
- **ingestion/** - Phase A implementation (to be developed)
- **retrieval/** - Phase B implementation (to be developed)
- **scoring/** - Phase C implementation (to be developed)
- **synthesis/** - Phase D implementation (to be developed)
- **evaluation/** - Phase E implementation (to be developed)
- **utils/** - Shared utilities (Groq pool, helpers)

### docs/
All documentation files:
- Setup guides
- Validation reports
- Technical documentation
- Quick references

### testing/
All validation and test scripts:
- Phase 0 validation
- Component-specific tests
- Integration tests
- Performance benchmarks

### venv/
Python virtual environment with all dependencies installed.

## Key Files

| File | Location | Purpose |
|------|----------|---------|
| `main.py` | `accreditation_copilot/` | Application entry point |
| `requirements.txt` | `accreditation_copilot/` | Python dependencies |
| `groq_pool.py` | `accreditation_copilot/utils/` | Multi-key Groq wrapper |
| `validate_phase0.py` | `testing/` | Phase 0 validation |
| `PHASE0_REPORT.md` | `docs/` | Validation results |
| `README.md` | Root | Project overview |
| `.env` | Root & app | API keys & config |

## Navigation

### For Development
```bash
cd accreditation_copilot
python main.py
```

### For Validation
```bash
python testing/validate_phase0.py
```

### For Documentation
```bash
# Read docs/INDEX.md for navigation
# Start with docs/START_HERE.md
```

## Clean Structure Benefits

1. **Organized** - Clear separation of concerns
2. **Maintainable** - Easy to find files
3. **Scalable** - Room for growth
4. **Professional** - Industry-standard layout
5. **Git-friendly** - Proper .gitignore setup

## Phase Status

- ✅ **Phase 0** - Environment setup complete
- 🔄 **Phase 1** - Ingestion (ready to implement)
- ⏳ **Phase 2** - Retrieval (pending)
- ⏳ **Phase 3** - Scoring (pending)
- ⏳ **Phase 4** - Synthesis (pending)
- ⏳ **Phase 5** - Evaluation (pending)
