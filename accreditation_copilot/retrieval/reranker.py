"""
Reranker - Phase 2
Cross-encoder reranking using BGE reranker.

Performance Fix: Uses ModelManager for shared model instances.
"""

import torch
import numpy as np
from typing import List, Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from retrieval.index_loader import IndexLoader
from models.model_manager import get_model_manager


class Reranker:
    """
    Cross-encoder reranker using BAAI/bge-reranker-base.
    Uses shared models from ModelManager for performance.
    """
    
    def __init__(self, max_length: int = 512, model_manager=None):
        """
        Initialize reranker with shared models.
        
        Args:
            max_length: Maximum sequence length
            model_manager: Optional ModelManager instance (for testing)
        """
        self.max_length = max_length
        
        # Get shared models from ModelManager
        if model_manager is None:
            model_manager = get_model_manager()
        
        self.tokenizer_tiktoken = model_manager.get_tiktoken_tokenizer()
        self.tokenizer = model_manager.get_reranker_tokenizer()
        self.model = model_manager.get_reranker_model()
        self.device = model_manager.get_device()
        
        self.index_loader = IndexLoader()
    
    def _truncate_text(self, text: str, max_tokens: int = 800) -> str:
        """
        Truncate text to max tokens.
        
        Args:
            text: Input text
            max_tokens: Maximum tokens
            
        Returns:
            Truncated text
        """
        tokens = self.tokenizer_tiktoken.encode(text)
        if len(tokens) > max_tokens:
            tokens = tokens[:max_tokens]
            text = self.tokenizer_tiktoken.decode(tokens)
        return text
    
    def rerank(self, query: str, candidates: List[Dict], top_k: int = 5, 
              batch_size: int = 8) -> List[Dict]:
        """
        Rerank candidates using cross-encoder.
        
        Args:
            query: Original query
            candidates: List of candidate dicts with chunk_id
            top_k: Number of results to return
            batch_size: Batch size for inference
            
        Returns:
            Top-K reranked results with reranker scores
        """
        if not candidates:
            return []
        
        # Get chunk texts from database
        chunk_texts = []
        for candidate in candidates:
            chunk = self.index_loader.get_chunk_metadata(candidate['chunk_id'])
            if chunk:
                # Truncate text
                text = self._truncate_text(chunk['text'], max_tokens=800)
                chunk_texts.append(text)
            else:
                chunk_texts.append("")
        
        # Create pairs
        pairs = [[query, text] for text in chunk_texts]
        
        # Batch inference
        all_scores = []
        
        with torch.no_grad():
            for i in range(0, len(pairs), batch_size):
                batch_pairs = pairs[i:i + batch_size]
                
                # Tokenize
                inputs = self.tokenizer(
                    batch_pairs,
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors='pt'
                ).to(self.device)
                
                # Forward pass
                outputs = self.model(**inputs)
                
                # Extract logits correctly - handle both 1D and 2D cases
                logits = outputs.logits
                if logits.dim() > 1:
                    # If 2D, take the first column (relevance score)
                    logits = logits[:, 0]
                
                # Apply sigmoid to convert logits to probabilities [0, 1]
                scores = torch.sigmoid(logits).cpu().numpy()
                
                all_scores.extend(scores.tolist())
        
        # Use sigmoid-normalized scores directly (already in [0, 1] range)
        normalized_scores = all_scores
        
        # Add reranker scores to candidates
        for candidate, score in zip(candidates, normalized_scores):
            candidate['reranker_score'] = float(score)
        
        # Sort by reranker score
        candidates.sort(key=lambda x: x['reranker_score'], reverse=True)
        
        # Return top-K
        return candidates[:top_k]
    
    def close(self):
        """Close resources."""
        self.index_loader.close()


# Test function
if __name__ == "__main__":
    reranker = Reranker()
    
    # Mock candidates
    candidates = [
        {'chunk_id': 'test-1', 'fused_score': 0.8},
        {'chunk_id': 'test-2', 'fused_score': 0.7}
    ]
    
    query = "Are we compliant with NAAC 3.2.1?"
    
    results = reranker.rerank(query, candidates, top_k=5)
    
    print(f"Reranked {len(results)} results")
    
    reranker.close()
