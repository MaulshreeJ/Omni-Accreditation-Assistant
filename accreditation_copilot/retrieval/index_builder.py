"""
Index Builder - Phase 1
Builds FAISS indices for different document types.
"""

import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from pathlib import Path
import pickle


class IndexBuilder:
    """
    Builds and persists FAISS indices for document chunks.
    """
    
    def __init__(self, model_name: str = 'BAAI/bge-base-en-v1.5', 
                 batch_size: int = 32, index_dir: str = 'indexes'):
        self.model_name = model_name
        self.batch_size = batch_size
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Load model
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Loading embedding model on {device}...")
        self.model = SentenceTransformer(model_name, device=device)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.embedding_dim}")
        
        # Index storage
        self.indices = {}
        self.chunk_id_maps = {}  # Maps index position to chunk_id
    
    def build_index(self, chunks: List[Dict], index_name: str) -> faiss.Index:
        """
        Build FAISS index for a set of chunks.
        
        Args:
            chunks: List of chunk dicts
            index_name: Name for the index
            
        Returns:
            FAISS index
        """
        if not chunks:
            print(f"Warning: No chunks provided for {index_name}")
            return None
        
        print(f"\nBuilding index: {index_name}")
        print(f"  Chunks: {len(chunks)}")
        
        # Extract texts and chunk IDs
        texts = [chunk['text'] for chunk in chunks]
        chunk_ids = [chunk['chunk_id'] for chunk in chunks]
        
        # Generate embeddings in batches
        print(f"  Generating embeddings...")
        embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = self.model.encode(
                batch,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            embeddings.append(batch_embeddings)
        
        embeddings = np.vstack(embeddings).astype('float32')
        print(f"  Embeddings shape: {embeddings.shape}")
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index (Inner Product for normalized vectors = cosine similarity)
        index = faiss.IndexFlatIP(self.embedding_dim)
        index.add(embeddings)
        
        print(f"  Index built with {index.ntotal} vectors")
        
        # Store index and mapping
        self.indices[index_name] = index
        self.chunk_id_maps[index_name] = chunk_ids
        
        return index
    
    def build_indices_by_type(self, all_chunks: List[Dict]) -> Dict[str, faiss.Index]:
        """
        Build separate indices for different document types.
        
        Args:
            all_chunks: All chunks from ingestion
            
        Returns:
            Dict of index_name -> FAISS index
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
        
        # Build index for each group
        indices = {}
        
        for index_name, chunks in grouped_chunks.items():
            index = self.build_index(chunks, index_name)
            if index:
                indices[index_name] = index
        
        return indices
    
    def persist_index(self, index_name: str):
        """
        Persist index and chunk ID mapping to disk.
        
        Args:
            index_name: Name of the index
        """
        if index_name not in self.indices:
            print(f"Warning: Index {index_name} not found")
            return
        
        index = self.indices[index_name]
        chunk_ids = self.chunk_id_maps[index_name]
        
        # Save FAISS index
        index_path = self.index_dir / f"{index_name}.index"
        faiss.write_index(index, str(index_path))
        print(f"  Saved index: {index_path}")
        
        # Save chunk ID mapping
        mapping_path = self.index_dir / f"{index_name}_mapping.pkl"
        with open(mapping_path, 'wb') as f:
            pickle.dump(chunk_ids, f)
        print(f"  Saved mapping: {mapping_path}")
    
    def persist_all_indices(self):
        """Persist all built indices."""
        print("\nPersisting indices...")
        
        for index_name in self.indices.keys():
            self.persist_index(index_name)
        
        print(f"All indices persisted to {self.index_dir}")
    
    def load_index(self, index_name: str) -> tuple:
        """
        Load index and mapping from disk.
        
        Args:
            index_name: Name of the index
            
        Returns:
            Tuple of (index, chunk_ids)
        """
        index_path = self.index_dir / f"{index_name}.index"
        mapping_path = self.index_dir / f"{index_name}_mapping.pkl"
        
        if not index_path.exists():
            raise FileNotFoundError(f"Index not found: {index_path}")
        
        # Load FAISS index
        index = faiss.read_index(str(index_path))
        
        # Load chunk ID mapping
        with open(mapping_path, 'rb') as f:
            chunk_ids = pickle.load(f)
        
        self.indices[index_name] = index
        self.chunk_id_maps[index_name] = chunk_ids
        
        return index, chunk_ids
    
    def get_index_info(self) -> Dict:
        """Get information about all indices."""
        info = {}
        
        for index_name, index in self.indices.items():
            info[index_name] = {
                'num_vectors': index.ntotal,
                'dimension': self.embedding_dim,
                'num_chunks': len(self.chunk_id_maps.get(index_name, []))
            }
        
        return info


# Test function
if __name__ == "__main__":
    builder = IndexBuilder()
    
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
    print(f"\nBuilt {len(indices)} indices")
    
    info = builder.get_index_info()
    print(f"Index info: {info}")
    
    builder.persist_all_indices()
