"""
Query Expander - Phase 2
Expands queries using Groq LLM.
"""

import json
import re
from typing import List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.groq_pool import GroqKeyPool


class QueryExpander:
    """
    Expands queries into multiple variants using Groq.
    """
    
    def __init__(self):
        self.groq_pool = GroqKeyPool()
        self.cache = {}
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for caching."""
        return re.sub(r'\s+', ' ', query.lower().strip())
    
    def expand_query(self, query: str, framework: str, max_retries: int = 2) -> List[str]:
        """
        Expand query into 6 variants.
        
        Args:
            query: Original query
            framework: NAAC or NBA
            max_retries: Number of retry attempts
            
        Returns:
            List of 6 query variants
        """
        # Check cache
        cache_key = (framework, self._normalize_query(query))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Construct prompt
        prompt = f"""Generate 6 search query variants for the following accreditation compliance query.

Framework: {framework}
Original Query: {query}

Create variants that:
1. Rephrase the question
2. Use synonyms and related terms
3. Focus on different aspects (requirements, evidence, documentation)
4. Include framework-specific terminology

Return ONLY a JSON object with this exact format:
{{
  "variants": [
    "variant 1",
    "variant 2",
    "variant 3",
    "variant 4",
    "variant 5",
    "variant 6"
  ]
}}"""
        
        # Try to get response
        for attempt in range(max_retries + 1):
            try:
                response, key_used = self.groq_pool.completion(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=500
                )
            except Exception as e:
                # FIX 1: Rate limit protection
                error_str = str(e).lower()
                if '429' in error_str or 'rate limit' in error_str:
                    print(f"[QUERY EXPANSION] Rate limit hit, using fallback (attempt {attempt + 1}/{max_retries + 1})")
                    if attempt >= max_retries:
                        return [query]  # Fallback to original query
                    continue
                elif attempt >= max_retries:
                    print(f"[QUERY EXPANSION] Error after {max_retries} retries: {e}")
                    return [query]  # Fallback to original query
                continue
            
            try:
                
                # Extract JSON from response
                content = response.choices[0].message.content.strip()
                
                # Try to parse JSON
                # Remove markdown code blocks if present
                content = re.sub(r'```json\s*', '', content)
                content = re.sub(r'```\s*$', '', content)
                
                data = json.loads(content)
                
                if 'variants' in data and isinstance(data['variants'], list):
                    variants = data['variants'][:6]  # Ensure max 6
                    
                    # Ensure we have 6 variants
                    while len(variants) < 6:
                        variants.append(query)  # Pad with original if needed
                    
                    # Cache result
                    self.cache[cache_key] = variants
                    
                    return variants
                
            except json.JSONDecodeError as e:
                if attempt < max_retries:
                    continue
                else:
                    print(f"JSON parse error after {max_retries} retries: {e}")
            except Exception as e:
                if attempt < max_retries:
                    continue
                else:
                    print(f"Error expanding query: {e}")
        
        # Fallback: return original query 6 times
        return [query] * 6


# Test function
if __name__ == "__main__":
    expander = QueryExpander()
    
    query = "Are we compliant with NAAC 3.2.1?"
    variants = expander.expand_query(query, "NAAC")
    
    print(f"Original: {query}\n")
    print("Variants:")
    for i, variant in enumerate(variants, 1):
        print(f"{i}. {variant}")
