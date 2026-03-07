"""
Institution Indexer - Phase 4 Milestone 3
Builds FAISS and BM25 indexes for institutional evidence chunks.

ARCHITECTURAL FIXES APPLIED:
- Issue 1: Criterion inference before indexing
- Issue 8: Embedding prefix for semantic retrieval
"""

import sys
import json
import sqlite3
import pickle
import numpy as np
import faiss
import torch
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class InstitutionIndexer:
    """Build and persist institution evidence indexes."""
    
    def __init__(self, model_name: str = 'BAAI/bge-base-en-v1.5', 
                 index_dir: str = 'indexes/institution',
                 db_path: str = 'data/metadata.db'):
        """
        Initialize indexer.
        
        Args:
            model_name: Embedding model (same as framework)
            index_dir: Directory for institution indexes
            db_path: SQLite database path
        """
        self.model_name = model_name
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = Path(db_path)
        
        # Load embedding model
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Loading embedding model on {device}...")
        self.model = SentenceTransformer(model_name, device=device)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25."""
        return text.lower().split()
    
    def _apply_criterion_inference(self, chunks: List[Dict[str, Any]], 
                                   parsed_doc: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Issue 1: Apply criterion inference to chunks.
        
        Args:
            chunks: List of chunks
            parsed_doc: Optional parsed document for context
            
        Returns:
            Chunks with inferred criterion and framework
        """
        # Use absolute import instead of relative
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from ingestion.institution.criterion_inferrer import CriterionInferrer
        
        inferrer = CriterionInferrer()
        
        print(f"\nApplying criterion inference...")
        inferred_count = 0
        
        for chunk in chunks:
            # Skip if already has criterion
            if chunk.get('criterion'):
                continue
            
            # Get context for inference
            page_text = ""
            table_caption = ""
            surrounding_text = ""
            
            # For table chunks, try to get table caption from table_id
            if chunk.get('chunk_type') == 'table_row':
                table_id = chunk.get('table_id', '')
                # Table ID might contain criterion info
                table_caption = table_id
            
            # Try to infer from available context
            criterion, framework = inferrer.infer_criterion_from_context(
                page_text, table_caption, surrounding_text
            )
            
            if criterion:
                chunk['criterion'] = criterion
                chunk['framework'] = framework
                inferred_count += 1
        
        print(f"  Inferred criterion for {inferred_count}/{len(chunks)} chunks")
        
        return chunks
    
    def _add_embedding_prefix(self, chunk: Dict[str, Any]) -> str:
        """
        Issue 8: Add embedding prefix for semantic retrieval.
        
        Format:
        - With criterion: "[{framework} {criterion} Evidence] {text}"
        - Without criterion: "[Institution Research Evidence] {text}"
        
        Args:
            chunk: Chunk dict
            
        Returns:
            Prefixed text for embedding
        """
        text = chunk['text']
        framework = chunk.get('framework')
        criterion = chunk.get('criterion')
        
        if framework and criterion:
            prefix = f"[{framework} {criterion} Evidence] "
        else:
            prefix = "[Institution Research Evidence] "
        
        return prefix + text
    
    def build_indexes(self, chunks: List[Dict[str, Any]], index_name: str = 'institution',
                     parsed_doc: Dict[str, Any] = None):
        """
        Build FAISS and BM25 indexes for institution chunks.
        
        Args:
            chunks: List of institution chunks
            index_name: Name for the indexes
            parsed_doc: Optional parsed document for criterion inference
        """
        if not chunks:
            print("No chunks provided")
            return
        
        print(f"\n{'='*80}")
        print(f"BUILDING INSTITUTION INDEXES")
        print(f"{'='*80}")
        print(f"Chunks: {len(chunks)}")
        print(f"Index name: {index_name}")
        
        # Issue 1: Apply criterion inference
        chunks = self._apply_criterion_inference(chunks, parsed_doc)
        
        # Extract texts and chunk IDs
        # Issue 8: Apply embedding prefix
        texts_for_embedding = [self._add_embedding_prefix(chunk) for chunk in chunks]
        texts_for_bm25 = [chunk['text'] for chunk in chunks]  # BM25 uses original text
        chunk_ids = [chunk['chunk_id'] for chunk in chunks]
        
        # Build FAISS index
        print(f"\n1. Building FAISS index (with embedding prefix)...")
        embeddings = self._embed_texts(texts_for_embedding)
        faiss_index = self._build_faiss_index(embeddings)
        print(f"   FAISS index built: {faiss_index.ntotal} vectors")
        
        # Build BM25 index
        print(f"\n2. Building BM25 index...")
        tokenized_corpus = [self._tokenize(text) for text in texts_for_bm25]
        bm25 = BM25Okapi(tokenized_corpus)
        print(f"   BM25 index built: {len(tokenized_corpus)} documents")
        
        # Save indexes
        print(f"\n3. Saving indexes...")
        self._save_faiss_index(faiss_index, chunk_ids, index_name)
        self._save_bm25_index(bm25, chunk_ids, tokenized_corpus, index_name)
        
        # Save metadata to database
        print(f"\n4. Saving metadata to database...")
        self._save_metadata(chunks)
        
        print(f"\n{'='*80}")
        print(f"INDEXES BUILT SUCCESSFULLY")
        print(f"{'='*80}")
        print(f"Location: {self.index_dir}")
        print(f"\nSummary:")
        print(f"  ✓ Indexed {len(chunks)} institution chunks")
        print(f"  ✓ FAISS index saved")
        print(f"  ✓ BM25 index saved")
        print(f"  ✓ Metadata updated")
        print(f"\nFiles:")
        print(f"  - {index_name}.index (FAISS)")
        print(f"  - {index_name}_mapping.pkl (chunk IDs)")
        print(f"  - {index_name}_bm25.pkl (BM25 + tokenized corpus)")
        print(f"  - metadata.db (SQLite)")
    
    def _embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of texts (with embedding prefix)
            batch_size: Batch size for encoding
            
        Returns:
            Normalized embeddings array
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        return embeddings.astype('float32')
    
    def _build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Build FAISS index from embeddings.
        
        Args:
            embeddings: Normalized embeddings
            
        Returns:
            FAISS index
        """
        # Create Inner Product index (for normalized vectors = cosine similarity)
        index = faiss.IndexFlatIP(self.embedding_dim)
        index.add(embeddings)
        
        return index
    
    def _save_faiss_index(self, index: faiss.Index, chunk_ids: List[str], index_name: str):
        """Save FAISS index and chunk ID mapping."""
        # Save FAISS index
        index_path = self.index_dir / f"{index_name}.index"
        faiss.write_index(index, str(index_path))
        print(f"   Saved FAISS index: {index_path}")
        
        # Save chunk ID mapping
        mapping_path = self.index_dir / f"{index_name}_mapping.pkl"
        with open(mapping_path, 'wb') as f:
            pickle.dump(chunk_ids, f)
        print(f"   Saved chunk mapping: {mapping_path}")
    
    def _save_bm25_index(self, bm25: BM25Okapi, chunk_ids: List[str], 
                         tokenized_corpus: List[List[str]], index_name: str):
        """Save BM25 index with tokenized corpus."""
        bm25_path = self.index_dir / f"{index_name}_bm25.pkl"
        
        data = {
            'bm25': bm25,
            'chunk_ids': chunk_ids,
            'tokenized_corpus': tokenized_corpus
        }
        
        with open(bm25_path, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"   Saved BM25 index: {bm25_path}")
    
    def _save_metadata(self, chunks: List[Dict[str, Any]]):
        """
        Save chunk metadata to SQLite database.
        
        Issue 9: Metadata alignment (page_number, source_path, source_type).
        
        Args:
            chunks: List of chunks with metadata
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Insert chunks
        for chunk in chunks:
            # Use inferred framework or placeholder
            framework = chunk.get('framework') or 'INSTITUTION'
            
            # Issue 9: Use page_number and source_path
            page_number = chunk.get('page_number', chunk.get('page', 1))
            source_path = chunk.get('source_path', chunk.get('source', 'unknown'))
            source_type = chunk.get('source_type', 'institution')  # Default to institution
            
            cursor.execute('''
                INSERT OR REPLACE INTO chunks 
                (chunk_id, source, page, framework, criterion, doc_type, text, source_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                chunk['chunk_id'],
                source_path,
                page_number,
                framework,
                chunk.get('criterion'),  # Can be NULL
                chunk['doc_type'],
                chunk['text'],
                source_type
            ))
        
        conn.commit()
        conn.close()
        
        print(f"   Saved {len(chunks)} chunks to database")


# Test function
if __name__ == '__main__':
    # Issue 13: Windows encoding fix
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    
    # Load sample chunks
    chunks_path = Path('data/institution_chunks_sample.json')
    
    if not chunks_path.exists():
        print(f"Sample chunks not found: {chunks_path}")
        print("Run test_milestone2.py first to generate sample chunks")
        sys.exit(1)
    
    with open(chunks_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chunks = data['chunks']
    
    print(f"Loaded {len(chunks)} chunks from {chunks_path}")
    
    # Build indexes
    indexer = InstitutionIndexer()
    indexer.build_indexes(chunks, index_name='institution')
    
    print("\nIndexing complete!")
