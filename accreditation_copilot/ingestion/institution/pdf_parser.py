"""
PDF Parser - Phase 4 Milestone 2
Extracts page text and tables from institutional PDFs.
Uses PyMuPDF (fitz) for text and pdfplumber for tables.
"""

import fitz  # PyMuPDF
import pdfplumber
from typing import List, Dict, Any
from pathlib import Path


class PDFParser:
    """Parse institutional PDFs to extract text and tables."""
    
    def parse(self, pdf_path: str) -> Dict[str, Any]:
        """
        Parse PDF and extract text blocks and tables.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict with pages containing text_blocks and tables
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        pages = []
        
        # Extract text using PyMuPDF
        text_doc = fitz.open(str(pdf_path))
        
        # Extract tables using pdfplumber
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_num in range(len(pdf.pages)):
                page_data = {
                    'page_number': page_num + 1,
                    'text_blocks': [],
                    'tables': []
                }
                
                # Extract text blocks from PyMuPDF
                fitz_page = text_doc[page_num]
                text = fitz_page.get_text("text")
                
                if text.strip():
                    page_data['text_blocks'].append({
                        'text': text.strip(),
                        'type': 'paragraph'
                    })
                
                # Extract tables from pdfplumber
                plumber_page = pdf.pages[page_num]
                tables = plumber_page.extract_tables()
                
                if tables:
                    for table_idx, table in enumerate(tables):
                        if table and len(table) > 0:
                            # Issue 6: Deterministic table ID format
                            # Format: {source}_p{page}_t{table_index}
                            # Example: SSR_Evidence_p45_t2
                            source_name = pdf_path.stem  # Filename without extension
                            table_id = f"{source_name}_p{page_num + 1}_t{table_idx + 1}"
                            
                            page_data['tables'].append({
                                'table_id': table_id,
                                'raw_data': table
                            })
                
                pages.append(page_data)
        
        text_doc.close()
        
        return {
            'source': pdf_path.name,
            'pages': pages
        }


# Test function
if __name__ == '__main__':
    parser = PDFParser()
    
    # Test with a sample PDF (you'll need to provide one)
    test_pdf = 'data/raw_docs/test_institution.pdf'
    
    if Path(test_pdf).exists():
        result = parser.parse(test_pdf)
        print(f"Parsed {len(result['pages'])} pages")
        
        # Show first page
        if result['pages']:
            page1 = result['pages'][0]
            print(f"\nPage 1:")
            print(f"  Text blocks: {len(page1['text_blocks'])}")
            print(f"  Tables: {len(page1['tables'])}")
            
            if page1['tables']:
                print(f"\n  First table: {page1['tables'][0]['table_id']}")
                print(f"  Rows: {len(page1['tables'][0]['raw_data'])}")
    else:
        print(f"Test PDF not found: {test_pdf}")
        print("Place a test institutional PDF at that location to test parsing")
