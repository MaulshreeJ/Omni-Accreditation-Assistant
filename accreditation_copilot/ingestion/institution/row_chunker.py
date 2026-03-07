"""
Row Chunker - Phase 4 Milestone 2
Converts table rows and paragraphs into searchable chunks.

ARCHITECTURAL FIXES APPLIED:
- Issue 2: Chunk text normalization (concise format)
- Issue 3: Currency normalization (₹X Lakhs)
- Issue 4: Agency normalization (DST, SERB, etc.)
- Issue 5: Paragraph cleaning (newlines, spacing)
- Issue 6: Deterministic table ID
- Issue 7: Chunk length guard (max 800 tokens)
- Issue 9: Metadata alignment (page_number, source_path)
- Issue 10: Remove S.No from chunk text and structured_data
"""

import uuid
import tiktoken
import re
from typing import List, Dict, Any


class RowChunker:
    """Convert table rows and paragraphs into searchable chunks."""
    
    # Issue 4: Agency normalization map
    AGENCY_MAP = {
        "department of science and technology": "DST",
        "science and engineering research board": "SERB",
        "department of biotechnology": "DBT",
        "indian council of social science research": "ICSSR",
        "indian council of medical research": "ICMR",
        "university grants commission": "UGC",
        "all india council for technical education": "AICTE",
        "council of scientific and industrial research": "CSIR",
        "defence research and development organisation": "DRDO",
    }
    
    def __init__(self, model_name: str = 'gpt-3.5-turbo'):
        """Initialize chunker with tokenizer."""
        self.tokenizer = tiktoken.encoding_for_model(model_name)
        # Issue 2: Paragraph token guard
        self.target_tokens = 600  # Target chunk size
        self.max_tokens = 800  # Maximum allowed
        self.paragraph_overlap = 100  # Overlap tokens
    
    def _normalize_agency(self, agency: str) -> str:
        """
        Normalize agency name to standard abbreviation.
        
        Args:
            agency: Agency name
            
        Returns:
            Normalized agency name
        """
        agency_lower = agency.lower().strip()
        return self.AGENCY_MAP.get(agency_lower, agency)
    
    def _normalize_currency(self, amount: str, header: str) -> str:
        """
        Normalize currency format.
        
        Examples:
        - "24.5" with header "Amount (INR Lakhs)" → "₹24.5 Lakhs"
        - "50" with header "Funding" → "₹50 Lakhs"
        
        Args:
            amount: Amount value
            header: Column header
            
        Returns:
            Normalized currency string
        """
        # Check if header indicates currency
        if any(keyword in header.lower() for keyword in ['amount', 'funding', 'grant', 'rupees', 'inr', 'lakhs', 'crores']):
            # Extract numeric value
            numeric = re.search(r'[\d.]+', amount)
            if numeric:
                value = numeric.group()
                # Determine unit from header or default to Lakhs
                if 'crore' in header.lower():
                    return f"₹{value} Crores"
                else:
                    return f"₹{value} Lakhs"
        
        return amount
    
    def _format_chunk_text(self, headers: List[str], row: List[str]) -> str:
        """
        Format chunk text in concise, semantically meaningful format.
        
        Issue 2: New format removes S.No and uses concise field names.
        Issue 3: Currency normalization applied.
        Issue 4: Agency normalization applied.
        Issue 10: S.No removed from output.
        
        Example output:
        "Project: AI in Education Research
         Agency: DST
         Funding: ₹24.5 Lakhs
         Year: 2022-23"
        
        Args:
            headers: Column headers
            row: Row values
            
        Returns:
            Formatted chunk text
        """
        text_parts = []
        
        for header, value in zip(headers, row):
            if not value or not value.strip():
                continue
            
            # Issue 10: Skip S.No column
            if header.lower() in ['s.no', 's no', 'sno', 'serial', 'sr.no', 'sr no']:
                continue
            
            # Normalize header to concise form
            header_normalized = header
            if 'project' in header.lower() and 'title' in header.lower():
                header_normalized = 'Project'
            elif 'agency' in header.lower() or 'funding agency' in header.lower():
                header_normalized = 'Agency'
                # Issue 4: Normalize agency name
                value = self._normalize_agency(value)
            elif 'amount' in header.lower() or 'funding' in header.lower():
                header_normalized = 'Funding'
                # Issue 3: Normalize currency
                value = self._normalize_currency(value, header)
            elif 'year' in header.lower():
                header_normalized = 'Year'
            elif 'duration' in header.lower():
                header_normalized = 'Duration'
            elif 'investigator' in header.lower() or 'pi' in header.lower():
                header_normalized = 'Investigator'
            elif 'department' in header.lower():
                header_normalized = 'Department'
            
            text_parts.append(f"{header_normalized}: {value}")
        
        return "\n".join(text_parts)
    
    def _normalize_structured_data(self, headers: List[str], row: List[str]) -> Dict[str, str]:
        """
        Issue 1: Normalize structured_data fields to canonical schema.
        
        Canonical schema:
        {
            "year": "2022-23",
            "project_title": "AI in Education Research",
            "agency": "DST",
            "funding_lakhs": "24.5",
            "duration": "2 years"
        }
        
        Args:
            headers: Column headers
            row: Row values
            
        Returns:
            Normalized structured data dict
        """
        normalized = {}
        
        for header, value in zip(headers, row):
            if not value or not value.strip():
                continue
            
            # Skip S.No
            if header.lower() in ['s.no', 's no', 'sno', 'serial', 'sr.no', 'sr no']:
                continue
            
            # Normalize to canonical field names
            header_lower = header.lower()
            
            if 'year' in header_lower:
                normalized['year'] = value
            elif 'project' in header_lower and 'title' in header_lower:
                normalized['project_title'] = value
            elif 'agency' in header_lower or 'funding agency' in header_lower:
                # Apply agency normalization
                normalized['agency'] = self._normalize_agency(value)
            elif 'amount' in header_lower or 'funding' in header_lower:
                # Extract numeric value only
                import re
                numeric = re.search(r'[\d.]+', value)
                if numeric:
                    normalized['funding_lakhs'] = numeric.group()
            elif 'duration' in header_lower:
                normalized['duration'] = value
            elif 'investigator' in header_lower or 'pi' in header_lower:
                normalized['investigator'] = value
            elif 'department' in header_lower:
                normalized['department'] = value
            # Add other common fields as needed
            elif 'title' in header_lower and 'project' not in header_lower:
                normalized['title'] = value
            elif 'name' in header_lower:
                normalized['name'] = value
        
        return normalized
    
    def chunk_table_row(self, row: List[str], headers: List[str], 
                        table_id: str, row_idx: int, page_number: int,
                        source_path: str) -> Dict[str, Any]:
        """
        Convert a table row into a searchable chunk.
        
        Args:
            row: Table row data
            headers: Column headers
            table_id: Table identifier (deterministic format)
            row_idx: Row index
            page_number: Page number
            source_path: Source PDF path
            
        Returns:
            Chunk dict with text and structured data
        """
        # Issue 2: Format chunk text in concise format
        text = self._format_chunk_text(headers, row)
        
        # Issue 1: Normalize structured_data to canonical schema
        structured_data = self._normalize_structured_data(headers, row)
        
        # Issue 5: Add evidence type and weight
        evidence_type = 'table_row'
        evidence_weight = 1.2
        
        # Issue 9: Metadata alignment (page_number, source_path)
        return {
            'chunk_id': str(uuid.uuid4()),
            'text': text,
            'structured_data': structured_data,
            'chunk_type': 'table_row',
            'source_type': 'institution',
            'doc_type': 'institutional',
            'evidence_type': evidence_type,  # Issue 5
            'evidence_weight': evidence_weight,  # Issue 5
            'table_id': table_id,
            'row_id': row_idx,
            'page_number': page_number,  # Issue 9: Changed from 'page'
            'source_path': source_path,  # Issue 9: Changed from 'source'
            'framework': None,  # Issue 1: Will be inferred by criterion_inferrer
            'criterion': None   # Issue 1: Will be inferred by criterion_inferrer
        }
    
    def chunk_table(self, table: Dict[str, Any], page_number: int, 
                    source_path: str) -> List[Dict[str, Any]]:
        """
        Convert all rows in a table into chunks.
        
        Args:
            table: Structured table
            page_number: Page number
            source_path: Source PDF path
            
        Returns:
            List of row chunks
        """
        chunks = []
        
        for row_idx, row in enumerate(table['rows']):
            chunk = self.chunk_table_row(
                row,
                table['headers'],
                table['table_id'],
                row_idx,
                page_number,
                source_path
            )
            chunks.append(chunk)
        
        return chunks
    
    def chunk_paragraph(self, text: str, page_number: int, 
                        source_path: str) -> List[Dict[str, Any]]:
        """
        Convert paragraph text into chunks with overlap.
        
        Issue 2: Paragraph token guard (target 600, max 800).
        Issue 5: Add evidence type and weight.
        
        Args:
            text: Paragraph text
            page_number: Page number
            source_path: Source PDF path
            
        Returns:
            List of paragraph chunks
        """
        # Issue 5: Paragraph cleaning
        # Replace newlines with spaces
        text = text.replace('\n', ' ')
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        
        # Skip if text is too short after cleaning
        if len(text) < 50:
            return []
        
        # Tokenize
        tokens = self.tokenizer.encode(text)
        
        chunks = []
        start = 0
        
        # Issue 2: Token guard - ensure chunks don't exceed max_tokens
        while start < len(tokens):
            # Get chunk tokens (target size, but respect max)
            end = min(start + self.target_tokens, len(tokens))
            
            # Issue 2: If chunk would exceed max_tokens, split it
            if end - start > self.max_tokens:
                end = start + self.max_tokens
            
            chunk_tokens = tokens[start:end]
            
            # Decode back to text
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            # Issue 5: Add evidence type and weight for paragraphs
            evidence_type = 'paragraph'
            evidence_weight = 1.0
            
            # Issue 9: Metadata alignment
            chunks.append({
                'chunk_id': str(uuid.uuid4()),
                'text': chunk_text,
                'structured_data': {},  # Paragraphs don't have structured data
                'chunk_type': 'paragraph',
                'source_type': 'institution',
                'doc_type': 'institutional',
                'evidence_type': evidence_type,  # Issue 5
                'evidence_weight': evidence_weight,  # Issue 5
                'page_number': page_number,  # Issue 9: Changed from 'page'
                'source_path': source_path,  # Issue 9: Changed from 'source'
                'framework': None,  # Issue 1: Will be inferred
                'criterion': None   # Issue 1: Will be inferred
            })
            
            # Move to next chunk with overlap
            start += self.target_tokens - self.paragraph_overlap
        
        return chunks
    
    def chunk_document(self, parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert entire parsed document into chunks.
        
        Args:
            parsed_doc: Parsed document from PDFParser
            
        Returns:
            List of all chunks (table rows + paragraphs)
        """
        from .table_extractor import TableExtractor
        
        extractor = TableExtractor()
        all_chunks = []
        source_path = parsed_doc['source']
        
        for page in parsed_doc['pages']:
            page_number = page['page_number']
            
            # Extract and chunk tables
            structured_tables = extractor.extract_all(page)
            
            for table in structured_tables:
                table_chunks = self.chunk_table(table, page_number, source_path)
                all_chunks.extend(table_chunks)
            
            # Chunk paragraphs
            for text_block in page.get('text_blocks', []):
                text = text_block['text']
                
                paragraph_chunks = self.chunk_paragraph(text, page_number, source_path)
                all_chunks.extend(paragraph_chunks)
        
        return all_chunks


# Test function
if __name__ == '__main__':
    chunker = RowChunker()
    
    # Test table row chunking with new format
    headers = ['S.No', 'Year', 'Project Title', 'Funding Agency', 'Amount (INR Lakhs)']
    row = ['1', '2022-23', 'AI in Education Research', 'Department of Science and Technology', '24.5']
    
    chunk = chunker.chunk_table_row(row, headers, 'SSR_Evidence_p45_t2', 0, 45, 'SSR_Evidence.pdf')
    
    print("Table Row Chunk (New Format):")
    print(f"  Chunk ID: {chunk['chunk_id']}")
    print(f"  Text:\n{chunk['text']}")
    print(f"  Type: {chunk['chunk_type']}")
    print(f"  Source Type: {chunk['source_type']}")
    print(f"  Structured Data: {chunk['structured_data']}")
    print(f"  Page Number: {chunk['page_number']}")
    print(f"  Source Path: {chunk['source_path']}")
    
    # Test paragraph chunking with cleaning
    long_text = "This is a test\nparagraph with\n\n  multiple   spaces.\nIt should be cleaned."
    para_chunks = chunker.chunk_paragraph(long_text, 1, 'test.pdf')
    
    print(f"\nParagraph Chunks: {len(para_chunks)}")
    if para_chunks:
        print(f"  Cleaned text: {para_chunks[0]['text']}")

