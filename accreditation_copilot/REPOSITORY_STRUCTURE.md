# 📁 Repository Structure Guide

## Overview

The repository has been organized into a clean, logical structure. Everything is now in its proper place!

---

## 🗂️ Directory Structure

```
accreditation_copilot/
│
├── 📱 Frontend Application
│   └── frontend/                    # Next.js application
│       ├── app/                     # App router pages
│       ├── components/              # React components
│       │   ├── Sidebar.tsx
│       │   ├── QueryPanel.tsx
│       │   ├── AuditDashboard.tsx
│       │   ├── EvidenceViewer.tsx
│       │   ├── GapAnalysisPanel.tsx
│       │   ├── MetricsPanel.tsx
│       │   └── ThemeSwitcher.tsx   # NEW: Theme system
│       ├── public/                  # Static assets
│       └── package.json
│
├── 🔧 Backend API
│   └── api/                         # FastAPI application
│       ├── main.py                  # API entry point
│       ├── routers/                 # Route handlers
│       │   ├── audit.py            # Audit endpoints
│       │   ├── upload.py           # Upload endpoints
│       │   └── metrics.py          # Metrics endpoints
│       ├── error_handler.py        # Error handling
│       └── requirements.txt        # API dependencies
│
├── 🧠 Core Business Logic
│   ├── audit/                       # Audit pipeline
│   │   ├── criterion_auditor.py    # Main auditor
│   │   ├── audit_enricher.py       # Evidence enrichment
│   │   └── full_audit_runner.py    # Batch auditing
│   │
│   ├── retrieval/                   # Retrieval system
│   │   ├── dual_retrieval.py       # Dual retrieval
│   │   ├── hybrid_retriever.py     # Hybrid search
│   │   ├── query_expander.py       # Query expansion
│   │   └── multi_query_retriever.py
│   │
│   ├── scoring/                     # Scoring pipeline
│   │   ├── scoring_pipeline.py     # Main pipeline
│   │   ├── evidence_scorer.py      # Evidence scoring
│   │   ├── confidence_calculator.py
│   │   ├── dimension_checker.py
│   │   └── evidence_strength.py
│   │
│   ├── analysis/                    # Analysis modules
│   │   ├── evidence_grounder.py    # Evidence grounding
│   │   └── gap_detector.py         # Gap detection
│   │
│   ├── synthesis/                   # Report synthesis
│   │   └── compliance_report_builder.py
│   │
│   └── validation/                  # Validation
│       └── report_validator.py
│
├── 💾 Data & Storage
│   ├── data/                        # Data files
│   │   ├── raw_docs/               # Original PDFs
│   │   ├── processed_chunks/       # Processed chunks
│   │   ├── raw_images/             # Extracted images
│   │   ├── metric_maps/            # YAML mappings
│   │   ├── metadata.db             # SQLite database
│   │   └── baseline_metrics.json   # Baseline data
│   │
│   ├── indexes/                     # Search indexes
│   │   ├── framework/              # Framework indexes
│   │   └── institution/            # Institution indexes
│   │
│   ├── cache/                       # Caching system
│   │   ├── audit_cache.py
│   │   └── __init__.py
│   │
│   └── audit_results/               # Audit outputs
│       └── cache_*.json            # Cached results
│
├── 🛠️ Utilities & Support
│   ├── ingestion/                   # Document ingestion
│   │   ├── framework/              # Framework ingestion
│   │   └── institution/            # Institution ingestion
│   │
│   ├── models/                      # Model management
│   │   └── model_manager.py        # Singleton manager
│   │
│   ├── criteria/                    # Criterion registry
│   │   └── criterion_registry.py
│   │
│   ├── utils/                       # Helper utilities
│   │   └── evidence_normalizer.py
│   │
│   ├── security/                    # Security utilities
│   ├── observability/              # Logging & tracing
│   ├── feedback/                   # Feedback system
│   ├── evaluation/                 # Evaluation tools
│   ├── mapping/                    # Metric mapping
│   ├── reporting/                  # Report generation
│   └── schemas/                    # Data schemas
│
├── 📜 Scripts (NEW - Organized!)
│   └── scripts/
│       ├── RESTART_BACKEND.bat     # Start backend
│       ├── START_FRONTEND.bat      # Start frontend
│       ├── start_servers.bat       # Start both
│       ├── start_servers.ps1       # PowerShell version
│       │
│       ├── demos/                   # Demo scripts
│       │   ├── demo_cache_system.py
│       │   ├── demo_phase6_complete.py
│       │   ├── demo_phase_e_tracing.py
│       │   ├── demo_preui_improvements.py
│       │   └── phase6_demo_output.json
│       │
│       └── utils/                   # Utility scripts
│           ├── check_criteria.py
│           ├── check_db.py
│           ├── clear_institution_data.py
│           ├── run_api.py
│           └── run_full_audit.py
│
├── 🧪 Tests (Organized!)
│   └── tests/
│       ├── test_audit_flow.py
│       ├── test_audit_response.py
│       ├── test_dimension_check.py
│       ├── test_groq_connection.py
│       ├── test_institution_retrieval.py
│       ├── test_integration.py
│       ├── test_retrieval_fields.py
│       └── test_stability_fixes.py
│
├── 📚 Documentation (All in one place!)
│   └── docs/
│       ├── User Guides/
│       │   ├── QUICK_FIX_GUIDE.md
│       │   ├── DATA_INGESTION_GUIDE.md
│       │   ├── MANUAL_INGESTION_GUIDE.md
│       │   ├── THEME_SYSTEM_GUIDE.md
│       │   └── THEME_PREVIEW.md
│       │
│       ├── Technical Docs/
│       │   ├── PROJECT_STRUCTURE.md
│       │   ├── RETRIEVAL_SYSTEM_COMPLETE.md
│       │   ├── CACHE_SYSTEM_COMPLETE.md
│       │   ├── PHASE6_SUMMARY.md
│       │   └── SYSTEM_STATUS.md
│       │
│       ├── Implementation Guides/
│       │   ├── UI_IMPLEMENTATION_GUIDE.md
│       │   ├── STABILITY_FIXES_COMPLETE.md
│       │   ├── RECOMMENDATIONS_FIX.md
│       │   └── EVIDENCE_DISPLAY_FIX.md
│       │
│       ├── Quick References/
│       │   ├── MULTI_QUERY_QUICK_REFERENCE.md
│       │   ├── RRF_QUICK_REFERENCE.md
│       │   ├── RETRIEVAL_QUICK_REFERENCE.md
│       │   └── STABILITY_QUICK_REF.md
│       │
│       └── Status Reports/
│           ├── FINAL_STATUS_REPORT.md
│           ├── PHASE_E_FINAL_STATUS.md
│           ├── UI_COMPLETE.md
│           └── INGESTION_SUCCESS.md
│
├── 📋 Root Files
│   ├── README.md                    # Main documentation (NEW!)
│   ├── REPOSITORY_STRUCTURE.md      # This file
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template
│   ├── .gitignore                   # Git ignore rules
│   └── main.py                      # Legacy entry point
│
└── 🔐 Configuration
    ├── .env                         # Environment variables (not in git)
    └── .env.example                 # Template for .env
```

