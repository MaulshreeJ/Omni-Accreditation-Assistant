# Quick Start Guide

Get the Accreditation Copilot up and running in 5 minutes!

---

## Prerequisites

- Python 3.12+
- CUDA-capable GPU (optional but recommended)
- 8GB+ RAM
- Groq API keys ([Get them here](https://console.groq.com))

---

## Installation (5 steps)

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd accreditation_copilot
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example environment file (from accreditation_copilot directory)
cp .env.example .env

# Edit .env and add your Groq API keys
# GROQ_API_KEY_1=your_first_key_here
# GROQ_API_KEY_2=your_second_key_here
```

**Important**: The `.env` file is in `accreditation_copilot/.env`, not in the root directory.

### 5. Add PDF Documents
```
Place your PDF files in:
- data/raw_docs/naac/  (NAAC documents)
- data/raw_docs/nba/   (NBA documents)
```

---

## First Run

### Build Indices
```bash
python scripts/rebuild_ingestion.py
```

**Expected output**:
```
PHASE 1.1: INGESTION GRANULARITY REBUILD
========================================
Processing NAAC Documents...
Processing NBA Documents...
Building Indices...
✅ REBUILD COMPLETE

Total chunks: 442
Average tokens: 354.6
```

**Time**: ~2 minutes for 14 PDFs

---

## Test the System

### Run Verification Test
```bash
python tests/test_phase2_2_verification.py
```

**Expected output**:
```
Phase 2.2 Verification Test
===========================

TEST 1: NAAC 3.2.1 Query
✅ Retrieval completed successfully
   Retrieved 5 results

Result #1:
  Siblings Used: 3
  Child Tokens: 304
  Parent Tokens: 1150
  ✅ Token limit OK

✅ ALL TESTS PASSED
```

---

## Usage Examples

### Example 1: NAAC Query
```python
from retrieval.retrieval_pipeline import RetrievalPipeline

pipeline = RetrievalPipeline()
results = await pipeline.retrieve("What are the requirements for NAAC 3.2.1?")

for result in results:
    print(f"Criterion: {result['criterion']}")
    print(f"Context: {result['parent_context'][:200]}...")
    print(f"Siblings: {result['metadata']['num_siblings_used']}")
```

### Example 2: NBA Query
```python
results = await pipeline.retrieve("What are the faculty requirements for NBA Tier-II?")

for result in results:
    print(f"Source: {result['source']}")
    print(f"Page: {result['page']}")
    print(f"Reranker Score: {result['scores']['reranker']}")
```

---

## Common Issues

### Issue 1: CUDA Not Available
**Error**: `CUDA not available, using CPU`

**Solution**: Install PyTorch with CUDA:
```bash
pip install torch==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

### Issue 2: Groq API Error
**Error**: `GroqKeyPool: No API keys found`

**Solution**: Check your .env file:
```bash
# Make sure you have at least one key
GROQ_API_KEY_1=your_key_here
```

### Issue 3: No PDFs Found
**Error**: `Warning: No PDF files found`

**Solution**: Place PDFs in correct directories:
```bash
# Check if directories exist
ls data/raw_docs/naac/
ls data/raw_docs/nba/

# If empty, add your PDF files there
```

### Issue 4: Import Errors
**Error**: `ModuleNotFoundError: No module named 'ingestion'`

**Solution**: Run from correct directory:
```bash
# Make sure you're in accreditation_copilot/
cd accreditation_copilot
python tests/test_phase2_2_verification.py
```

---

## Project Structure (Quick Reference)

```
accreditation_copilot/
├── ingestion/          # PDF → Chunks
├── retrieval/          # Search & Retrieve
├── utils/              # Database, API pool
├── tests/              # Test files
├── scripts/            # Utility scripts
├── docs/               # Documentation
├── data/               # PDFs, database
└── indexes/            # Vector indices
```

---

## Next Steps

1. **Read the docs**:
   - [Complete Implementation Guide](COMPLETE_IMPLEMENTATION_GUIDE.md)
   - [Phase 2 Output Examples](PHASE2_OUTPUT_EXAMPLES.md)

2. **Explore the code**:
   - Start with `retrieval/retrieval_pipeline.py`
   - Check `ingestion/semantic_chunker.py`

3. **Run more tests**:
   ```bash
   python tests/test_phase2.py
   python tests/test_phase2_1.py
   ```

4. **Customize**:
   - Adjust chunk sizes in `ingestion/semantic_chunker.py`
   - Modify retrieval parameters in `retrieval/retrieval_pipeline.py`

---

## Performance Tips

### 1. Use GPU
- 10x faster embedding generation
- Enable CUDA in PyTorch

### 2. Multiple API Keys
- Add more Groq keys for higher rate limits
- Round-robin rotation automatically handles load

### 3. Optimize Chunk Size
- Current: 300-400 tokens (optimal)
- Smaller = more granular, slower
- Larger = less granular, faster

### 4. Adjust Top-K
- Increase for better recall
- Decrease for faster retrieval

---

## Getting Help

- **Documentation**: Check `docs/` folder
- **Issues**: Create GitHub issue
- **Questions**: [Add contact method]

---

**Ready to go!** 🚀

Start with: `python tests/test_phase2_2_verification.py`
