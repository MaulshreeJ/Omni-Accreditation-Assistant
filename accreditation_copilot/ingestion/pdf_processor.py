"""
PDF Processor - Phase 1
Extracts text from PDF documents page by page with metadata.
"""

import pymupdf
import re
from typing import List, Dict
from pathlib import Path


class PDFProcessor:
    """
    Processes PDF documents and extracts text page by page.
    Preserves page numbers and normalizes whitespace.
    """
    
    def __init__(self):
        self.header_patterns = [
            r'^Page \d+',
            r'^\d+\s*$',
            r'^NAAC.*?Manual',
            r'^NBA.*?Manual',
        ]
        self.footer_patterns = [
            r'Page \d+ of \d+',
            r'^\d+\s*$',
        ]
    
    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extract text from PDF page by page.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dicts with page, text, and source
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        pages = []
        
        try:
            doc = pymupdf.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Clean text
                text = self._clean_text(text)
                
                if text.strip():  # Only add non-empty pages
                    pages.append({
                        "page": page_num + 1,  # 1-indexed
                        "text": text,
                        "source": pdf_path.name
                    })
            
            doc.close()
            
        except Exception as e:
            raise Exception(f"Error processing {pdf_path}: {e}")
        
        return pages
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        # Remove headers/footers
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip headers
            if any(re.match(pattern, line, re.IGNORECASE) for pattern in self.header_patterns):
                continue
            
            # Skip footers
            if any(re.match(pattern, line, re.IGNORECASE) for pattern in self.footer_patterns):
                continue
            
            cleaned_lines.append(line)
        
        # Join lines
        text = '\n'.join(cleaned_lines)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def process_directory(self, directory: str, framework: str = None) -> List[Dict]:
        """
        Process all PDFs in a directory.
        
        Args:
            directory: Path to directory containing PDFs
            framework: Optional framework filter (naac/nba)
            
        Returns:
            List of all pages from all PDFs
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        all_pages = []
        pdf_files = list(directory.glob("*.pdf"))
        
        if not pdf_files:
            print(f"Warning: No PDF files found in {directory}")
            return all_pages
        
        for pdf_file in pdf_files:
            # Filter by framework if specified
            if framework:
                if framework.lower() not in pdf_file.name.lower():
                    continue
            
            print(f"Processing: {pdf_file.name}")
            pages = self.process_pdf(str(pdf_file))
            all_pages.extend(pages)
            print(f"  Extracted {len(pages)} pages")
        
        return all_pages


# Test function
if __name__ == "__main__":
    processor = PDFProcessor()
    
    # Test with sample PDF
    test_dir = Path("../data/raw_docs/naac")
    if test_dir.exists():
        pages = processor.process_directory(str(test_dir))
        print(f"\nTotal pages extracted: {len(pages)}")
        
        if pages:
            print(f"\nSample page:")
            print(f"Page: {pages[0]['page']}")
            print(f"Source: {pages[0]['source']}")
            print(f"Text preview: {pages[0]['text'][:200]}...")
