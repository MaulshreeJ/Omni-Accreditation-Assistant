"""
BM25 Builder - Phase 1
Builds BM25 indices for sparse retrieval.
"""

from rank_bm25 import BM25Okapi
from typing import List, Dict
from pathlib import Path
import pickle
import re


class BM25Builder:
    """
    Builds and persists BM25 indices for document chunks.
    """
    
    def __init__(self, index_dir: str = 'indexes'):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # BM25 storage
        self.bm25_indices = {}
        self.chunk_id_maps = {}
        self.tokenized_corpus = {}
    
    def tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization for BM25.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Lowercase and split on non-alphanumeric
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def build_bm25(self, chunks: List[Dict], index_name: str) -> BM25Okapi:
        """
        Build BM25 index for a set of chunks.
        
        Args:
            chunks: List of chunk dicts
            index_name: Name for the index
            
        Returns:
            BM25Okapi index
        """
        if not chunks:
            print(f"Warning: No chunks provided for {index_name}")
            return None
        
        print(f"\nBuilding BM25 index: {index_name}")
        print(f"  Chunks: {len(chunks)}")
        
        # Extract texts and chunk IDs
        texts = [chunk['text'] for chunk in chunks]
        chunk_ids = [chunk['chunk_id'] for chunk in chunks]
        
        # Tokenize corpus
        print(f"  Tokenizing corpus...")
        tokenized_corpus = [self.tokenize(text) for text in texts]
        
        # Build BM25 index
        bm25 = BM25Okapi(tokenized_corpus)
        
        print(f"  BM25 index built with {len(tokenized_corpus)} documents")
        
        # Store index and mappings
        self.bm25_indices[index_name] = bm25
        self.chunk_id_maps[index_name] = chunk_ids
        self.tokenized_corpus[index_name] = tokenized_corpus
        
        return bm25
    
    def build_indices_by_type(self, all_chunks: List[Dict]) -> Dict[str, BM25Okapi]:
        """
        Build separate BM25 indices for different document types.
        
        Args:
            all_chunks: All chunks from ingestion
            
        Returns:
            Dict of index_name -> BM25 index
        """
        # Group chunks by framework and doc_type
        grouped_chunks = {}
        
        for chunk in all_chunks:
            framework = chunk['framework']
            doc_type = chunk['doc_type']
            key = f"{framework.lower()}_{doc_type}"
            
            if key not in grouped_chunks:
                grouped_chunks[key] = []
            
            grouped_chunks[key].append(chunk)
        
        # Build BM25 index for each group
        indices = {}
        
        for index_name, chunks in grouped_chunks.items():
            bm25 = self.build_bm25(chunks, index_name)
            if bm25:
                indices[index_name] = bm25
        
        return indices
    
    def persist_bm25(self, index_name: str):
        """
        Persist BM25 index and mappings to disk.
        
        Args:
            index_name: Name of the index
        """
        if index_name not in self.bm25_indices:
            print(f"Warning: BM25 index {index_name} not found")
            return
        
        bm25 = self.bm25_indices[index_name]
        chunk_ids = self.chunk_id_maps[index_name]
        tokenized_corpus = self.tokenized_corpus[index_name]
        
        # Save BM25 index and data
        data = {
            'bm25': bm25,
            'chunk_ids': chunk_ids,
            'tokenized_corpus': tokenized_corpus
        }
        
        bm25_path = self.index_dir / f"{index_name}_bm25.pkl"
        with open(bm25_path, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"  Saved BM25 index: {bm25_path}")
    
    def persist_all_indices(self):
        """Persist all built BM25 indices."""
        print("\nPersisting BM25 indices...")
        
        for index_name in self.bm25_indices.keys():
            self.persist_bm25(index_name)
        
        print(f"All BM25 indices persisted to {self.index_dir}")
    
    def load_bm25(self, index_name: str) -> tuple:
        """
        Load BM25 index from disk.
        
        Args:
            index_name: Name of the index
            
        Returns:
            Tuple of (bm25, chunk_ids, tokenized_corpus)
        """
        bm25_path = self.index_dir / f"{index_name}_bm25.pkl"
        
        if not bm25_path.exists():
            raise FileNotFoundError(f"BM25 index not found: {bm25_path}")
        
        with open(bm25_path, 'rb') as f:
            data = pickle.load(f)
        
        self.bm25_indices[index_name] = data['bm25']
        self.chunk_id_maps[index_name] = data['chunk_ids']
        self.tokenized_corpus[index_name] = data['tokenized_corpus']
        
        return data['bm25'], data['chunk_ids'], data['tokenized_corpus']
    
    def get_index_info(self) -> Dict:
        """Get information about all BM25 indices."""
        info = {}
        
        for index_name, bm25 in self.bm25_indices.items():
            info[index_name] = {
                'num_documents': len(self.tokenized_corpus.get(index_name, [])),
                'num_chunks': len(self.chunk_id_maps.get(index_name, []))
            }
        
        return info


# Test function
if __name__ == "__main__":
    builder = BM25Builder()
    
    # Test with sample chunks
    test_chunks = [
        {
            'chunk_id': 'test-1',
            'text': 'NAAC accreditation requires comprehensive documentation',
            'framework': 'NAAC',
            'doc_type': 'policy'
        },
        {
            'chunk_id': 'test-2',
            'text': 'NBA focuses on outcome-based education',
            'framework': 'NBA',
            'doc_type': 'policy'
        }
    ]
    
    indices = builder.build_indices_by_type(test_chunks)
    print(f"\nBuilt {len(indices)} BM25 indices")
    
    info = builder.get_index_info()
    print(f"BM25 index info: {info}")
    
    builder.persist_all_indices()