---

## 📍 Quick Navigation

### Want to...

**Start the application?**
→ `scripts/RESTART_BACKEND.bat` and `scripts/START_FRONTEND.bat`

**Read documentation?**
→ `docs/` folder or `README.md`

**Run tests?**
→ `tests/` folder

**Check utility scripts?**
→ `scripts/utils/` folder

**See demo examples?**
→ `scripts/demos/` folder

**Modify the UI?**
→ `frontend/components/` folder

**Modify the API?**
→ `api/routers/` folder

**Modify core logic?**
→ `audit/`, `retrieval/`, `scoring/` folders

**Add new documents?**
→ `data/raw_docs/` folder

**Check audit results?**
→ `audit_results/` folder

---

## 🎯 Key Changes

### Before (Messy)
```
accreditation_copilot/
├── 50+ markdown files scattered everywhere
├── test_*.py files in root
├── demo_*.py files in root
├── *.bat files in root
├── *.json output files in root
└── No clear organization
```

### After (Clean)
```
accreditation_copilot/
├── 📚 docs/          # All documentation
├── 🧪 tests/         # All test files
├── 📜 scripts/       # All scripts
│   ├── demos/        # Demo scripts
│   └── utils/        # Utility scripts
├── 📋 README.md      # Comprehensive guide
└── Clean root directory
```

