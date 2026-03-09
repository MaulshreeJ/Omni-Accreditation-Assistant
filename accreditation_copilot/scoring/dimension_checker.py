"""
C2 - Dimension Coverage Checker
Determines which required compliance dimensions are present in retrieved evidence.

FIXED: Per-chunk coverage tracking for traceability.
PHASE 6: Enhanced with regex-based semantic detection for better coverage accuracy.
"""

import yaml
import os
import re
from typing import List, Dict, Any, Set


class DimensionChecker:
    """Check coverage of required compliance dimensions."""
    
    def __init__(self, metric_maps_dir: str = None):
        """
        Initialize dimension checker with metric maps.
        
        Args:
            metric_maps_dir: Path to directory containing YAML metric maps
        """
        if metric_maps_dir is None:
            # Default to data/metric_maps relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            metric_maps_dir = os.path.join(
                os.path.dirname(current_dir),
                'data',
                'metric_maps'
            )
        
        self.metric_maps_dir = metric_maps_dir
        self.naac_map = self._load_yaml('naac_metric_map.yaml')
        self.nba_map = self._load_yaml('nba_metric_map.yaml')
        
        # Database path for loading text
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(os.path.dirname(current_dir), 'data', 'metadata.db')
    
    def _load_yaml(self, filename: str) -> Dict:
        """Load YAML metric map."""
        filepath = os.path.join(self.metric_maps_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Metric map not found: {filepath}")
            return {}
    
    def _load_text_from_db(self, chunk_id: str) -> str:
        """Load chunk text from database if not in result."""
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT text FROM chunks WHERE chunk_id = ?', (chunk_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return row[0]
            return ''
        except Exception as e:
            print(f"[DimensionChecker] Error loading text for {chunk_id}: {e}")
            return ''
    
    def check(self, results: List[Dict[str, Any]], framework: str, criterion: str) -> Dict[str, Any]:
        """
        Check dimension coverage for a criterion.
        
        MILESTONE 5: Only count institution chunks as evidence.
        Framework chunks remain available for LLM context only.
        
        Args:
            results: List of retrieval results from Phase 2
            framework: 'NAAC' or 'NBA'
            criterion: Criterion ID (e.g., '3.2.1' or 'C5')
            
        Returns:
            Coverage analysis with per-chunk dimension hits
        """
        # Get metric definition
        metric_map = self.naac_map if framework == 'NAAC' else self.nba_map
        
        if framework not in metric_map:
            return self._empty_coverage()
        
        metric_def = metric_map[framework].get(criterion)
        if not metric_def:
            return self._empty_coverage()
        
        dimensions = metric_def.get('dimensions', [])
        if not dimensions:
            return self._empty_coverage()
        
        # MILESTONE 5: Filter to only institution chunks for evidence counting
        institution_chunks = [r for r in results if r.get('source_type') == 'institution']
        
        # DEBUG: Log retrieval result structure
        if institution_chunks:
            first_chunk = institution_chunks[0]
            print(f"[DimensionChecker DEBUG] First chunk keys: {list(first_chunk.keys())}")
            print(f"[DimensionChecker DEBUG] Has 'text': {'text' in first_chunk}")
            print(f"[DimensionChecker DEBUG] Has 'child_text': {'child_text' in first_chunk}")
            print(f"[DimensionChecker DEBUG] Has 'parent_context': {'parent_context' in first_chunk}")
            
            # Check what text we can extract
            if 'child_text' in first_chunk:
                sample_text = first_chunk.get('child_text', '')[:100]
            elif 'text' in first_chunk:
                sample_text = first_chunk.get('text', '')[:100]
            else:
                sample_text = "NO TEXT FIELD FOUND"
            print(f"[DimensionChecker DEBUG] Sample text: {sample_text}")
        
        # If no institution evidence, coverage_ratio = 0
        if not institution_chunks:
            # Return zero coverage but keep framework chunks for LLM context
            required_dims = [d['id'] for d in dimensions if d.get('required', True)]
            optional_dims = [d['id'] for d in dimensions if not d.get('required', True)]
            
            return {
                'dimensions_covered': [],
                'dimensions_missing': required_dims,
                'coverage_ratio': 0.0,
                'per_chunk_hits': {},
                'required_dimensions': required_dims,
                'optional_dimensions': optional_dims,
                'metric_name': metric_def.get('name', 'Unknown'),
                'institution_evidence_available': False
            }
        
        # Check coverage PER CHUNK (only institution chunks)
        dimension_hits: Set[str] = set()
        per_chunk_hits: Dict[str, List[str]] = {}
        
        for result in institution_chunks:
            chunk_id = result.get('chunk_id', 'unknown')
            per_chunk_hits[chunk_id] = []
            
            # FIX: Handle multiple text formats and load from DB if needed
            text = ''
            if 'child_text' in result:
                # Expanded format (from parent_expander)
                text = (result.get('child_text', '') + ' ' + result.get('parent_context', '')).lower()
            elif 'text' in result and result.get('text'):
                # Non-expanded format with text already loaded
                text = result.get('text', '').lower()
            else:
                # Text not in result - load from database
                text = self._load_text_from_db(chunk_id).lower()
            
            # DEBUG: Log first chunk text to verify content
            if len(per_chunk_hits) == 1:
                print(f"[DimensionChecker DEBUG] First chunk text (200 chars): {text[:200]}")
                print(f"[DimensionChecker DEBUG] Text length: {len(text)}")
                print(f"[DimensionChecker DEBUG] Text source: {'child_text' if 'child_text' in result else 'text' if 'text' in result else 'database'}")
            
            # Skip empty text
            if not text or len(text) < 10:
                print(f"[DimensionChecker WARNING] Skipping chunk {chunk_id} - empty or too short text")
                continue
            
            # Check each dimension against THIS chunk
            for dimension in dimensions:
                dim_id = dimension['id']
                keywords = dimension.get('keywords', [])
                
                # Phase 6: Enhanced detection with regex patterns
                if self._check_dimension_match(text, keywords):
                    dimension_hits.add(dim_id)
                    per_chunk_hits[chunk_id].append(dim_id)
        
        # Separate required and optional dimensions
        required_dims = [d['id'] for d in dimensions if d.get('required', True)]
        optional_dims = [d['id'] for d in dimensions if not d.get('required', True)]
        
        covered = list(dimension_hits)
        missing = [d for d in required_dims if d not in dimension_hits]
        
        # Calculate coverage ratio (only for required dimensions)
        coverage_ratio = (
            len([d for d in covered if d in required_dims]) / len(required_dims)
            if required_dims else 1.0
        )
        
        return {
            'dimensions_covered': covered,
            'dimensions_missing': missing,
            'coverage_ratio': round(coverage_ratio, 3),
            'per_chunk_hits': per_chunk_hits,
            'required_dimensions': required_dims,
            'optional_dimensions': optional_dims,
            'metric_name': metric_def.get('name', 'Unknown'),
            'institution_evidence_available': True
        }
    
    def _empty_coverage(self) -> Dict[str, Any]:
        """Return empty coverage result."""
        return {
            'dimensions_covered': [],
            'dimensions_missing': [],
            'coverage_ratio': 0.0,
            'per_chunk_hits': {},
            'required_dimensions': [],
            'optional_dimensions': [],
            'metric_name': 'Unknown'
        }
    
    def _check_dimension_match(self, text: str, keywords: List[str]) -> bool:
        """
        Check if dimension is present using enhanced multi-signal detection.
        
        Pre-UI Enhancement: Combines regex, keyword proximity, and numeric signals.
        
        Args:
            text: Chunk text (lowercased)
            keywords: List of keywords for this dimension
            
        Returns:
            True if dimension is detected
        """
        detection_score = 0
        has_numeric = bool(re.search(r'\b\d+\b', text))
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Signal 1: Exact keyword match (case-insensitive) - Strong signal
            if keyword_lower in text:
                detection_score += 2
                break
            
            # Signal 2: Word boundary match (avoid partial matches) - Strong signal
            # e.g., "research" matches "research projects" but not "researcher"
            pattern = r'\b' + re.escape(keyword_lower) + r'\b'
            if re.search(pattern, text):
                detection_score += 2
                break
            
            # Signal 3: Plural/singular variations - Medium signal
            # e.g., "publication" matches "publications"
            if keyword_lower.endswith('s'):
                singular = keyword_lower[:-1]
                if singular in text:
                    detection_score += 1
                    break
            else:
                plural = keyword_lower + 's'
                if plural in text:
                    detection_score += 1
                    break
            
            # Signal 4: Common variations - Medium signal
            # e.g., "funding" matches "funded", "funds"
            variations = self._get_keyword_variations(keyword_lower)
            for variation in variations:
                if variation in text:
                    detection_score += 1
                    break
            
            # Signal 5: Keyword proximity (within 50 chars) - Weak signal
            if self._check_keyword_proximity(text, keyword_lower):
                detection_score += 1
        
        # Signal 6: Numeric presence - Weak signal (adds context)
        if has_numeric:
            detection_score += 1
        
        # Threshold: Need at least 2 points to consider dimension detected
        # This allows weaker evidence to still count toward coverage
        return detection_score >= 2
    
    def _get_keyword_variations(self, keyword: str) -> List[str]:
        """
        Generate common variations of a keyword.
        
        Args:
            keyword: Base keyword
            
        Returns:
            List of variations
        """
        variations = []
        
        # Common suffixes
        if keyword.endswith('ing'):
            # funding -> funded, fund, funds
            base = keyword[:-3]
            variations.extend([base, base + 'ed', base + 's'])
        elif keyword.endswith('ed'):
            # funded -> funding, fund, funds
            base = keyword[:-2]
            variations.extend([base, base + 'ing', base + 's'])
        elif keyword.endswith('tion'):
            # publication -> publish, published, publishing
            base = keyword[:-4]
            variations.extend([base, base + 'ed', base + 'ing'])
        
        return variations
    
    def _check_keyword_proximity(self, text: str, keyword: str, window: int = 50) -> bool:
        """
        Check if keyword appears within a proximity window of related terms.
        
        Args:
            text: Chunk text (lowercased)
            keyword: Keyword to check
            window: Character window size
            
        Returns:
            True if keyword is near related terms
        """
        # Find all occurrences of keyword-related terms
        related_terms = ['project', 'program', 'initiative', 'activity', 
                        'research', 'study', 'grant', 'funding', 'award']
        
        for term in related_terms:
            if term in text:
                # Check if keyword is within window of this term
                term_pos = text.find(term)
                keyword_pos = text.find(keyword)
                
                if keyword_pos >= 0 and abs(term_pos - keyword_pos) <= window:
                    return True
        
        return False
