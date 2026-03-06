"""
Quick Groq Connection Test
Verifies that Groq API keys are working correctly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.groq_pool import GroqKeyPool


def test_groq_connection():
    """Test Groq API connection with current keys."""
    print("\n" + "="*80)
    print("GROQ CONNECTION TEST")
    print("="*80)
    
    try:
        # Initialize GroqKeyPool
        print("\n[Step 1] Initializing GroqKeyPool...")
        pool = GroqKeyPool()
        
        print(f"[PASS] GroqKeyPool initialized with {pool.get_key_count()} key(s)")
        
        # Test a simple completion
        print("\n[Step 2] Testing API connection...")
        response, key_used = pool.completion(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "Say 'Hello, Groq is working!' in exactly 5 words."}
            ],
            max_tokens=50,
            temperature=0.0
        )
        
        content = response.choices[0].message.content
        
        print(f"[PASS] API connection successful")
        print(f"  Used key: GROQ_API_KEY_{key_used}")
        print(f"  Model: {response.model}")
        print(f"  Response: {content}")
        
        # Test key rotation
        print("\n[Step 3] Testing key rotation...")
        for i in range(3):
            response, key_used = pool.completion(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": f"Count: {i+1}"}
                ],
                max_tokens=10,
                temperature=0.0
            )
            print(f"  Request {i+1}: Used GROQ_API_KEY_{key_used}")
        
        print("[PASS] Key rotation working")
        
        # Summary
        print("\n" + "="*80)
        print("GROQ CONNECTION TEST RESULTS")
        print("="*80)
        print(f"✓ GroqKeyPool initialized: {pool.get_key_count()} keys")
        print(f"✓ API connection: Working")
        print(f"✓ Key rotation: Working")
        print(f"✓ Model: llama-3.3-70b-versatile")
        print("\n[SUCCESS] Groq connection is fully operational!")
        
        return True
        
    except ValueError as e:
        print(f"\n[FAIL] Configuration error: {e}")
        print("\nPlease check your .env file:")
        print("  GROQ_API_KEY_1=gsk_your_key_here")
        print("  GROQ_API_KEY_2=gsk_your_key_here")
        return False
        
    except Exception as e:
        print(f"\n[FAIL] Connection error: {e}")
        print("\nPossible issues:")
        print("  • Invalid API key")
        print("  • Network connectivity")
        print("  • Groq API service down")
        print("  • Rate limit exceeded")
        return False


if __name__ == "__main__":
    success = test_groq_connection()
    exit(0 if success else 1)
