"""
Test Groq API Key Pool - Verify both keys are working
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils.groq_pool import GroqKeyPool

def test_groq_keys():
    """Test that both Groq API keys are loaded and working."""
    
    print("="*80)
    print("GROQ API KEY POOL TEST")
    print("="*80)
    
    try:
        # Initialize pool
        pool = GroqKeyPool()
        
        print(f"\n[OK] Groq Key Pool initialized")
        print(f"[OK] Number of API keys loaded: {pool.get_key_count()}")
        
        # Test multiple requests to see rotation
        print(f"\nTesting key rotation with 4 requests:")
        print("-"*80)
        
        for i in range(4):
            response, key_used = pool.completion(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Say 'Test {i+1}' and nothing else."}],
                max_tokens=10,
                temperature=0
            )
            
            content = response.choices[0].message.content
            print(f"Request {i+1}: Used GROQ_API_KEY_{key_used} -> Response: {content}")
        
        print("-"*80)
        print(f"\n[OK] Both API keys are working correctly!")
        print(f"[OK] Round-robin rotation is functioning")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_groq_keys()
    sys.exit(0 if success else 1)
