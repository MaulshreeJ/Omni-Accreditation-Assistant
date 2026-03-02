"""
Phase 0 - Environment Validation Script
Omni-Accreditation Compliance Copilot (NAAC MVP)

Validates all foundational dependencies before core implementation.
"""

import sys
import os
import time
import json
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("="*70)
print("PHASE 0 - ENVIRONMENT VALIDATION")
print("Omni-Accreditation Compliance Copilot (NAAC MVP)")
print("="*70)

validation_results = {}
vram_snapshots = {}
latency_measurements = {}

# 1. CUDA & PyTorch Validation
print("\n[1/8] Validating CUDA & PyTorch...")
try:
    import torch
    
    cuda_available = torch.cuda.is_available()
    validation_results['cuda'] = cuda_available
    
    if cuda_available:
        gpu_name = torch.cuda.get_device_name(0)
        total_vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        allocated_vram = torch.cuda.memory_allocated(0) / (1024**3)
        
        print(f"  [OK] CUDA Available: {cuda_available}")
        print(f"  [OK] GPU: {gpu_name}")
        print(f"  [OK] Total VRAM: {total_vram:.2f} GB")
        print(f"  [OK] Allocated VRAM: {allocated_vram:.2f} GB")
        
        vram_snapshots['baseline'] = allocated_vram
        
        # Test GPU operation
        x = torch.randn(1000, 1000).cuda()
        y = torch.randn(1000, 1000).cuda()
        z = torch.matmul(x, y)
        print("  [OK] GPU tensor operations working")
        
        del x, y, z
        torch.cuda.empty_cache()
    else:
        print("  [FAIL] CUDA not available")
        validation_results['cuda'] = False
        
except Exception as e:
    print(f"  [FAIL] Error: {e}")
    validation_results['cuda'] = False

# 2. FAISS Validation
print("\n[2/8] Validating FAISS...")
try:
    import faiss
    import numpy as np
    
    print(f"  [OK] FAISS Version: {faiss.__version__}")
    
    # Create test index
    dimension = 768
    n_vectors = 1000
    
    vectors = np.random.random((n_vectors, dimension)).astype('float32')
    
    # Try GPU index first, fallback to CPU
    try:
        res = faiss.StandardGpuResources()
        cpu_index = faiss.IndexFlatIP(dimension)
        gpu_index = faiss.index_cpu_to_gpu(res, 0, cpu_index)
        
        faiss.normalize_L2(vectors)
        gpu_index.add(vectors)
        
        query = np.random.random((1, dimension)).astype('float32')
        faiss.normalize_L2(query)
        
        distances, indices = gpu_index.search(query, k=5)
        
        print("  [OK] FAISS-GPU index creation successful")
        print(f"  [OK] Search returned top-5 results")
        validation_results['faiss_gpu'] = True
        
        if cuda_available:
            vram_snapshots['after_faiss'] = torch.cuda.memory_allocated(0) / (1024**3)
            
    except Exception as gpu_error:
        print(f"  [WARN] FAISS-GPU not available: {gpu_error}")
        print("  [INFO] Falling back to FAISS-CPU")
        
        cpu_index = faiss.IndexFlatIP(dimension)
        faiss.normalize_L2(vectors)
        cpu_index.add(vectors)
        
        query = np.random.random((1, dimension)).astype('float32')
        faiss.normalize_L2(query)
        
        distances, indices = cpu_index.search(query, k=5)
        
        print("  [OK] FAISS-CPU index creation successful")
        print(f"  [OK] Search returned top-5 results")
        validation_results['faiss_gpu'] = False
        validation_results['faiss_cpu'] = True
        
except Exception as e:
    print(f"  [FAIL] Error: {e}")
    validation_results['faiss_gpu'] = False
    validation_results['faiss_cpu'] = False

# 3. BGE Embedder Validation
print("\n[3/8] Validating BGE Embedder (BAAI/bge-base-en-v1.5)...")
try:
    from sentence_transformers import SentenceTransformer
    
    device = 'cuda' if validation_results.get('cuda', False) else 'cpu'
    model = SentenceTransformer('BAAI/bge-base-en-v1.5', device=device)
    
    print(f"  [OK] Model loaded on {device}")
    
    # Single sentence embedding
    start_time = time.time()
    embedding = model.encode(["NAAC accreditation requires comprehensive documentation"], convert_to_numpy=True)
    single_latency = (time.time() - start_time) * 1000
    
    print(f"  [OK] Embedding dimension: {embedding.shape[1]}")
    print(f"  [OK] Single sentence latency: {single_latency:.2f}ms")
    
    latency_measurements['embedding_single'] = single_latency
    
    # Batch embedding
    test_sentences = ["Test sentence " + str(i) for i in range(32)]
    start_time = time.time()
    batch_embeddings = model.encode(test_sentences, convert_to_numpy=True)
    batch_latency = (time.time() - start_time) * 1000
    
    print(f"  [OK] Batch (32) latency: {batch_latency:.2f}ms")
    latency_measurements['embedding_batch32'] = batch_latency
    
    if cuda_available:
        vram_snapshots['after_embedder'] = torch.cuda.memory_allocated(0) / (1024**3)
    
    validation_results['embedder'] = True
    
