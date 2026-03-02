"""
FAISS Verification Script
Tests FAISS CPU/GPU functionality with embeddings
"""
import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer

print("=" * 60)
print("FAISS Verification")
print("=" * 60)

# Check FAISS version
print(f"\n✓ FAISS Version: {faiss.__version__}")

# Test embedding generation
print("\n--- Embedding Generation Test ---")
try:
    model = SentenceTransformer('BAAI/bge-small-en-v1.5')  # Using small model for quick test
    print(f"✓ Model loaded: BAAI/bge-small-en-v1.5")
    
    # Generate test embeddings
    test_docs = [
        "NAAC accreditation requires comprehensive documentation",
        "Infrastructure facilities must meet minimum standards",
        "Faculty qualifications are essential for NBA accreditation"
    ]
    
    embeddings = model.encode(test_docs, convert_to_numpy=True)
    print(f"✓ Generated embeddings shape: {embeddings.shape}")
    embedding_dim = embeddings.shape[1]
    print(f"✓ Embedding dimension: {embedding_dim}")
    
except Exception as e:
    print(f"✗ Embedding generation failed: {e}")
    import sys
    sys.exit(1)

# Test FAISS CPU index
print("\n--- FAISS CPU Index Test ---")
try:
    # Create CPU index
    cpu_index = faiss.IndexFlatIP(embedding_dim)
    print(f"✓ Created FAISS CPU index (Inner Product)")
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Add embeddings
    cpu_index.add(embeddings)
    print(f"✓ Added {cpu_index.ntotal} vectors to index")
    
    # Test search
    query_embedding = model.encode(["What are NAAC requirements?"], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)
    
    distances, indices = cpu_index.search(query_embedding, k=2)
    print(f"✓ Search successful")
    print(f"  Top result index: {indices[0][0]}")
    print(f"  Top result score: {distances[0][0]:.4f}")
    print(f"  Top result text: {test_docs[indices[0][0]]}")
    
except Exception as e:
    print(f"✗ FAISS CPU test failed: {e}")
    import sys
    sys.exit(1)

# Test FAISS GPU (if available)
print("\n--- FAISS GPU Test ---")
if torch.cuda.is_available():
    try:
        # Check if FAISS GPU is available
        res = faiss.StandardGpuResources()
        print("✓ FAISS GPU resources initialized")
        
        # Try to create GPU index
        gpu_index = faiss.index_cpu_to_gpu(res, 0, cpu_index)
        print("✓ Successfully moved index to GPU")
        
        # Test GPU search
        distances_gpu, indices_gpu = gpu_index.search(query_embedding, k=2)
        print(f"✓ GPU search successful")
        print(f"  GPU result matches CPU: {np.array_equal(indices, indices_gpu)}")
        
        print("\n✓ FAISS GPU is AVAILABLE and working!")
        
    except Exception as e:
        print(f"⚠ FAISS GPU not available: {e}")
        print("  Note: FAISS-CPU is installed. For GPU support on Windows:")
        print("  - Build FAISS from source with CUDA support, or")
        print("  - Use conda: conda install -c pytorch faiss-gpu")
        print("  - CPU version will work but slower for large datasets")
else:
    print("⚠ CUDA not available, skipping GPU test")

print("\n" + "=" * 60)
print("✓ FAISS verification complete!")
print("=" * 60)
