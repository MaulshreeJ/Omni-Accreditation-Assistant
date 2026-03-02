"""
Ingestion Orchestrator - Phase 1
Coordinates the complete ingestion pipeline.
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.pdf_processor import PDFProcessor
from ingestion.semantic_chunker import SemanticChunker
from utils.metadata_store import MetadataStore
from retrieval.index_builder import IndexBuilder
from retrieval.bm25_builder import BM25Builder


class IngestionOrchestrator:
    """
    Orchestrates the complete ingestion pipeline.
    """
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.chunker = SemanticChunker()
        self.metadata_store = MetadataStore("data/metadata.db")
        self.index_builder = IndexBuilder(index_dir='indexes')
        self.bm25_builder = BM25Builder(index_dir='indexes')
        
        self.all_chunks = []
        self.stats = {
            'NAAC': {'policy': 0, 'metric': 0},
            'NBA': {'policy': 0, 'metric': 0, 'prequalifier': 0}
        }
    
    def process_framework(self, framework: str, data_dir: str):
        """
        Process all PDFs for a framework.
        
        Args:
            framework: 'NAAC' or 'NBA'
            data_dir: Directory containing PDFs
        """
        print(f"\n{'='*60}")
        print(f"Processing {framework} Documents")
        print(f"{'='*60}")
        
        data_path = Path(data_dir)
        
        if not data_path.exists():
            print(f"Warning: Directory not found: {data_path}")
            return
        
        pdf_files = list(data_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"Warning: No PDF files found in {data_path}")
            return
        
        print(f"Found {len(pdf_files)} PDF files")
        
        for pdf_file in pdf_files:
            print(f"\n--- Processing: {pdf_file.name} ---")
            
            try:
                # Step 1: Extract pages
                pages = self.pdf_processor.process_pdf(str(pdf_file))
                print(f"  Extracted {len(pages)} pages")
                
                if not pages:
                    print(f"  Warning: No pages extracted from {pdf_file.name}")
                    continue
                
                # Step 2: Chunk semantically
                chunks = self.chunker.chunk_pages(pages, framework)
                print(f"  Generated {len(chunks)} chunks")
                
                if not chunks:
                    print(f"  Warning: No chunks generated from {pdf_file.name}")
                    continue
                
                # Step 3: Store in database
                inserted = self.metadata_store.insert_chunks_batch(chunks)
                print(f"  Inserted {inserted} chunks into database")
                
                # Step 4: Collect for indexing
                self.all_chunks.extend(chunks)
                
                # Update stats
                for chunk in chunks:
                    doc_type = chunk['doc_type']
                    if framework == 'NAAC' and doc_type in self.stats['NAAC']:
                        self.stats['NAAC'][doc_type] += 1
                    elif framework == 'NBA' and doc_type in self.stats['NBA']:
                        self.stats['NBA'][doc_type] += 1
                
            except Exception as e:
                print(f"  Error processing {pdf_file.name}: {e}")
                continue
    
    def build_indices(self):
        """Build FAISS and BM25 indices."""
        if not self.all_chunks:
            print("\nNo chunks to index!")
            return
        
        print(f"\n{'='*60}")
        print(f"Building Indices")
        print(f"{'='*60}")
        print(f"Total chunks to index: {len(self.all_chunks)}")
        
        # Build FAISS indices
        print("\n--- Building FAISS Indices ---")
        faiss_indices = self.index_builder.build_indices_by_type(self.all_chunks)
        print(f"Built {len(faiss_indices)} FAISS indices")
        
        # Build BM25 indices
        print("\n--- Building BM25 Indices ---")
        bm25_indices = self.bm25_builder.build_indices_by_type(self.all_chunks)
        print(f"Built {len(bm25_indices)} BM25 indices")
        
        # Persist indices
        self.index_builder.persist_all_indices()
        self.bm25_builder.persist_all_indices()
    
    def validate(self):
        """Validate ingestion results."""
        print(f"\n{'='*60}")
        print(f"Validation")
        print(f"{'='*60}")
        
        # Check database
        db_count = self.metadata_store.get_chunk_count()
        print(f"\nDatabase:")
        print(f"  Total chunks in SQLite: {db_count}")
        print(f"  Total chunks processed: {len(self.all_chunks)}")
        print(f"  Match: {'✓' if db_count == len(self.all_chunks) else '✗'}")
        
        # Check indices
        print(f"\nFAISS Indices:")
        faiss_info = self.index_builder.get_index_info()
        for name, info in faiss_info.items():
            print(f"  {name}: {info['num_vectors']} vectors")
        
        print(f"\nBM25 Indices:")
        bm25_info = self.bm25_builder.get_index_info()
        for name, info in bm25_info.items():
            print(f"  {name}: {info['num_documents']} documents")
        
        # Check chunk quality
        print(f"\nChunk Quality:")
        empty_chunks = sum(1 for c in self.all_chunks if not c['text'].strip())
        print(f"  Empty chunks: {empty_chunks}")
        
        # Check token counts
        from tiktoken import get_encoding
        tokenizer = get_encoding("cl100k_base")
        
        oversized = 0
        for chunk in self.all_chunks:
            tokens = len(tokenizer.encode(chunk['text']))
            if tokens > 1500:
                oversized += 1
        
        print(f"  Chunks exceeding 1500 tokens: {oversized}")
        
        # Metadata validation
        print(f"\nMetadata:")
        frameworks = set(c['framework'] for c in self.all_chunks)
        doc_types = set(c['doc_type'] for c in self.all_chunks)
        print(f"  Frameworks: {frameworks}")
        print(f"  Document types: {doc_types}")
    
    def print_summary(self):
        """Print ingestion summary."""
        print(f"\n{'='*60}")
        print(f"Ingestion Summary")
        print(f"{'='*60}")
        
        print(f"\nFramework: NAAC")
        for doc_type, count in self.stats['NAAC'].items():
            if count > 0:
                print(f"  {doc_type.capitalize()} chunks: {count}")
        
        print(f"\nFramework: NBA")
        for doc_type, count in self.stats['NBA'].items():
            if count > 0:
                print(f"  {doc_type.capitalize()} chunks: {count}")
        
        total = sum(self.stats['NAAC'].values()) + sum(self.stats['NBA'].values())
        print(f"\nTotal chunks: {total}")
        
        # Criterion Quality Check
        print(f"\n{'='*60}")
        print(f"Criterion Quality Check (5 Random Metric Chunks)")
        print(f"{'='*60}")
        
        # Get metric chunks only
        metric_chunks = [c for c in self.all_chunks if c['doc_type'] == 'metric']
        
        if metric_chunks:
            import random
            sample_size = min(5, len(metric_chunks))
            sample_chunks = random.sample(metric_chunks, sample_size)
            
            for i, chunk in enumerate(sample_chunks):
                print(f"\nMetric Chunk {i+1}:")
                print(json.dumps({
                    'framework': chunk['framework'],
                    'doc_type': chunk['doc_type'],
                    'criterion': chunk.get('criterion'),
                    'source': chunk['source'],
                    'page': chunk['page']
                }, indent=2))
            
            # Count non-null criteria
            non_null = sum(1 for c in sample_chunks if c.get('criterion'))
            print(f"\nCriterion extraction: {non_null}/{sample_size} chunks have non-null criterion")
        else:
            print("\nNo metric chunks found!")
        
        # Sample chunks
        print(f"\n{'='*60}")
        print(f"Sample Chunks (3)")
        print(f"{'='*60}")
        
        for i, chunk in enumerate(self.all_chunks[:3]):
            print(f"\nChunk {i+1}:")
            print(json.dumps({
                'chunk_id': chunk['chunk_id'],
                'framework': chunk['framework'],
                'doc_type': chunk['doc_type'],
                'criterion': chunk.get('criterion'),
                'page': chunk['page'],
                'source': chunk['source'],
                'text_preview': chunk['text'][:200] + '...'
            }, indent=2))
    
    def run(self, naac_dir: str = None, nba_dir: str = None):
        """
        Run the complete ingestion pipeline.
        
        Args:
            naac_dir: Optional custom path to NAAC documents
            nba_dir: Optional custom path to NBA documents
        """
        print(f"\n{'='*60}")
        print(f"PHASE 1 - INGESTION PIPELINE")
        print(f"{'='*60}")
        
        # Use custom paths or defaults
        naac_path = naac_dir or 'data/raw_docs/naac'
        nba_path = nba_dir or 'data/raw_docs/nba'
        
        # Process NAAC documents
        self.process_framework('NAAC', naac_path)
        
        # Process NBA documents
        self.process_framework('NBA', nba_path)
        
        # Build indices
        self.build_indices()
        
        # Validate
        self.validate()
        
        # Print summary
        self.print_summary()
        
        # Close database
        self.metadata_store.close()
        
        print(f"\n{'='*60}")
        print(f"PHASE 1 COMPLETE")
        print(f"{'='*60}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Phase 1 Ingestion Pipeline')
    parser.add_argument('--naac-dir', type=str, help='Path to NAAC documents directory')
    parser.add_argument('--nba-dir', type=str, help='Path to NBA documents directory')
    
    args = parser.parse_args()
    
    orchestrator = IngestionOrchestrator()
    orchestrator.run(naac_dir=args.naac_dir, nba_dir=args.nba_dir)


if __name__ == "__main__":
    main()
