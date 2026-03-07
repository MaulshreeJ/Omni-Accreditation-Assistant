"""
C1 - Evidence Scorer
Deterministic scoring of evidence quality in retrieved chunks.
No LLM calls - pure signal detection.

FIXED v3: Additional template penalty to prevent instruction section inflation.
- Numeric evidence requires currency values, project counts, or date ranges
- Structure signal only activates if real evidence is present
- Framework chunks receive 0.6x penalty
- Template sections receive additional 0.7x penalty
"""

import re
from typing import List, Dict, Any


class EvidenceScorer:
    """Score evidence quality based on detectable signals."""
    
    # FIXED: Stricter patterns for real evidence only
    CURRENCY_PATTERN = re.compile(r'(rs\.?|inr|₹)\s*\d+(\.\d+)?\s*(crore|lakh|lakhs|million)?', re.IGNORECASE)
    PROJECT_COUNT_PATTERN = re.compile(r'\d+\s+(projects?|grants?|proposals?|schemes?)', re.IGNORECASE)
    DATE_RANGE_PATTERN = re.compile(r'(19|20)\d{2}[-–]\d{2,4}', re.IGNORECASE)
    
    ENTITY_PATTERN = re.compile(r'\b(dst|serb|dbt|icssr|ugc|aicte)\b', re.IGNORECASE)
    KEYWORD_PATTERN = re.compile(r'\b(grant|funded|sanctioned|extramural|sponsored|awarded)\b', re.IGNORECASE)
    STRUCTURE_PATTERN = re.compile(r'(\||table|year wise|year-wise|\t)', re.IGNORECASE)
    
    # Signal weights
    WEIGHTS = {
        'numeric': 0.25,
        'entity': 0.20,
        'keyword': 0.15,
        'structure': 0.10,
        'reranker': 0.30
    }
    
    def score(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score evidence quality for each retrieved chunk.
        
        FIXED: Apply framework penalty to prevent guideline inflation.
        
        Args:
            results: List of retrieval results from Phase 2
            
        Returns:
            List of evidence scores with signals and normalized values
        """
        scored_results = []
        
        for result in results:
            # Combine child and parent text for analysis
            text = result.get('child_text', '') + ' ' + result.get('parent_context', '')
            
            # Detect signals with stricter rules
            signals = self._detect_signals(text)
            
            # Get reranker score from Phase 2 (handle both formats)
            reranker_score = result.get('reranker_score', 0.0)
            if reranker_score == 0.0:
                # Try nested format
                reranker_score = result.get('scores', {}).get('reranker', 0.0)
            
            # Calculate evidence score
            evidence_score = self._calculate_score(signals, reranker_score)
            
            # FIXED: Apply framework penalty
            source_type = result.get('source_type', 'framework')  # Default to framework
            if source_type == 'framework':
                evidence_score *= 0.6  # Penalty for guideline documents
            
            # FIXED: Apply template penalty for template/instruction sections
            text_lower = text.lower()
            if self._is_template_section(text_lower):
                evidence_score *= 0.7  # Additional penalty for templates
            
            scored_results.append({
                'chunk_id': result.get('chunk_id', 'unknown'),
                'evidence_score': round(evidence_score, 3),
                'source_type': source_type,
                'signals': {
                    'numeric': round(signals['numeric'], 3),
                    'entity': round(signals['entity'], 3),
                    'keyword': round(signals['keyword'], 3),
                    'structure': round(signals['structure'], 3)
                }
            })
        
        return scored_results
    
    def _is_template_section(self, text_lower: str) -> bool:
        """
        Detect if text is a template or instruction section.
        
        Args:
            text_lower: Lowercase text
            
        Returns:
            True if template section detected
        """
        template_indicators = [
            'template',
            'upload the following',
            'provide the following',
            'data template',
            'fill in the',
            'enter the',
            'attach the',
            'submit the',
            'upload documents',
            'upload certificate',
            'upload award'
        ]
        
        return any(indicator in text_lower for indicator in template_indicators)
    
    def _detect_signals(self, text: str) -> Dict[str, float]:
        """
        Detect evidence signals in text.
        
        FIXED: Stricter numeric detection - requires real values, not templates.
        - Currency values (Rs. 4.2 crore, INR 50 lakhs)
        - Project counts (23 projects funded)
        - Date ranges (2019-2024)
        
        Structure signal only activates if numeric OR entity evidence exists.
        """
        # FIXED: Count only real evidence patterns
        currency_matches = len(self.CURRENCY_PATTERN.findall(text))
        project_matches = len(self.PROJECT_COUNT_PATTERN.findall(text))
        date_matches = len(self.DATE_RANGE_PATTERN.findall(text))
        
        # Total numeric evidence (cap at 5)
        total_numeric = currency_matches + project_matches + date_matches
        numeric_signal = min(total_numeric / 5.0, 1.0)
        
        # Entity and keyword detection
        entity_matches = len(self.ENTITY_PATTERN.findall(text))
        keyword_matches = len(self.KEYWORD_PATTERN.findall(text))
        structure_matches = len(self.STRUCTURE_PATTERN.findall(text))
        
        entity_signal = min(entity_matches / 3.0, 1.0)
        keyword_signal = min(keyword_matches / 3.0, 1.0)
        
        # FIXED: Structure signal only if real evidence exists
        if numeric_signal > 0 or entity_signal > 0:
            structure_signal = min(structure_matches / 2.0, 1.0)
        else:
            structure_signal = 0.0  # No structure credit for templates
        
        return {
            'numeric': numeric_signal,
            'entity': entity_signal,
            'keyword': keyword_signal,
            'structure': structure_signal
        }
    
    def _calculate_score(self, signals: Dict[str, float], reranker_score: float) -> float:
        """Calculate final evidence score using weighted formula."""
        score = (
            self.WEIGHTS['numeric'] * signals['numeric'] +
            self.WEIGHTS['entity'] * signals['entity'] +
            self.WEIGHTS['keyword'] * signals['keyword'] +
            self.WEIGHTS['structure'] * signals['structure'] +
            self.WEIGHTS['reranker'] * reranker_score
        )
        
        # Clamp to [0, 1]
        return min(max(score, 0.0), 1.0)
