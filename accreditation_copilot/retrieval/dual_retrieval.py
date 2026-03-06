"""
Dual Retrieval - Phase 4 Milestone 4
Retrieves from both framework and institution indexes.

Performance Fix: Uses ModelManager for shared model instances.
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))
from retrieval.hybrid_retriever import HybridRetriever
from retrieval.reranker import Reranker
from retrieval.index_loader import IndexLoader
from models.model_manager import get_model_manager


class DualRetriever:
    """Retrieve from both framework and institution indexes."""
    
    def __init__(self, model_manager=None):
        """
        Initialize dual retriever with shared models.
        
        Args:
            model_manager: Optional ModelManager instance (for testing)
        """
        self.hybrid_retriever = HybridRetriever(model_manager=model_manager)
        self.reranker = Reranker(model_manager=model_manager)
        self.index_loader = IndexLoader()
        
        # Get shared embedder from ModelManager
        if model_manager is None:
            model_manager = get_model_manager()
        self.model_manager = model_manager
        self.embedder = model_manager.get_embedder()
    
    def retrieve(self, query: str, query_variants: List[str], framework: str,
                 query_type: str, top_k_framework: int = 3,  # Issue 11: Changed from 5 to 3
                 top_k_institution: int = 7) -> Tuple[List[Dict], bool]:  # Issue 11: Changed from 10 to 7
        """
        Retrieve from both framework and institution indexes.
        
        Issue 11: Slot allocation bias - framework provides context, institution provides evidence.
        
        Args:
            query: Original query
            query_variants: Expanded query variants
            framework: NAAC or NBA
            query_type: metric or policy
            top_k_framework: Number of framework results (default: 3)
            top_k_institution: Number of institution results (default: 7)
            
        Returns:
            Tuple of (merged_results, institution_evidence_available)
        """
        # Retrieve from framework index (existing)
        framework_results = self.hybrid_retriever.retrieve(
            query_variants,
            framework,
            query_type,
            query,
            explicit_metric=None,
            top_k_per_variant=15,
            final_top_k=top_k_framework
        )
        
        # Try to retrieve from institution index
        institution_results = []
        institution_evidence_available = False
        
        try:
            # Check if institution index exists
            institution_index_path = self.index_loader.institution_index_dir / 'institution.index'
            
            if institution_index_path.exists():
                # Retrieve from institution index
                institution_results = self._retrieve_institution(
                    query_variants,
                    query,
                    top_k_institution
                )
                
                # Issue 12: Empty institution index handling
                if institution_results and len(institution_results) > 0:
                    institution_evidence_available = True
        
        except Exception as e:
            # Institution index not available yet - this is expected
            # before any institutional evidence is uploaded
            pass
        
        # Merge results
        merged_results = framework_results + institution_results
        
        # Rerank merged results
        if merged_results:
            reranked = self.reranker.rerank(query, merged_results, top_k=15)
            
            # Apply evidence weight to prioritize institution chunks
            # This ensures table rows rank higher than framework context
            for result in reranked:
                chunk_id = result['chunk_id']
                chunk = self.index_loader.get_chunk_metadata(chunk_id)
                
                # CRITICAL: Preserve reranker_score from reranking step
                reranker_score = result.get('reranker_score', 0.0)
                
                if chunk:
                    # Infer evidence weight from source_type
                    source_type = chunk.get('source_type', 'framework')
                    
                    # Add source_type and text to result for downstream use
                    result['source_type'] = source_type
                    result['text'] = chunk.get('text', '')  # Add text for evidence grounding
                    result['child_text'] = chunk.get('text', '')  # For dimension checking
                    result['parent_context'] = chunk.get('parent_context', '')
                    
                    if source_type == 'institution':
                        # Institution chunks get strong priority boost
                        # Use 3.0x boost to ensure institutional evidence dominates
                        # This is necessary because framework chunks often have
                        # higher semantic similarity to compliance queries
                        evidence_weight = 3.0
                    else:
                        # Framework chunks get penalty (context only)
                        evidence_weight = 0.6
                    
                    # Apply weight to reranker score (preserve original score)
                    result['final_score'] = reranker_score * evidence_weight
                else:
                    # Fallback if metadata not found
                    result['source_type'] = 'framework'
                    result['text'] = ''
                    result['child_text'] = ''
                    result['parent_context'] = ''
                    result['final_score'] = reranker_score
            
            # Re-sort by final_score to prioritize institution evidence
            reranked_with_weights = sorted(reranked, key=lambda x: x.get('final_score', 0.0), reverse=True)
            
            return reranked_with_weights, institution_evidence_available
        
        return framework_results, institution_evidence_available
    
    def _retrieve_institution(self, query_variants: List[str], original_query: str,
                             top_k: int) -> List[Dict]:
        """
        Retrieve from institution index.
        
        Issue 12: Empty institution index handling.
        
        Args:
            query_variants: Expanded query variants
            original_query: Original query
            top_k: Number of results
            
        Returns:
            List of institution results
        """
        # Use the same hybrid retrieval approach but with institution index
        # For now, use simple retrieval from institution index
        
        # Load institution indexes
        try:
            faiss_index, chunk_ids = self.index_loader.load_faiss_index_institution('institution')
            bm25, bm25_chunk_ids, tokenized = self.index_loader.load_bm25_index_institution('institution')
        except:
            return []
        
        # Issue 12: Check if index is empty
        if faiss_index.ntotal == 0:
            return []
        
        # Use shared embedder from ModelManager
        query_text = query_variants[0] if query_variants else original_query
        query_embedding = self.embedder.encode([query_text], normalize_embeddings=True)[0]
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # FAISS search
        distances, indices = faiss_index.search(query_embedding, min(top_k, faiss_index.ntotal))
        
        # Build results
        results = []
        for idx, score in zip(indices[0], distances[0]):
            if idx < len(chunk_ids) and idx >= 0:  # Issue 12: Validate index
                results.append({
                    'chunk_id': chunk_ids[idx],
                    'dense_score': float(score),
                    'bm25_score': 0.0,
                    'fused_score': float(score),
                    'reranker_score': 0.0
                })
        
        return results
    
    def close(self):
        """Close resources."""
        self.hybrid_retriever.close()
        self.reranker.close()
        self.index_loader.close()
