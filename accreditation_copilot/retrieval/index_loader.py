"""
Index Loader - Phase 2
Loads and searches FAISS and BM25 indices.
"""

import faiss
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.metadata_store import MetadataStore


class IndexLoader:
    """
    Loads FAISS and BM25 indices and provides search functionality.
    """
    
    def __init__(self, index_dir: str = 'indexes', db_path: str = 'data/metadata.db'):
        self.index_dir = Path(index_dir)
        self.framework_index_dir = self.index_dir / 'framework'  # MILESTONE 1: Framework indexes
        self.institution_index_dir = self.index_dir / 'institution'  # MILESTONE 1: Institution indexes
        self.metadata_store = MetadataStore(db_path)
        
        # Cache for loaded indices
        self.faiss_indices = {}
        self.faiss_mappings = {}
        self.bm25_indices = {}
        self.bm25_mappings = {}
        self.bm25_tokenized = {}
    
    def load_faiss_index(self, index_name: str) -> Tuple[faiss.Index, List[str]]:
        """
        Load FAISS index and chunk ID mapping.
        
        Args:
            index_name: Name of the index (e.g., 'naac_metric')
            
        Returns:
            Tuple of (faiss_index, chunk_ids)
        """
        if index_name in self.faiss_indices:
            return self.faiss_indices[index_name], self.faiss_mappings[index_name]
        
        # MILESTONE 1: Look in framework directory for existing indexes
        index_path = self.framework_index_dir / f"{index_name}.index"
        mapping_path = self.framework_index_dir / f"{index_name}_mapping.pkl"
        
        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index not found: {index_path}")
        
        # Load FAISS index
        index = faiss.read_index(str(index_path))
        
        # Load chunk ID mapping
        with open(mapping_path, 'rb') as f:
            chunk_ids = pickle.load(f)
        
        # Cache
        self.faiss_indices[index_name] = index
        self.faiss_mappings[index_name] = chunk_ids
        
        return index, chunk_ids
    
    def load_bm25_index(self, index_name: str) -> Tuple[object, List[str], List[List[str]]]:
        """
        Load BM25 index, chunk ID mapping, and tokenized corpus.
        
        Args:
            index_name: Name of the index (e.g., 'naac_metric')
            
        Returns:
            Tuple of (bm25_index, chunk_ids, tokenized_corpus)
        """
        if index_name in self.bm25_indices:
            return (
                self.bm25_indices[index_name],
                self.bm25_mappings[index_name],
                self.bm25_tokenized[index_name]
            )
        
        bm25_path = self.framework_index_dir / f"{index_name}_bm25.pkl"  # MILESTONE 1: Framework directory
        
        if not bm25_path.exists():
            raise FileNotFoundError(f"BM25 index not found: {bm25_path}")
        
        # Load BM25 data
        with open(bm25_path, 'rb') as f:
            data = pickle.load(f)
        
        bm25 = data['bm25']
        chunk_ids = data['chunk_ids']
        tokenized_corpus = data['tokenized_corpus']
        
        # Cache
        self.bm25_indices[index_name] = bm25
        self.bm25_mappings[index_name] = chunk_ids
        self.bm25_tokenized[index_name] = tokenized_corpus
        
        return bm25, chunk_ids, tokenized_corpus
    
    def search_faiss(self, index_name: str, embedding: np.ndarray, top_k: int = 15) -> List[Dict]:
        """
        Search FAISS index.
        
        Args:
            index_name: Name of the index
            embedding: Query embedding (normalized)
            top_k: Number of results
            
        Returns:
            List of dicts with chunk_id and dense_score
        """
        index, chunk_ids = self.load_faiss_index(index_name)
        
        # Ensure embedding is 2D and normalized
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        faiss.normalize_L2(embedding)
        
        # Search
        scores, indices = index.search(embedding.astype('float32'), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(chunk_ids):
                results.append({
                    'chunk_id': chunk_ids[idx],
                    'dense_score': float(score)
                })
        
        return results
    
    def search_bm25(self, index_name: str, query_tokens: List[str], top_k: int = 15) -> List[Dict]:
        """
        Search BM25 index.
        
        Args:
            index_name: Name of the index
            query_tokens: Tokenized query
            top_k: Number of results
            
        Returns:
            List of dicts with chunk_id and bm25_score
        """
        bm25, chunk_ids, _ = self.load_bm25_index(index_name)
        
        # Get BM25 scores
        scores = bm25.get_scores(query_tokens)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if idx < len(chunk_ids):
                results.append({
                    'chunk_id': chunk_ids[idx],
                    'bm25_score': float(scores[idx])
                })
        
        return results
    
    def get_chunk_metadata(self, chunk_id: str) -> Dict:
        """
        Get chunk metadata from SQLite.
        
        Args:
            chunk_id: Chunk ID
            
        Returns:
            Chunk dict with all metadata
        """
        return self.metadata_store.get_chunk(chunk_id)
    
    def load_faiss_index_institution(self, index_name: str) -> Tuple[faiss.Index, List[str]]:
        """
        Load FAISS index from institution directory.
        
        Args:
            index_name: Name of the index (e.g., 'institution')
            
        Returns:
            Tuple of (faiss_index, chunk_ids)
        """
        cache_key = f"institution_{index_name}"
        if cache_key in self.faiss_indices:
            return self.faiss_indices[cache_key], self.faiss_mappings[cache_key]
        
        index_path = self.institution_index_dir / f"{index_name}.index"
        mapping_path = self.institution_index_dir / f"{index_name}_mapping.pkl"
        
        if not index_path.exists():
            raise FileNotFoundError(f"Institution FAISS index not found: {index_path}")
        
        # Load FAISS index
        index = faiss.read_index(str(index_path))
        
        # Load chunk ID mapping
        with open(mapping_path, 'rb') as f:
            chunk_ids = pickle.load(f)
        
        # Cache
        self.faiss_indices[cache_key] = index
        self.faiss_mappings[cache_key] = chunk_ids
        
        return index, chunk_ids
    
    def load_bm25_index_institution(self, index_name: str) -> Tuple:
        """
        Load BM25 index from institution directory.
        
        Args:
            index_name: Name of the index (e.g., 'institution')
            
        Returns:
            Tuple of (bm25_index, chunk_ids, tokenized_corpus)
        """
        cache_key = f"institution_{index_name}"
        if cache_key in self.bm25_indices:
            return (
                self.bm25_indices[cache_key],
                self.bm25_mappings[cache_key],
                self.bm25_tokenized[cache_key]
            )
        
        bm25_path = self.institution_index_dir / f"{index_name}_bm25.pkl"
        
        if not bm25_path.exists():
            raise FileNotFoundError(f"Institution BM25 index not found: {bm25_path}")
        
        # Load BM25 data
        with open(bm25_path, 'rb') as f:
            data = pickle.load(f)
        
        bm25 = data['bm25']
        chunk_ids = data['chunk_ids']
        tokenized_corpus = data['tokenized_corpus']
        
        # Cache
        self.bm25_indices[cache_key] = bm25
        self.bm25_mappings[cache_key] = chunk_ids
        self.bm25_tokenized[cache_key] = tokenized_corpus
        
        return bm25, chunk_ids, tokenized_corpus
    
    def close(self):
        """Close database connection."""
        self.metadata_store.close()


# Test function
if __name__ == "__main__":
    loader = IndexLoader()
    
    # Test FAISS load
    index, chunk_ids = loader.load_faiss_index('naac_metric')
    print(f"Loaded FAISS index: {index.ntotal} vectors")
    
    # Test BM25 load
    bm25, chunk_ids, tokenized = loader.load_bm25_index('naac_metric')
    print(f"Loaded BM25 index: {len(chunk_ids)} documents")
    
    loader.close()
