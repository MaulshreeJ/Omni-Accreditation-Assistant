"""
HyDE Retriever - Phase 2
Hypothetical Document Embeddings retrieval.
"""

import re
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import torch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from retrieval.index_loader import IndexLoader
from utils.groq_pool import GroqKeyPool


class HyDERetriever:
    """
    HyDE (Hypothetical Document Embeddings) retrieval.
    Generates hypothetical answer, embeds it, and searches.
    """
    
    # Index mapping
    INDEX_MAP = {
        ('NAAC', 'metric'): 'naac_metric',
        ('NAAC', 'policy'): 'naac_policy',
        ('NBA', 'metric'): 'nba_metric',
        ('NBA', 'policy'): 'nba_policy',
        ('NBA', 'prequalifier'): 'nba_prequalifier'
    }
    
    def __init__(self, model_name: str = 'BAAI/bge-base-en-v1.5'):
        self.index_loader = IndexLoader()
        self.groq_pool = GroqKeyPool()
        
        # Load embedding model
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = SentenceTransformer(model_name, device=device)
        
        # Cache
        self.cache = {}
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for caching."""
        return re.sub(r'\s+', ' ', query.lower().strip())
    
    def _extract_criterion(self, query: str) -> str:
        """Extract criterion from query for cache key."""
        # NAAC metric
        naac_match = re.search(r'\b(\d\.\d\.\d)\b', query)
        if naac_match:
            return naac_match.group(1)
        
        # NBA PO/PEO
        nba_match = re.search(r'\b(PO|PEO|PSO)(\d+)\b', query, re.IGNORECASE)
        if nba_match:
            return f"{nba_match.group(1).upper()}{nba_match.group(2)}"
        
        return self._normalize_query(query)
    
    def generate_hypothetical_answer(self, query: str, framework: str) -> str:
        """
        Generate hypothetical answer using Groq.
        
        Args:
            query: User query
            framework: NAAC or NBA
            
        Returns:
            Hypothetical answer text
        """
        # Check cache
        cache_key = (framework, self._extract_criterion(query))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Construct prompt
        prompt = f"""Generate an ideal A++ compliant answer for this {framework} accreditation query.

Query: {query}

Provide a comprehensive, evidence-based answer that would satisfy {framework} evaluators. Include:
- Specific requirements
- Documentation needed
- Compliance criteria
- Best practices

Keep the answer focused and under 300 words."""
        
        try:
            response, key_used = self.groq_pool.completion(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=400
            )
            
            hypothetical_answer = response.choices[0].message.content.strip()
            
            # Cache
            self.cache[cache_key] = hypothetical_answer
            
            return hypothetical_answer
            
        except Exception as e:
            print(f"Error generating hypothetical answer: {e}")
            # Fallback to original query
            return query
    
    def retrieve(self, query: str, framework: str, query_type: str, 
                top_k: int = 10) -> List[Dict]:
        """
        HyDE retrieval.
        
        Args:
            query: Original query
            framework: NAAC or NBA
            query_type: metric, policy, or prequalifier
            top_k: Number of results
            
        Returns:
            Top-K results with dense scores
        """
        # Get index name
        index_key = (framework, query_type)
        if index_key not in self.INDEX_MAP:
            raise ValueError(f"Invalid index key: {index_key}")
        
        index_name = self.INDEX_MAP[index_key]
        
        # Generate hypothetical answer
        hypothetical_answer = self.generate_hypothetical_answer(query, framework)
        
        # Embed hypothetical answer
        embedding = self.model.encode(hypothetical_answer, convert_to_numpy=True)
        
        # FAISS search (dense only)
        results = self.index_loader.search_faiss(index_name, embedding, top_k=top_k)
        
        return results
    
    def close(self):
        """Close resources."""
        self.index_loader.close()


# Test function
if __name__ == "__main__":
    retriever = HyDERetriever()
    
    query = "Are we compliant with NAAC 3.2.1?"
    
    results = retriever.retrieve(
        query=query,
        framework='NAAC',
        query_type='metric',
        top_k=10
    )
    
    print(f"Retrieved {len(results)} results")
    for i, result in enumerate(results[:5], 1):
        print(f"\n{i}. Chunk ID: {result['chunk_id']}")
        print(f"   Dense: {result['dense_score']:.3f}")
    
    retriever.close()
