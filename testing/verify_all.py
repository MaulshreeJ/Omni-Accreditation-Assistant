"""
Simple ASCII-only verification script for Windows
"""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("="*60)
print("ENVIRONMENT VERIFICATION")
print("="*60)

# 1. Check CUDA & PyTorch
print("\n[1/4] Checking CUDA & PyTorch...")
try:
    import torch
    print(f"  PyTorch Version: {torch.__version__}")
    cuda_available = torch.cuda.is_available()
    print(f"  CUDA Available: {cuda_available}")
    
    if cuda_available:
        print(f"  CUDA Version: {torch.version.cuda}")
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
        
        # Test GPU operation
        x = torch.randn(100, 100).cuda()
        y = torch.randn(100, 100).cuda()
        z = torch.matmul(x, y)
        print("  [OK] GPU operations working")
        cuda_ok = True
    else:
        print("  [FAIL] CUDA not available")
        cuda_ok = False
except Exception as e:
    print(f"  [FAIL] Error: {e}")
    cuda_ok = False

# 2. Check FAISS & Embeddings
print("\n[2/4] Checking FAISS & Embeddings...")
try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    
    print(f"  FAISS Version: {faiss.__version__}")
    
    # Test embedding
    model = SentenceTransformer('BAAI/bge-small-en-v1.5', device='cuda' if cuda_ok else 'cpu')
    test_text = ["Test document for NAAC accreditation"]
    embeddings = model.encode(test_text, convert_to_numpy=True)
    
    print(f"  Embedding Dimension: {embeddings.shape[1]}")
    
    # Test FAISS
    index = faiss.IndexFlatIP(embeddings.shape[1])
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    
    distances, indices = index.search(embeddings, k=1)
    print(f"  [OK] FAISS operations working")
    faiss_ok = True
except Exception as e:
    print(f"  [FAIL] Error: {e}")
    faiss_ok = False

# 3. Check Ollama
print("\n[3/4] Checking Ollama...")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"  Ollama Running: Yes")
        print(f"  Models Available: {len(models)}")
        
        llava_found = any('llava' in m.get('name', '').lower() for m in models)
        if llava_found:
            print("  [OK] LLaVA model found")
            ollama_ok = True
        else:
            print("  [WARN] LLaVA model not found - run: ollama pull llava")
            ollama_ok = False
    else:
        print("  [FAIL] Ollama service error")
        ollama_ok = False
except Exception as e:
    print("  [FAIL] Ollama not running")
    print("  Install from: https://ollama.ai/download")
    ollama_ok = False

# 4. Check Groq API
print("\n[4/4] Checking Groq API...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.environ.get("GROQ_API_KEY")
    
    if api_key:
        print(f"  API Key Found: Yes (length: {len(api_key)})")
        
        from groq import Groq
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'OK' if you can read this"}],
            max_tokens=10
        )
        
        print("  [OK] Groq API working")
        groq_ok = True
    else:
        print("  [FAIL] GROQ_API_KEY not set")
        print("  Create .env file with: GROQ_API_KEY=your_key_here")
        groq_ok = False
except Exception as e:
    print(f"  [FAIL] Error: {e}")
    groq_ok = False

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"CUDA & PyTorch:     {'[OK]' if cuda_ok else '[FAIL]'}")
print(f"FAISS & Embeddings: {'[OK]' if faiss_ok else '[FAIL]'}")
print(f"Ollama & LLaVA:     {'[OK]' if ollama_ok else '[WARN]'}")
print(f"Groq API:           {'[OK]' if groq_ok else '[WARN]'}")

critical_ok = cuda_ok and faiss_ok
print("\n" + "="*60)
if cuda_ok and faiss_ok and ollama_ok and groq_ok:
    print("STATUS: ALL SYSTEMS READY")
elif critical_ok:
    print("STATUS: CORE SYSTEMS READY - Complete Ollama/Groq setup")
else:
    print("STATUS: SETUP INCOMPLETE - Review errors above")
print("="*60)

sys.exit(0 if critical_ok else 1)
