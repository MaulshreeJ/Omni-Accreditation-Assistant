"""
Ollama + LLaVA Verification Script
Tests local vision model inference
"""
import requests
import json
import base64
import os

print("=" * 60)
print("Ollama + LLaVA Verification")
print("=" * 60)

# Check if Ollama is running
OLLAMA_URL = "http://localhost:11434"

print("\n--- Checking Ollama Service ---")
try:
    response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
    if response.status_code == 200:
        print("✓ Ollama service is running")
        
        # List available models
        models = response.json().get('models', [])
        print(f"✓ Available models: {len(models)}")
        
        llava_found = False
        for model in models:
            model_name = model.get('name', '')
            print(f"  - {model_name}")
            if 'llava' in model_name.lower():
                llava_found = True
        
        if not llava_found:
            print("\n⚠ LLaVA model not found!")
            print("  To install LLaVA, run:")
            print("  ollama pull llava")
        else:
            print("\n✓ LLaVA model is available")
            
            # Test LLaVA inference
            print("\n--- Testing LLaVA Inference ---")
            test_prompt = {
                "model": "llava",
                "prompt": "Describe this image in JSON format with keys: description, objects_detected, compliance_relevant",
                "stream": False
            }
            
            try:
                response = requests.post(
                    f"{OLLAMA_URL}/api/generate",
                    json=test_prompt,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✓ LLaVA inference test successful")
                    print(f"  Response preview: {result.get('response', '')[:100]}...")
                else:
                    print(f"✗ LLaVA inference failed: {response.status_code}")
                    
            except Exception as e:
                print(f"✗ LLaVA inference test failed: {e}")
    else:
        print(f"✗ Ollama service returned status code: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to Ollama service")
    print("\n  Ollama is NOT installed or NOT running")
    print("\n  Installation instructions:")
    print("  1. Download from: https://ollama.ai/download")
    print("  2. Install Ollama")
    print("  3. Run: ollama serve (starts the service)")
    print("  4. Run: ollama pull llava (downloads LLaVA model)")
    print("\n  After installation, run this script again")
    
except Exception as e:
    print(f"✗ Error checking Ollama: {e}")

print("\n" + "=" * 60)
