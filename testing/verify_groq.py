"""
Groq API Verification Script
Tests Groq API connectivity and inference
"""
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("=" * 60)
print("Groq API Verification")
print("=" * 60)

# Check for API key
print("\n--- Checking Groq API Key ---")
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("✗ GROQ_API_KEY not found in environment variables")
    print("\n  Setup instructions:")
    print("  1. Get API key from: https://console.groq.com/keys")
    print("  2. Create a .env file in project root:")
    print("     GROQ_API_KEY=your_api_key_here")
    print("  3. Or set environment variable:")
    print("     Windows: set GROQ_API_KEY=your_api_key_here")
    print("     Linux/Mac: export GROQ_API_KEY=your_api_key_here")
    print("\n  After setting the key, run this script again")
else:
    print(f"✓ GROQ_API_KEY found (length: {len(api_key)})")
    
    # Test API connection
    print("\n--- Testing Groq API Connection ---")
    try:
        client = Groq(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Respond in JSON format."
                },
                {
                    "role": "user",
                    "content": "Generate a hypothetical ideal response for NAAC accreditation compliance. Return JSON with keys: metric, status, evidence."
                }
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        print("✓ Groq API connection successful")
        print(f"✓ Model used: {response.model}")
        print(f"✓ Tokens used: {response.usage.total_tokens}")
        print(f"\n  Response preview:")
        print(f"  {response.choices[0].message.content[:200]}...")
        
    except Exception as e:
        print(f"✗ Groq API test failed: {e}")
        print("\n  Possible issues:")
        print("  - Invalid API key")
        print("  - Network connectivity issues")
        print("  - API rate limits exceeded")

print("\n" + "=" * 60)