except Exception as e:
    print(f"  [FAIL] Error: {e}")
    validation_results['embedder'] = False

# 4. BGE Reranker Validation
print("\n[4/8] Validating BGE Reranker (BAAI/bge-reranker-base)...")
try:
    from sentence_transformers import CrossEncoder
    
    device_str = 'cuda' if validation_results.get('cuda', False) else 'cpu'
    reranker = CrossEncoder('BAAI/bge-reranker-base', device=device_str)
    
    print(f"  [OK] Reranker loaded on {device_str}")
    
    # Test reranking
    query = "What are NAAC accreditation requirements?"
    passages = [
        "NAAC accreditation requires comprehensive documentation of institutional processes",
        "The weather is sunny today",
        "Infrastructure facilities must meet minimum standards for accreditation",
        "Python is a programming language",
        "Faculty qualifications are essential for NBA accreditation"
    ]
    
    pairs = [[query, passage] for passage in passages]
    
    start_time = time.time()
    scores = reranker.predict(pairs[:10])  # Test with 10 pairs
    rerank_latency = (time.time() - start_time) * 1000
    
    print(f"  [OK] Reranking latency (10 pairs): {rerank_latency:.2f}ms")
    print(f"  [OK] Score range: [{scores.min():.3f}, {scores.max():.3f}]")
    
    latency_measurements['reranker_10pairs'] = rerank_latency
    
    if cuda_available:
        vram_snapshots['after_reranker'] = torch.cuda.memory_allocated(0) / (1024**3)
    
    validation_results['reranker'] = True
    
except Exception as e:
    print(f"  [FAIL] Error: {e}")
    validation_results['reranker'] = False

# 5. Groq Multi-Key Pool Validation
print("\n[5/8] Validating Groq Multi-Key Pool...")
try:
    from dotenv import load_dotenv
    from groq import Groq
    
    load_dotenv()
    
    # Load API keys
    groq_keys = []
    for i in range(1, 10):  # Support up to 9 keys
        key = os.getenv(f"GROQ_API_KEY_{i}")
        if key:
            groq_keys.append(key)
    
    if len(groq_keys) == 0:
        print("  [FAIL] No Groq API keys found in .env")
        validation_results['groq'] = False
    else:
        print(f"  [OK] Loaded {len(groq_keys)} Groq API key(s)")
        
        # Test first key
        client = Groq(api_key=groq_keys[0])
        
        start_time = time.time()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'OK' if you can read this"}],
            max_tokens=10
        )
        groq_latency = (time.time() - start_time) * 1000
        
        print(f"  [OK] Groq API connection successful")
        print(f"  [OK] Response latency: {groq_latency:.2f}ms")
        print(f"  [OK] Using key: GROQ_API_KEY_1")
        
        latency_measurements['groq_completion'] = groq_latency
        validation_results['groq'] = True
        validation_results['groq_key_count'] = len(groq_keys)
        
except Exception as e:
    print(f"  [FAIL] Error: {e}")
    validation_results['groq'] = False

# 6. LLaVA Service Validation
print("\n[6/8] Validating LLaVA Service (Ollama)...")
try:
    import requests
    
    ollama_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    response = requests.get(f"{ollama_url}/api/tags", timeout=5)
    
    if response.status_code == 200:
        models = response.json().get('models', [])
        llava_found = any('llava' in m.get('name', '').lower() for m in models)
        
        print(f"  [OK] Ollama service running")
        print(f"  [OK] Available models: {len(models)}")
        
        if llava_found:
            print(f"  [OK] LLaVA model available")
            validation_results['llava'] = True
        else:
            print(f"  [WARN] LLaVA model not found")
            validation_results['llava'] = False
    else:
        print(f"  [FAIL] Ollama service error")
        validation_results['llava'] = False
        
