"""
Groq Multi-Key Pool Wrapper
Implements round-robin load balancing across multiple Groq API keys.

Phase 0: Scaffold only - HyDE and synthesis logic to be implemented in later phases.
"""

import os
from typing import List, Optional
from groq import Groq
from dotenv import load_dotenv

class GroqKeyPool:
    """
    Multi-key wrapper for Groq API with round-robin rotation.
    
    Loads multiple API keys from environment variables and rotates through them
    to distribute load and avoid rate limits.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize the Groq key pool.
        
        Args:
            env_file: Optional path to .env file. If None, uses default .env
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        self.keys: List[str] = []
        self.clients: List[Groq] = []
        self.current_index: int = 0
        
        # Load all GROQ_API_KEY_N from environment
        for i in range(1, 10):  # Support up to 9 keys
            key = os.getenv(f"GROQ_API_KEY_{i}")
            if key:
                self.keys.append(key)
                self.clients.append(Groq(api_key=key))
        
        if len(self.keys) == 0:
            raise ValueError("No Groq API keys found in environment variables. "
                           "Set GROQ_API_KEY_1, GROQ_API_KEY_2, etc.")
        
        print(f"[GroqKeyPool] Initialized with {len(self.keys)} API key(s)")
    
    def get_next_client(self) -> tuple[Groq, int]:
        """
        Get the next client in round-robin order.
        
        Returns:
            Tuple of (Groq client, key index)
        """
        client = self.clients[self.current_index]
        key_index = self.current_index
        
        # Rotate to next key
        self.current_index = (self.current_index + 1) % len(self.clients)
        
        return client, key_index + 1  # Return 1-indexed for logging
    
    def completion(self, model: str, messages: list, **kwargs) -> tuple[any, int]:
        """
        Create a chat completion using the next available key.
        
        Args:
            model: Model name (e.g., "llama-3.3-70b-versatile")
            messages: List of message dicts
            **kwargs: Additional arguments for Groq API
        
        Returns:
            Tuple of (response, key_index_used)
        """
        client, key_index = self.get_next_client()
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        
        return response, key_index
    
    def get_key_count(self) -> int:
        """Get the number of available API keys."""
        return len(self.keys)
    
    def reset_rotation(self):
        """Reset rotation to first key."""
        self.current_index = 0


# Example usage (for testing only)
if __name__ == "__main__":
    try:
        pool = GroqKeyPool()
        
        print(f"\nTesting Groq Key Pool with {pool.get_key_count()} key(s)")
        
        # Test 3 requests to see rotation
        for i in range(3):
            response, key_used = pool.completion(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Test request {i+1}"}],
                max_tokens=20
            )
            
            print(f"\nRequest {i+1}:")
            print(f"  Used key: GROQ_API_KEY_{key_used}")
            print(f"  Response: {response.choices[0].message.content[:50]}...")
        
        print("\n[OK] Groq Key Pool working correctly")
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
