# Testing & Validation Scripts

This folder contains all validation and testing scripts for the Omni-Accreditation Compliance Copilot system.

## Phase 0 Validation

### Main Validation Script
```bash
python validate_phase0.py
```
Comprehensive validation of all Phase 0 components:
- CUDA & PyTorch
- FAISS (CPU/GPU)
- BGE Embedder & Reranker
- Groq API
- LLaVA (Ollama)
- LangSmith
- Project structure

### Individual Component Tests

**CUDA Verification:**
```bash
python verify_cuda.py
```
Tests GPU detection, CUDA availability, and tensor operations.

**FAISS Verification:**
```bash
python verify_faiss.py
```
Tests FAISS index creation, embedding generation, and similarity search.

**Groq API Verification:**
```bash
python verify_groq.py
```
Tests Groq API connectivity and completion generation.

**Ollama/LLaVA Verification:**
```bash
python verify_ollama.py
```
Tests Ollama service and LLaVA model availability.

**LLaVA Inference Test:**
```bash
python test_llava.py
```
Tests actual LLaVA inference with a sample prompt.

**All-in-One Verification:**
```bash
python verify_all.py
```
Quick verification of all critical components.

**Complete Verification Suite:**
```bash
python run_all_verifications.py
```
Runs all verification scripts and generates a summary report.

## Usage

### From Project Root
```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run validation
python testing/validate_phase0.py
```

### From Testing Folder
```bash
cd testing
python validate_phase0.py
```

## Output

Validation scripts generate:
- Console output with status indicators
- `baseline_metrics.json` (from validate_phase0.py)
- Performance measurements
- VRAM usage snapshots

## Status Indicators

- `[OK]` - Component working correctly
- `[WARN]` - Component working but with warnings
- `[FAIL]` - Component not working, needs attention

## Troubleshooting

If validation fails:
1. Check error messages in console output
2. Review `../docs/SETUP_GUIDE.md` for setup instructions
3. Verify environment variables in `.env` file
4. Check GPU drivers and CUDA installation
