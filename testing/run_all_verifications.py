"""
Master Verification Script
Runs all environment checks and generates a summary report
"""
import subprocess
import sys
from datetime import datetime

def run_script(script_name, description):
    """Run a verification script and capture results"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"✗ {script_name} timed out")
        return False
    except Exception as e:
        print(f"✗ Error running {script_name}: {e}")
        return False

def main():
    print("="*60)
    print("ENVIRONMENT VERIFICATION SUITE")
    print("Omni-Accreditation & Compliance Copilot")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {}
    
    # Run all verification scripts
    scripts = [
        ("verify_cuda.py", "CUDA & PyTorch"),
        ("verify_faiss.py", "FAISS & Embeddings"),
        ("verify_ollama.py", "Ollama & LLaVA"),
        ("verify_groq.py", "Groq API"),
    ]
    
    for script, description in scripts:
        results[description] = run_script(script, description)
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    for component, passed in results.items():
        status = "✅ PASS" if passed else "⚠️  NEEDS SETUP"
        print(f"{component:.<40} {status}")
    
    # Overall status
    all_passed = all(results.values())
    critical_passed = results.get("CUDA & PyTorch", False) and results.get("FAISS & Embeddings", False)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL COMPONENTS VERIFIED - READY FOR DEVELOPMENT")
    elif critical_passed:
        print("⚠️  CORE COMPONENTS READY - COMPLETE SETUP FOR FULL FUNCTIONALITY")
        print("\nRequired Actions:")
        if not results.get("Ollama & LLaVA", False):
            print("  - Install Ollama and pull LLaVA model")
        if not results.get("Groq API", False):
            print("  - Configure GROQ_API_KEY in .env file")
    else:
        print("❌ CRITICAL COMPONENTS MISSING - REVIEW SETUP GUIDE")
    
    print("="*60)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return 0 if critical_passed else 1

if __name__ == "__main__":
    sys.exit(main())
