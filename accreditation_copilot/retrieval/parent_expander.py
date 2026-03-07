"""
Parent Expander - Phase 2.2
Hierarchical expansion of child chunks with parent context.
"""

import sqlite3
from typing import List, Dict
from pathlib import Path


class ParentExpander:
    """
    Expands child chunks with parent section context.
    """
    
    def __init__(self, db_path: str = "data/metadata.db"):
        self.db_path = Path(db_path)
    
    def _compute_parent_section_id(self, chunk: Dict) -> str:
        """
        Compute synthetic parent section ID for a chunk.
        
        Args:
            chunk: Chunk metadata dict
            
        Returns:
            Parent section ID string
        """
        framework = chunk['framework']
        source = chunk['source']
        criterion = chunk.get('criterion')
        page = chunk['page']
        
        # Strategy A: If criterion exists
        if criterion:
            # NAAC: Extract Key Indicator (e.g., 3.2.1 → 3, 7.1.6 → 7)
            # This groups all metrics under the same Key Indicator together
            if framework == 'NAAC' and '.' in criterion:
                parts = criterion.split('.')
                if len(parts) >= 1:
                    key_indicator = parts[0]
                    return f"{framework}_{source}_KI{key_indicator}"
            
            # NBA: Use full criterion as parent
            # (C5, PO1, PEO2, etc. are already section-level)
            return f"{framework}_{source}_{criterion}"
        
        # Strategy B: If criterion is NULL, group by page neighborhood
        # Group every 5 pages into one synthetic section
        page_group = page // 5
        return f"{framework}_{source}_page_{page_group}"
    
    def _fetch_section_chunks(self, framework: str, source: str) -> List[Dict]:
        """
        Fetch all chunks from the same framework and source.
        
        Args:
            framework: Framework name
            source: Source document name
            
        Returns:
            List of chunk dicts
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT chunk_id, text, page, criterion, chunk_order, source FROM chunks WHERE framework = ? AND source = ? ORDER BY page, chunk_order',
                (framework, source)
            )
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"Error fetching section chunks: {e}")
            return []
    
    def _filter_by_parent_id(self, chunks: List[Dict], parent_id: str, framework: str) -> List[Dict]:
        """
        Filter chunks that belong to the same parent section.
        
        Args:
            chunks: All chunks from source
            parent_id: Target parent section ID
            framework: Framework name
            
        Returns:
            Filtered chunks belonging to same parent
        """
        filtered = []
        
        for chunk in chunks:
            # Reconstruct parent ID for this chunk
            chunk_dict = {
                'framework': framework,
                'source': chunk.get('source', ''),
                'criterion': chunk.get('criterion'),
                'page': chunk['page']
            }
            
            chunk_parent_id = self._compute_parent_section_id(chunk_dict)
            
            if chunk_parent_id == parent_id:
                filtered.append(chunk)
        
        return filtered
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text string
            
        Returns:
            Approximate token count
        """
        return int(len(text.split()) * 1.3)
    
    def _build_parent_context(self, child_chunk: Dict, section_chunks: List[Dict], 
                              max_tokens: int = 1200) -> tuple:
        """
        Build parent context with siblings around child chunk.
        
        Args:
            child_chunk: The child chunk dict
            section_chunks: All chunks in the same section (sorted by page, chunk_order)
            max_tokens: Maximum token limit
            
        Returns:
            Tuple of (parent_context_text, num_siblings_used)
        """
        # Find child index in section
        child_id = child_chunk['chunk_id']
        child_idx = None
        
        for i, chunk in enumerate(section_chunks):
            if chunk['chunk_id'] == child_id:
                child_idx = i
                break
        
        if child_idx is None:
            # Child not found, return child text only
            return child_chunk['text'], 0
        
        # Start with child chunk
        selected_chunks = [section_chunks[child_idx]]
        context_text = child_chunk['text']
        current_tokens = self._estimate_tokens(context_text)
        
        # Expand outward incrementally: add siblings one at a time
        before_idx = child_idx - 1
        after_idx = child_idx + 1
        
        # Try to add up to 2 siblings before and 2 after, checking token limit each time
        for _ in range(2):
            # Try to add before
            if before_idx >= 0:
                candidate_text = section_chunks[before_idx]['text'] + ' ' + context_text
                candidate_tokens = self._estimate_tokens(candidate_text)
                
                if candidate_tokens <= max_tokens:
                    selected_chunks.insert(0, section_chunks[before_idx])
                    context_text = candidate_text
                    current_tokens = candidate_tokens
                    before_idx -= 1
            
            # Try to add after
            if after_idx < len(section_chunks):
                candidate_text = context_text + ' ' + section_chunks[after_idx]['text']
                candidate_tokens = self._estimate_tokens(candidate_text)
                
                if candidate_tokens <= max_tokens:
                    selected_chunks.append(section_chunks[after_idx])
                    context_text = candidate_text
                    current_tokens = candidate_tokens
                    after_idx += 1
        
        num_siblings = len(selected_chunks) - 1  # Exclude child itself
        
        return context_text, num_siblings
    
    def expand_with_parent(self, top_children: List[Dict]) -> List[Dict]:
        """
        PART 5: Expand top-5 child chunks with parent context.
        Must preserve ranking order exactly - no sorting, no deduplication, no reordering.
        
        Args:
            top_children: Top-5 reranked child chunks (in ranked order)
            
        Returns:
            Enriched results with parent_context (same order as input)
        """
        # Store input order for assertion
        input_ids = [child['chunk_id'] for child in top_children]
        
        enriched_results = []
        
        for child in top_children:
            # Compute parent section ID
            parent_id = self._compute_parent_section_id(child)
            
            # Fetch all chunks from same source
            section_chunks = self._fetch_section_chunks(
                child['framework'],
                child['source']
            )
            
            # Filter to same parent section
            parent_section_chunks = self._filter_by_parent_id(
                section_chunks,
                parent_id,
                child['framework']
            )
            
            # Build parent context
            parent_context, num_siblings = self._build_parent_context(
                child,
                parent_section_chunks,
                max_tokens=1200
            )
            
            # Create enriched result (preserve all fields including chunk_id and source_type)
            enriched = {
                'chunk_id': child.get('chunk_id'),  # Preserve chunk_id
                'framework': child['framework'],
                'doc_type': child['doc_type'],
                'source_type': child.get('source_type', 'framework'),  # FIXED: Preserve source_type
                'criterion': child.get('criterion'),
                'source': child['source'],
                'page': child['page'],
                'child_text': child['text'],
                'parent_context': parent_context,
                'scores': child['scores'],
                'metadata': {
                    'parent_section_id': parent_id,
                    'num_siblings_used': num_siblings,
                    'child_tokens': self._estimate_tokens(child['text']),
                    'parent_tokens': self._estimate_tokens(parent_context)
                }
            }
            
            enriched_results.append(enriched)
        
        # PART 5: Assert order preservation
        output_ids = [r['chunk_id'] for r in enriched_results]
        assert input_ids == output_ids, "Parent expansion must not reorder results"
        
        return enriched_results


# Test function
if __name__ == "__main__":
    expander = ParentExpander()
    
    # Test with mock child chunk
    test_child = {
        'chunk_id': 'test-123',
        'framework': 'NAAC',
        'doc_type': 'metric',
        'criterion': '3.2.1',
        'source': 'NAAC_SSR_Manual.pdf',
        'page': 65,
        'text': 'Test child chunk text.',
        'scores': {
            'dense': 0.8,
            'bm25': 0.6,
            'fused': 0.7,
            'reranker': 0.9
        }
    }
    
    results = expander.expand_with_parent([test_child])
    
    for result in results:
        print(f"Framework: {result['framework']}")
        print(f"Criterion: {result['criterion']}")
        print(f"Parent Section ID: {result['metadata']['parent_section_id']}")
        print(f"Siblings Used: {result['metadata']['num_siblings_used']}")
        print(f"Child Tokens: {result['metadata']['child_tokens']}")
        print(f"Parent Tokens: {result['metadata']['parent_tokens']}")
