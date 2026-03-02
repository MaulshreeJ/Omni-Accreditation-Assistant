"""
CUDA and PyTorch Verification Script
Tests GPU availability and compatibility
"""
import torch
import sys

print("=" * 60)
print("CUDA & PyTorch Verification")
print("=" * 60)

# Check PyTorch version
print(f"\n[OK] PyTorch Version: {torch.__version__}")

# Check CUDA availability
cuda_available = torch.cuda.is_available()
print(f"[OK] CUDA Available: {cuda_available}")

if cuda_available:
    # CUDA version
    print(f"[OK] CUDA Version: {torch.version.cuda}")
    
    # GPU count
    gpu_count = torch.cuda.device_count()
    print(f"[OK] GPU Count: {gpu_count}")
    
    # GPU details
    for i in range(gpu_count):
        print(f"\n--- GPU {i} Details ---")
        print(f"  Name: {torch.cuda.get_device_name(i)}")
        print(f"  Compute Capability: {torch.cuda.get_device_capability(i)}")
        
        # Memory info
        total_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
        print(f"  Total Memory: {total_memory:.2f} GB")
        
        # Current memory usage
        allocated = torch.cuda.memory_allocated(i) / (1024**3)
        reserved = torch.cuda.memory_reserved(i) / (1024**3)
        print(f"  Allocated Memory: {allocated:.2f} GB")
        print(f"  Reserved Memory: {reserved:.2f} GB")
    
    # Test tensor operation on GPU
    print("\n--- GPU Tensor Test ---")
    try:
        x = torch.randn(1000, 1000).cuda()
        y = torch.randn(1000, 1000).cuda()
        z = torch.matmul(x, y)
        print("[OK] GPU tensor operations working correctly")
        print(f"  Test tensor device: {z.device}")
        print(f"  Test tensor shape: {z.shape}")
    except Exception as e:
        print(f"[FAIL] GPU tensor test failed: {e}")
        sys.exit(1)
else:
    print("\n[FAIL] CUDA not available. GPU acceleration will not work.")
    print("  Possible reasons:")
    print("  - NVIDIA drivers not installed")
    print("  - PyTorch CPU-only version installed")
    print("  - CUDA toolkit version mismatch")
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] All CUDA checks passed!")
print("=" * 60)