---

## 🚀 Startup Scripts Location

All startup scripts are now in `scripts/`:

```bash
# Backend
.\scripts\RESTART_BACKEND.bat

# Frontend
.\scripts\START_FRONTEND.bat

# Both servers
.\scripts\start_servers.bat
.\scripts\start_servers.ps1  # PowerShell version
```

---

## 📚 Documentation Organization

All docs are in `docs/` organized by category:

### User Guides
- How to use the system
- Quick start guides
- Theme system guides

### Technical Docs
- Architecture details
- System design
- Component documentation

### Implementation Guides
- How features were built
- Fix documentation
- Integration guides

### Quick References
- Cheat sheets
- Command references
- API quick refs

### Status Reports
- Project milestones
- Completion reports
- Phase summaries

---

## 🧪 Testing Organization

All tests are in `tests/`:

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_audit_flow.py

# Run with coverage
pytest --cov=. tests/
```

---

## 📜 Scripts Organization

### Startup Scripts (`scripts/`)
- `RESTART_BACKEND.bat` - Start backend with updates
- `START_FRONTEND.bat` - Start frontend
- `start_servers.bat` - Start both
- `start_servers.ps1` - PowerShell version

### Demo Scripts (`scripts/demos/`)
- `demo_cache_system.py` - Cache system demo
- `demo_phase6_complete.py` - Phase 6 demo
- `demo_phase_e_tracing.py` - Tracing demo
- `demo_preui_improvements.py` - Pre-UI demo

### Utility Scripts (`scripts/utils/`)
- `check_criteria.py` - Check criterion registry
- `check_db.py` - Check database
- `clear_institution_data.py` - Clear institution data
- `run_api.py` - Run API server
- `run_full_audit.py` - Run full audit

---

## 💡 Tips

### Finding Files

**Old location** → **New location**

- `test_*.py` → `tests/test_*.py`
- `demo_*.py` → `scripts/demos/demo_*.py`
- `*.bat` → `scripts/*.bat`
- `*_GUIDE.md` → `docs/*_GUIDE.md`
- `*_SUMMARY.md` → `docs/*_SUMMARY.md`
- `check_*.py` → `scripts/utils/check_*.py`

### Updating Imports

If you have scripts that import from moved files:

```python
# Old
from test_audit_flow import test_function

# New
from tests.test_audit_flow import test_function
```

### Running Scripts

Always run from the `accreditation_copilot` directory:

```bash
# Correct
cd accreditation_copilot
.\scripts\RESTART_BACKEND.bat

# Wrong
cd scripts
.\RESTART_BACKEND.bat  # Won't work!
```

---

## ✅ Benefits

### Before
- ❌ 50+ files in root directory
- ❌ Hard to find anything
- ❌ No clear organization
- ❌ Multiple README files
- ❌ Confusing structure

### After
- ✅ Clean root directory
- ✅ Logical organization
- ✅ Easy to navigate
- ✅ One comprehensive README
- ✅ Clear structure

---

## 🎉 Summary

The repository is now:

✅ **Organized** - Everything in its proper place  
✅ **Clean** - No clutter in root directory  
✅ **Documented** - One comprehensive README  
✅ **Navigable** - Easy to find what you need  
✅ **Professional** - Industry-standard structure  

Enjoy the clean, organized repository! 🚀
