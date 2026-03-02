"""
Semantic Chunker - Phase 1.1
Structure-aware chunking for NAAC and NBA documents.
Token-based chunking with BGE tokenizer for proper granularity.
"""

import re
import uuid
from typing import List, Dict
from transformers import AutoTokenizer


class SemanticChunker:
    """
    Performs semantic, structure-aware chunking for NAAC and NBA documents.
    Maintains chunk coherence and attaches rich metadata.
    
    Phase 1.1 Changes:
    - Token-based chunking using BGE tokenizer
    - Smaller chunks (300 tokens target, 400 hard cap, 450 absolute max)
    - Enables meaningful parent-child expansion
    """
    
    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 50):
        """
        Initialize semantic chunker with token-based parameters.
        
        Args:
            chunk_size: Target chunk size in tokens (default 300)
            chunk_overlap: Overlap between chunks in tokens (default 50)
        """
        self.chunk_size = chunk_size  # Target: 300 tokens
        self.chunk_overlap = chunk_overlap  # Overlap: 50 tokens
        self.hard_cap = 400  # Hard cap at 400 tokens
        self.absolute_max = 450  # Never exceed 450 tokens
        
        # Use BGE tokenizer for accurate token counting
        print("Loading BGE tokenizer for chunking...")
        self.tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-base-en-v1.5")
        print("BGE tokenizer loaded successfully")
        
        # NAAC patterns - improved metric extraction
        self.naac_metric_pattern = r'\b(\d\.\d\.\d)\b'
        
        # NBA patterns - improved criterion extraction
        self.nba_po_pattern = r'\b(PO\d+)\b'
        self.nba_peo_pattern = r'\b(PEO\d+)\b'
        self.nba_criterion_pattern = r'\bCriterion\s+(\d+)\b'
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens using BGE tokenizer.
        
        Args:
            text: Text to tokenize
            
        Returns:
            Number of tokens
        """
        return len(self.tokenizer.encode(text, add_special_tokens=False))
    
    def chunk_pages(self, pages: List[Dict], framework: str) -> List[Dict]:
        """
        Chunk pages based on framework-specific structure.
        
        Args:
            pages: List of page dicts from PDF processor
            framework: 'NAAC' or 'NBA'
            
        Returns:
            List of chunk dicts with metadata
        """
        if framework.upper() == 'NAAC':
            return self._chunk_naac(pages)
        elif framework.upper() == 'NBA':
            return self._chunk_nba(pages)
        else:
            raise ValueError(f"Unknown framework: {framework}")
    
    def _chunk_naac(self, pages: List[Dict]) -> List[Dict]:
        """
        Chunk NAAC documents with token-based granularity.
        Target: 300 tokens, Hard cap: 400, Absolute max: 450
        """
        chunks = []
        current_chunk = []
        current_criterion = None
        current_tokens = 0
        chunk_order = 0
        
        for page_data in pages:
            text = page_data['text']
            page_num = page_data['page']
            source = page_data['source']
            
            # Detect document type
            doc_type = self._detect_naac_doc_type(source)
            
            # Split by sentences for finer granularity
            sentences = self._split_sentences(text)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Extract metric ID (e.g., 1.1.1, 2.3.4)
                metric_matches = re.findall(self.naac_metric_pattern, sentence)
                if metric_matches:
                    current_criterion = metric_matches[0]
                
                sentence_tokens = self._count_tokens(sentence)
                
                # Check if adding this sentence would exceed hard cap
                if current_tokens + sentence_tokens > self.hard_cap and current_chunk:
                    # Save current chunk
                    chunk_text = ' '.join(current_chunk)
                    chunk_tokens = self._count_tokens(chunk_text)
                    
                    # Enforce absolute max
                    if chunk_tokens > self.absolute_max:
                        # Trim to absolute max
                        chunk_text = self._trim_to_token_limit(chunk_text, self.absolute_max)
                    
                    chunks.append(self._create_chunk(
                        chunk_text, page_num, source, 'NAAC', doc_type, 
                        {'criterion': current_criterion}, chunk_order
                    ))
                    chunk_order += 1
                    
                    # Start new chunk with overlap
                    if self.chunk_overlap > 0 and len(current_chunk) > 0:
                        # Keep last few sentences for overlap
                        overlap_text = ' '.join(current_chunk[-2:])  # Last 2 sentences
                        overlap_tokens = self._count_tokens(overlap_text)
                        if overlap_tokens <= self.chunk_overlap:
                            current_chunk = current_chunk[-2:]
                            current_tokens = overlap_tokens
                        else:
                            current_chunk = []
                            current_tokens = 0
                    else:
                        current_chunk = []
                        current_tokens = 0
                
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
                
                # Also create chunk if we hit target size and have a good break point
                if current_tokens >= self.chunk_size and metric_matches:
                    chunk_text = ' '.join(current_chunk)
                    chunk_tokens = self._count_tokens(chunk_text)
                    
                    if chunk_tokens > self.absolute_max:
                        chunk_text = self._trim_to_token_limit(chunk_text, self.absolute_max)
                    
                    chunks.append(self._create_chunk(
                        chunk_text, page_num, source, 'NAAC', doc_type,
                        {'criterion': current_criterion}, chunk_order
                    ))
                    chunk_order += 1
                    
                    # Start new chunk with overlap
                    if self.chunk_overlap > 0 and len(current_chunk) > 0:
                        overlap_text = ' '.join(current_chunk[-2:])
                        overlap_tokens = self._count_tokens(overlap_text)
                        if overlap_tokens <= self.chunk_overlap:
                            current_chunk = current_chunk[-2:]
                            current_tokens = overlap_tokens
                        else:
                            current_chunk = []
                            current_tokens = 0
                    else:
                        current_chunk = []
                        current_tokens = 0
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_tokens = self._count_tokens(chunk_text)
            
            if chunk_tokens > self.absolute_max:
                chunk_text = self._trim_to_token_limit(chunk_text, self.absolute_max)
            
            chunks.append(self._create_chunk(
                chunk_text, page_num, source, 'NAAC', doc_type,
                {'criterion': current_criterion}, chunk_order
            ))
        
        return chunks
    
    def _chunk_nba(self, pages: List[Dict]) -> List[Dict]:
        """
        Chunk NBA documents with token-based granularity.
        Target: 300 tokens, Hard cap: 400, Absolute max: 450
        """
        chunks = []
        current_chunk = []
        current_criterion = None
        current_tokens = 0
        chunk_order = 0
        
        for page_data in pages:
            text = page_data['text']
            page_num = page_data['page']
            source = page_data['source']
            
            # Detect document type and tier
            doc_type = self._detect_nba_doc_type(source)
            tier = self._detect_nba_tier(source)
            
            # Split by sentences for finer granularity
            sentences = self._split_sentences(text)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Extract criterion - prioritize PO/PEO, then Criterion number
                po_matches = re.findall(self.nba_po_pattern, sentence)
                peo_matches = re.findall(self.nba_peo_pattern, sentence)
                criterion_matches = re.findall(self.nba_criterion_pattern, sentence)
                
                # Priority: PO > PEO > Criterion
                if po_matches:
                    current_criterion = po_matches[0]
                elif peo_matches:
                    current_criterion = peo_matches[0]
                elif criterion_matches:
                    current_criterion = f"C{criterion_matches[0]}"
                
                sentence_tokens = self._count_tokens(sentence)
                
                # Check if adding this sentence would exceed hard cap
                if current_tokens + sentence_tokens > self.hard_cap and current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    chunk_tokens = self._count_tokens(chunk_text)
                    
                    if chunk_tokens > self.absolute_max:
                        chunk_text = self._trim_to_token_limit(chunk_text, self.absolute_max)
                    
                    chunks.append(self._create_chunk(
                        chunk_text, page_num, source, 'NBA', doc_type,
                        {'criterion': current_criterion, 'tier': tier}, chunk_order
                    ))
                    chunk_order += 1
                    
                    # Start new chunk with overlap
                    if self.chunk_overlap > 0 and len(current_chunk) > 0:
                        overlap_text = ' '.join(current_chunk[-2:])
                        overlap_tokens = self._count_tokens(overlap_text)
                        if overlap_tokens <= self.chunk_overlap:
                            current_chunk = current_chunk[-2:]
                            current_tokens = overlap_tokens
                        else:
                            current_chunk = []
                            current_tokens = 0
                    else:
                        current_chunk = []
                        current_tokens = 0
                
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
                
                # Create chunk at good break points
                if current_tokens >= self.chunk_size and (po_matches or peo_matches or criterion_matches):
                    chunk_text = ' '.join(current_chunk)
                    chunk_tokens = self._count_tokens(chunk_text)
                    
                    if chunk_tokens > self.absolute_max:
                        chunk_text = self._trim_to_token_limit(chunk_text, self.absolute_max)
                    
                    chunks.append(self._create_chunk(
                        chunk_text, page_num, source, 'NBA', doc_type,
                        {'criterion': current_criterion, 'tier': tier}, chunk_order
                    ))
                    chunk_order += 1
                    
                    # Start new chunk with overlap
                    if self.chunk_overlap > 0 and len(current_chunk) > 0:
                        overlap_text = ' '.join(current_chunk[-2:])
                        overlap_tokens = self._count_tokens(overlap_text)
                        if overlap_tokens <= self.chunk_overlap:
                            current_chunk = current_chunk[-2:]
                            current_tokens = overlap_tokens
                        else:
                            current_chunk = []
                            current_tokens = 0
                    else:
                        current_chunk = []
                        current_tokens = 0
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_tokens = self._count_tokens(chunk_text)
            
            if chunk_tokens > self.absolute_max:
                chunk_text = self._trim_to_token_limit(chunk_text, self.absolute_max)
            
            chunks.append(self._create_chunk(
                chunk_text, page_num, source, 'NBA', doc_type,
                {'criterion': current_criterion, 'tier': tier}, chunk_order
            ))
        
        return chunks
    
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences while preserving structure.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting on common delimiters
        # Preserve paragraph breaks
        sentences = []
        for para in text.split('\n\n'):
            # Split on sentence boundaries
            para_sentences = re.split(r'(?<=[.!?])\s+', para)
            sentences.extend(para_sentences)
        
        return [s.strip() for s in sentences if s.strip()]
    
    def _trim_to_token_limit(self, text: str, max_tokens: int) -> str:
        """
        Trim text to fit within token limit.
        
        Args:
            text: Text to trim
            max_tokens: Maximum number of tokens
            
        Returns:
            Trimmed text
        """
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        if len(tokens) <= max_tokens:
            return text
        
        # Trim tokens and decode
        trimmed_tokens = tokens[:max_tokens]
        return self.tokenizer.decode(trimmed_tokens)
    
    def _create_chunk(self, text: str, page: int, source: str, 
                     framework: str, doc_type: str, metadata: Dict, 
                     chunk_order: int = 0) -> Dict:
        """Create a chunk dict with metadata."""
        chunk_id = str(uuid.uuid4())
        
        chunk = {
            'chunk_id': chunk_id,
            'text': text,
            'page': page,
            'source': source,
            'framework': framework,
            'doc_type': doc_type,
            'criterion': metadata.get('criterion'),
            'tier': metadata.get('tier', 'general'),
            'stage': 'general',
            'chunk_order': chunk_order
        }
        
        return chunk
    
    def _detect_naac_doc_type(self, filename: str) -> str:
        """Detect NAAC document type from filename."""
        filename_lower = filename.lower()
        
        # Metric documents
        if any(keyword in filename_lower for keyword in ['ssr', 'manual', 'quality indicator', 'qif', 'sss']):
            return 'metric'
        
        # Policy documents
        if any(keyword in filename_lower for keyword in ['raf', 'dvv', 'sop']):
            return 'policy'
        
        # Default to policy
        return 'policy'
    
    def _detect_nba_doc_type(self, filename: str) -> str:
        """Detect NBA document type from filename."""
        filename_lower = filename.lower()
        
        # Prequalifier documents
        if 'prequalifier' in filename_lower or 'pro_forma' in filename_lower:
            return 'prequalifier'
        
        # Metric documents (includes SAR)
        if any(keyword in filename_lower for keyword in ['sar', 'evaluation_guidelines', 'accreditation_manual']):
            return 'metric'
        
        # Policy documents
        if 'general_accreditation_manual' in filename_lower or 'general' in filename_lower:
            return 'policy'
        
        # Default to metric
        return 'metric'
    
    def _detect_nba_tier(self, filename: str) -> str:
        """Detect NBA tier from filename."""
        filename_lower = filename.lower()
        
        if 'tier' in filename_lower:
            if 'tier-ii' in filename_lower or 'tier 2' in filename_lower:
                return 'tier2'
            else:
                return 'tier1'
        elif 'general' in filename_lower:
            return 'general'
        else:
            return 'general'


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
