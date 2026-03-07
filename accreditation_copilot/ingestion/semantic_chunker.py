"""
Semantic Chunker - Phase 1.4 Final Fix
Robust metric boundary enforcement.

CRITICAL RULE: Every metric header (X.Y.Z QnM) creates a hard boundary.
No chunk labeled X.Y.Z may contain another metric header.
"""

import re
import uuid
from typing import List, Dict, Tuple
from transformers import AutoTokenizer


# Robust metric header detection - handles PDF line noise
# Matches X.Y.Z QnM anywhere in text, with optional "Weightage" prefix
NAAC_METRIC_HEADER_PATTERN = re.compile(
    r'([1-7]\.\d{1,2}\.\d{1,2})\s+QnM\b'
)

NAAC_WEIGHTAGE_PATTERN = re.compile(
    r'Weightage\s+([1-7]\.\d{1,2}\.\d{1,2})\s+QnM\b'
)

NAAC_KI_PATTERN = re.compile(
    r'Key\s+Indicator\s*[-–]\s*([1-7]\.\d{1,2})\b'
)

# NBA Header Patterns
NBA_CRITERION_PATTERN = re.compile(
    r'Criterion\s+(\d+)\s*:'
)

NBA_SHORT_CODE_PATTERN = re.compile(
    r'\bC(\d+)\b'
)


def find_criterion_boundaries(text: str, framework: str) -> List[Tuple[int, str]]:
    """
    Find all metric-level criterion boundaries in text.
    
    CRITICAL: Only X.Y.Z QnM headers create boundaries for NAAC.
    Only C# headers create boundaries for NBA.
    No normalization, no inference - direct match only.
    
    Returns:
        List of (position, criterion_id) tuples, sorted by position
    """
    boundaries = []
    seen_positions = []
    
    if framework == "NAAC":
        # Detect all metric-level headers (X.Y.Z QnM)
        for match in NAAC_METRIC_HEADER_PATTERN.finditer(text):
            pos = match.start()
            raw_id = match.group(1)
            
            # Deduplicate only extremely close matches (within 10 chars)
            if any(abs(pos - p) < 10 for p in seen_positions):
                continue
            
            # Validate format: must be X.Y.Z
            if not re.match(r'^[1-7]\.\d{1,2}\.\d{1,2}$', raw_id):
                continue
            
            boundaries.append((pos, raw_id))
            seen_positions.append(pos)
    
    elif framework == "NBA":
        # Detect "Criterion #:" headers
        for match in NBA_CRITERION_PATTERN.finditer(text):
            pos = match.start()
            criterion_num = match.group(1)
            criterion = f"C{criterion_num}"
            
            # Validate: only C1-C10 are valid NBA criteria
            if not (1 <= int(criterion_num) <= 10):
                continue
            
            # Deduplicate only extremely close matches (within 10 chars)
            if any(abs(pos - p) < 10 for p in seen_positions):
                continue
            
            boundaries.append((pos, criterion))
            seen_positions.append(pos)
        
        # Detect "C#" short code (word boundary)
        # Only if not already detected by Criterion pattern
        for match in NBA_SHORT_CODE_PATTERN.finditer(text):
            pos = match.start()
            criterion_num = match.group(1)
            criterion = f"C{criterion_num}"
            
            # Validate: only C1-C10 are valid NBA criteria
            if not (1 <= int(criterion_num) <= 10):
                continue
            
            # Deduplicate only extremely close matches (within 10 chars)
            if any(abs(pos - p) < 10 for p in seen_positions):
                continue
            
            boundaries.append((pos, criterion))
            seen_positions.append(pos)
    
    # Sort by position
    boundaries.sort(key=lambda x: x[0])
    return boundaries


def split_into_criterion_sections(text: str, framework: str) -> List[Dict]:
    """
    Split document into criterion sections.
    Each section has a single criterion label.
    
    Returns:
        List of section dicts with criterion, text, start_pos, end_pos
    """
    boundaries = find_criterion_boundaries(text, framework)
    
    if not boundaries:
        # No boundaries found - return entire text as unlabeled section
        return [{
            "criterion": None,
            "text": text,
            "start_pos": 0,
            "end_pos": len(text)
        }]
    
    sections = []
    
    # Preamble (text before first boundary)
    if boundaries[0][0] > 0:
        preamble = text[:boundaries[0][0]].strip()
        if len(preamble) > 100:
            sections.append({
                "criterion": None,
                "text": preamble,
                "start_pos": 0,
                "end_pos": boundaries[0][0]
            })
    
    # Process each boundary
    for i, (pos, criterion_id) in enumerate(boundaries):
        end_pos = boundaries[i+1][0] if i+1 < len(boundaries) else len(text)
        section_text = text[pos:end_pos].strip()
        
        # Skip very short sections
        if len(section_text) < 50:
            continue
        
        sections.append({
            "criterion": criterion_id,
            "text": section_text,
            "start_pos": pos,
            "end_pos": end_pos
        })
    
    return sections


def determine_page(position: int, page_positions: List[Tuple[int, int]]) -> int:
    """
    Determine which page a text position belongs to.
    
    Args:
        position: Character position in full text
        page_positions: List of (start_pos, page_num) tuples
        
    Returns:
        Page number
    """
    for i, (start_pos, page_num) in enumerate(page_positions):
        if i + 1 < len(page_positions):
            next_start = page_positions[i + 1][0]
            if start_pos <= position < next_start:
                return page_num
        else:
            # Last page
            if position >= start_pos:
                return page_num
    
    # Default to first page if not found
    return page_positions[0][1] if page_positions else 1


