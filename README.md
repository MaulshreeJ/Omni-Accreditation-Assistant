# Multimodal RAG Project

This repository contains the **Omni-Accreditation Compliance Copilot** system and related validation tools.

## Project Structure

```
.
├── accreditation_copilot/    # Main application
│   ├── data/                 # Data storage
│   ├── ingestion/            # Document processing
│   ├── retrieval/            # Hybrid search
│   ├── scoring/              # Compliance scoring
│   ├── synthesis/            # LLM synthesis
│   ├── evaluation/           # Metrics & evaluation
│   └── utils/                # Utilities
│
├── docs/                     # Documentation
│   ├── PHASE0_REPORT.md     # Environment setup report
│   ├── SETUP_GUIDE.md       # Setup instructions
│   └── ...                  # Other documentation
│
├── testing/                  # Validation scripts
│   ├── validate_phase0.py   # Phase 0 validation
│   ├── verify_cuda.py       # CUDA verification
│   └── ...                  # Other test scripts
│
├── venv/                     # Python virtual environment
├── .env                      # Environment variables (not in git)
└── .env.example             # Environment template
```

## Quick Start

### 1. Activate Virtual Environment

```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Validate Environment

```bash
cd accreditation_copilot
python ..\testing\validate_phase0.py
```

### 3. Run Application

```bash
cd accreditation_copilot
python main.py
```

## Documentation

All documentation is in the `docs/` folder:
- **PHASE0_REPORT.md** - Environment validation results
- **SETUP_GUIDE.md** - Detailed setup instructions
- **ENVIRONMENT_REPORT.md** - Technical environment details

## Testing

Validation and test scripts are in the `testing/` folder.

## Configuration

1. Copy `.env.example` to `.env`
2. Add your API keys:
   - Groq API keys
   - LangSmith API key (optional)
3. Configure Ollama host if needed

## System Requirements

- Python 3.12+
- NVIDIA GPU with CUDA support (RTX 4060 or better)
- 8GB+ VRAM
- Ollama with LLaVA model

## Current Status

✅ **Phase 0 Complete** - Environment validated and ready  
🔄 **Phase 1 Next** - Ingestion pipeline implementation

See `docs/PHASE0_REPORT.md` for detailed validation results.
