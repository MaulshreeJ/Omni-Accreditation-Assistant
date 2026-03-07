"""
Institution Document Ingestion Runner
Processes uploaded institution documents and builds indexes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ingestion.institution.pdf_parser import PDFParser
from ingestion.institution.table_extractor import TableExtractor
from ingestion.institution.row_chunker import RowChunker
from ingestion.institution.institution_indexer import InstitutionIndexer


def run_institution_ingestion(raw_docs_dir: str = "data/raw_docs"):
    """
    Run complete institution document ingestion pipeline.
    
    Args:
        raw_docs_dir: Directory containing uploaded PDFs
        
    Returns:
        dict: Ingestion results with counts
    """
    print("\n" + "="*60)
    print("INSTITUTION DOCUMENT INGESTION")
    print("="*60)
    
    raw_docs_path = Path(raw_docs_dir)
    
    if not raw_docs_path.exists():
        print(f"Error: Directory not found: {raw_docs_path}")
        return {"status": "error", "message": "Raw docs directory not found"}
    
    # Find all PDFs
    pdf_files = list(raw_docs_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"Warning: No PDF files found in {raw_docs_path}")
        return {"status": "error", "message": "No PDF files found", "files_processed": 0}
    
    print(f"Found {len(pdf_files)} PDF file(s) to process")
    
    # Initialize components
    parser = PDFParser()
    table_extractor = TableExtractor()
    row_chunker = RowChunker()
    indexer = InstitutionIndexer()
    
    all_chunks = []
    files_processed = 0
    
    # Process each PDF
    for pdf_file in pdf_files:
        print(f"\n--- Processing: {pdf_file.name} ---")
        
        try:
            # Step 1: Parse PDF
            parsed_doc = parser.parse(str(pdf_file))
            print(f"  Parsed {len(parsed_doc['pages'])} pages")
            print(f"  Found {len([t for p in parsed_doc['pages'] for t in p.get('tables', [])])} tables")
            
            # Step 2: Extract tables from all pages
            all_tables = []
            for page in parsed_doc['pages']:
                page_tables = table_extractor.extract_all(page)
                all_tables.extend(page_tables)
            print(f"  Extracted {len(all_tables)} tables")
            
            # Step 3: Chunk document (tables + paragraphs)
            chunks = row_chunker.chunk_document(parsed_doc)
            print(f"  Created {len(chunks)} chunks")
            
            if chunks:
                all_chunks.extend(chunks)
                files_processed += 1
            
        except Exception as e:
            print(f"  Error processing {pdf_file.name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if not all_chunks:
        print("\nNo chunks created from any files!")
        return {
            "status": "error",
            "message": "No chunks created",
            "files_processed": files_processed,
            "chunks_created": 0
        }
    
    print(f"\n--- Building Indexes ---")
    print(f"Total chunks to index: {len(all_chunks)}")
    
    # Step 4: Build indexes
    try:
        indexer.build_indexes(all_chunks, index_name='institution')
        print("  FAISS index built and saved")
        print("  BM25 index built and saved")
        print("  Metadata saved to database")
        
    except Exception as e:
        print(f"  Error building indexes: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Index building failed: {str(e)}",
            "files_processed": files_processed,
            "chunks_created": len(all_chunks)
        }
    
    print("\n" + "="*60)
    print("INGESTION COMPLETE")
    print("="*60)
    print(f"Files processed: {files_processed}")
    print(f"Chunks created: {len(all_chunks)}")
    
    return {
        "status": "success",
        "message": "Institution documents ingested successfully",
        "files_processed": files_processed,
        "chunks_created": len(all_chunks)
    }


if __name__ == "__main__":
    result = run_institution_ingestion()
    print(f"\nResult: {result}")