class SemanticChunker:
    """
    Structure-aware chunker that respects criterion boundaries.
    
    CRITICAL GUARANTEE: No chunk crosses criterion boundaries.
    """
    
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 50):
        """
        Initialize semantic chunker.
        
        Args:
            chunk_size: Target chunk size in characters (default 600)
            chunk_overlap: Overlap between chunks in characters (default 50)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Use BGE tokenizer for token counting
        print("Loading BGE tokenizer for chunking...")
        self.tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-base-en-v1.5")
        print("BGE tokenizer loaded successfully")
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens using BGE tokenizer."""
        return len(self.tokenizer.encode(text, add_special_tokens=False))
    
    def _split_text_simple(self, text: str) -> List[str]:
        """
        Simple text splitter that respects chunk_size and chunk_overlap.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If not at end, try to break at sentence boundary
            if end < len(text):
                # Look for sentence end in last 100 chars
                search_start = max(start, end - 100)
                last_period = text.rfind('.', search_start, end)
                last_newline = text.rfind('\n', search_start, end)
                
                break_point = max(last_period, last_newline)
                if break_point > start:
                    end = break_point + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start forward with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def chunk_pages(self, pages: List[Dict], framework: str) -> List[Dict]:
        """
        Chunk pages with structure-aware boundary respect.
        
        Args:
            pages: List of page dicts from PDF processor
            framework: 'NAAC' or 'NBA'
            
        Returns:
            List of chunk dicts with metadata
        """
        # Concatenate all pages with page markers
        full_text = ""
        page_positions = []
        
        for page_data in pages:
            page_positions.append((len(full_text), page_data['page']))
            full_text += f"\n\n[PAGE_{page_data['page']}]\n" + page_data['text']
        
        source = pages[0]['source'] if pages else "unknown"
        
        # Split into criterion sections
        sections = split_into_criterion_sections(full_text, framework)
        
        # Chunk within each section
        chunks = []
        chunk_order = 0
        
        for section in sections:
            criterion = section["criterion"]
            section_text = section["text"]
            section_start = section["start_pos"]
            
            # Split section into chunks
            sub_chunks = self._split_text_simple(section_text)
            
            for chunk_text in sub_chunks:
                if len(chunk_text.strip()) < 50:
                    continue
                
                # Determine page number
                chunk_pos_in_full_text = section_start + section_text.find(chunk_text[:50])
                page_num = determine_page(chunk_pos_in_full_text, page_positions)
                
                # Detect document type
                doc_type = self._detect_doc_type(source, framework)
                
                # Create chunk
                chunk_id = str(uuid.uuid4())
                chunk = {
                    'chunk_id': chunk_id,
                    'text': chunk_text.strip(),
                    'page': page_num,
                    'source': source,
                    'framework': framework,
                    'doc_type': doc_type,
                    'criterion': criterion,
                    'tier': 'general',
                    'stage': 'general',
                    'chunk_order': chunk_order
                }
                
                chunks.append(chunk)
                chunk_order += 1
        
        return chunks
    
    def _detect_doc_type(self, filename: str, framework: str) -> str:
        """Detect document type from filename."""
        filename_lower = filename.lower()
        
        if framework == 'NAAC':
            # Metric documents
            if any(keyword in filename_lower for keyword in ['ssr', 'manual', 'quality indicator', 'qif', 'sss']):
                return 'metric'
            # Policy documents
            if any(keyword in filename_lower for keyword in ['raf', 'dvv', 'sop']):
                return 'policy'
            return 'policy'
        
        elif framework == 'NBA':
            # Prequalifier documents
            if 'prequalifier' in filename_lower or 'pro_forma' in filename_lower:
                return 'prequalifier'
            # Metric documents
            if any(keyword in filename_lower for keyword in ['sar', 'evaluation_guidelines', 'accreditation_manual']):
                return 'metric'
            # Policy documents
            if 'general_accreditation_manual' in filename_lower or 'general' in filename_lower:
                return 'policy'
            return 'metric'
        
        return 'general'


def validate_no_cross_metric_contamination(db_path: str) -> bool:
    """
    Validate that no chunk contains metric headers other than its own label.
    
    CRITICAL VALIDATION: This must pass before proceeding to Phase 2.
    
    Args:
        db_path: Path to metadata.db
        
    Returns:
        True if validation passes, False otherwise
    """
    import sqlite3
    
    conn = sqlite3.connect(db_path)
    
    cursor = conn.execute("""
        SELECT chunk_id, criterion, text
        FROM chunks
        WHERE framework='NAAC'
        AND criterion IS NOT NULL
    """)
    
    violations = []
    
    for chunk_id, criterion, text in cursor.fetchall():
        # Find all metric headers in chunk text
        headers = re.findall(
            r'([1-7]\.\d{1,2}\.\d{1,2})\s+QnM',
            text
        )
        
        unique_headers = set(headers)
        
        # Check if any header differs from chunk's label
        for h in unique_headers:
            if h != criterion:
                violations.append((chunk_id, criterion, h))
    
    conn.close()
    
    if violations:
        print("CROSS-METRIC CONTAMINATION DETECTED:")
        for chunk_id, labeled, found in violations:
            print(f"  Chunk {chunk_id[:8]}... labeled '{labeled}' contains header '{found}'")
        return False
    
    print("[PASS] Zero cross-metric contamination")
    return True


# Test function
if __name__ == "__main__":
    chunker = SemanticChunker()
    
    # Test with sample pages
    sample_pages = [
        {
            "page": 1,
            "text": "Criterion I: Curricular Aspects\n\n1.1.1 The Institution ensures effective curriculum delivery through a well-planned and documented process.",
            "source": "NAAC_RAF.pdf"
        }
    ]
    
    chunks = chunker.chunk_pages(sample_pages, 'NAAC')
    print(f"Generated {len(chunks)} chunks")
    
    if chunks:
        print(f"\nSample chunk:")
        print(chunks[0])
