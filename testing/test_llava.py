"""
Quick LLaVA inference test
Tests vision model with a simple prompt
"""
import requests
import json

print("Testing LLaVA inference...")
print("Note: First inference may take 30-60 seconds to load model into GPU")

OLLAMA_URL = "http://localhost:11434"

# Simple text-only test (no image)
test_prompt = {
    "model": "llava",
    "prompt": "Describe what you would look for when analyzing an infrastructure image for NAAC compliance. List 3 key elements.",
    "stream": False
}

try:
    print("\nSending request to LLaVA...")
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json=test_prompt,
        timeout=120  # Longer timeout for first run
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n[SUCCESS] LLaVA is working!")
        print("\nResponse:")
        print("-" * 60)
        print(result.get('response', ''))
        print("-" * 60)
        print(f"\nModel: {result.get('model', 'N/A')}")
        print(f"Total duration: {result.get('total_duration', 0) / 1e9:.2f}s")
    else:
        print(f"[FAIL] Status code: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("[WARN] Request timed out - LLaVA may be loading (this is normal on first run)")
    print("Try running this script again in a few moments")
except Exception as e:
    print(f"[FAIL] Error: {e}")
