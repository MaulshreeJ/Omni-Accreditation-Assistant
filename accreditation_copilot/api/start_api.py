"""
Simple startup script for the API
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Starting Omni Accreditation Copilot API...")
print(f"Python version: {sys.version}")
print(f"Working directory: {Path.cwd()}")

try:
    import uvicorn
    print("✓ uvicorn installed")
except ImportError:
    print("✗ uvicorn not installed. Run: pip install fastapi uvicorn")
    sys.exit(1)

try:
    import fastapi
    print("✓ fastapi installed")
except ImportError:
    print("✗ fastapi not installed. Run: pip install fastapi")
    sys.exit(1)

print("\nStarting server on http://localhost:8000")
print("API docs available at http://localhost:8000/docs")
print("\nPress Ctrl+C to stop the server\n")

if __name__ == "__main__":
    import os
    os.chdir(Path(__file__).parent)
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