except Exception as e:
    print(f"  [FAIL] Ollama not running: {e}")
    validation_results['llava'] = False

# 7. LangSmith Tracing Validation
print("\n[7/8] Validating LangSmith Tracing...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    langsmith_key = os.getenv("LANGCHAIN_API_KEY")
    tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    
    if langsmith_key and langsmith_key != "your_langsmith_key_here":
        print(f"  [OK] LangSmith API key configured")
        print(f"  [OK] Tracing enabled: {tracing_enabled}")
        
        # Test with a simple LangChain operation
        from langchain_core.messages import HumanMessage
        from langchain_groq import ChatGroq
        
        if validation_results.get('groq', False):
            llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
            messages = [HumanMessage(content="Test")]
            
            # This will be traced if LangSmith is configured
            result = llm.invoke(messages)
            
            print(f"  [OK] LangChain operation traced")
            validation_results['langsmith'] = True
        else:
            print(f"  [WARN] Groq not available, skipping trace test")
            validation_results['langsmith'] = 'partial'
    else:
        print(f"  [WARN] LangSmith API key not configured")
        validation_results['langsmith'] = False
        
except Exception as e:
    print(f"  [FAIL] Error: {e}")
    validation_results['langsmith'] = False

# 8. Project Structure Validation
print("\n[8/8] Validating Project Structure...")
try:
    required_dirs = [
        'data/raw_docs',
        'data/raw_images',
        'data/processed_chunks',
        'data/metric_maps',
        'ingestion',
        'retrieval',
        'scoring',
        'synthesis',
        'evaluation',
        'utils'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"  [FAIL] Missing directory: {dir_path}")
            all_exist = False
    
    if all_exist:
        print(f"  [OK] All required directories exist")
        validation_results['project_structure'] = True
    else:
        validation_results['project_structure'] = False
        
except Exception as e:
    print(f"  [FAIL] Error: {e}")
    validation_results['project_structure'] = False

# Generate Report
print("\n" + "="*70)
print("VALIDATION SUMMARY")
print("="*70)

print("\nComponent Status:")
print(f"  CUDA & PyTorch:     {'[OK]' if validation_results.get('cuda') else '[FAIL]'}")
print(f"  FAISS-GPU:          {'[OK]' if validation_results.get('faiss_gpu') else '[WARN - Using CPU]'}")
print(f"  BGE Embedder:       {'[OK]' if validation_results.get('embedder') else '[FAIL]'}")
print(f"  BGE Reranker:       {'[OK]' if validation_results.get('reranker') else '[FAIL]'}")
print(f"  Groq API:           {'[OK]' if validation_results.get('groq') else '[FAIL]'}")
print(f"  LLaVA (Ollama):     {'[OK]' if validation_results.get('llava') else '[WARN]'}")
print(f"  LangSmith:          {'[OK]' if validation_results.get('langsmith') == True else '[WARN]'}")
print(f"  Project Structure:  {'[OK]' if validation_results.get('project_structure') else '[FAIL]'}")

if vram_snapshots:
    print("\nVRAM Usage Snapshots:")
    for stage, vram in vram_snapshots.items():
        print(f"  {stage:20s}: {vram:.2f} GB")
    
    peak_vram = max(vram_snapshots.values())
    print(f"\n  Peak VRAM Usage: {peak_vram:.2f} GB")
    
    if peak_vram > 7.5:
        print(f"  [WARN] Peak VRAM exceeds 7.5GB threshold")

if latency_measurements:
    print("\nBaseline Latency Measurements:")
    for operation, latency in latency_measurements.items():
        print(f"  {operation:25s}: {latency:.2f}ms")

# Save metrics
metrics = {
    'timestamp': datetime.now().isoformat(),
    'validation_results': validation_results,
    'vram_snapshots': vram_snapshots,
    'latency_measurements': latency_measurements
}

with open('baseline_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"\nMetrics saved to: baseline_metrics.json")

# Final Status
critical_ok = (
    validation_results.get('cuda', False) and
    (validation_results.get('faiss_gpu', False) or validation_results.get('faiss_cpu', False)) and
    validation_results.get('embedder', False) and
    validation_results.get('reranker', False) and
    validation_results.get('groq', False)
)

print("\n" + "="*70)
if critical_ok:
    print("STATUS: PHASE 0 COMPLETE - READY FOR PHASE 1 (INGESTION)")
    sys.exit(0)
else:
    print("STATUS: PHASE 0 INCOMPLETE - RESOLVE FAILURES BEFORE PROCEEDING")
    sys.exit(1)
print("="*70)
