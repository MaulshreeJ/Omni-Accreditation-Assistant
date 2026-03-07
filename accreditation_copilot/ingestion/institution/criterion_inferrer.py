"""
Criterion Inferrer - Phase 4 Architectural Fix
Infers NAAC/NBA criterion from table context.
"""

import re
from typing import Tuple, Optional


class CriterionInferrer:
    """Infer criterion from table context."""
    
    def __init__(self):
        """Initialize criterion inferrer."""
        pass
    
    def infer_criterion_from_context(self, page_text: str, table_caption: str = "",
                                     surrounding_text: str = "") -> Tuple[Optional[str], Optional[str]]:
        """
        Infer criterion and framework from context.
        
        Strategy:
        PASS 1 — TABLE CAPTION: Look for patterns like "Table 3.2.1"
        PASS 2 — SECTION HEADER: Search first 10 lines above table
        PASS 3 — PAGE HEADER: Search first 5 lines of page
        
        Args:
            page_text: Full page text
            table_caption: Table caption if available
            surrounding_text: Text surrounding the table
            
        Returns:
            Tuple of (criterion, framework) or (None, None)
        """
        # PASS 1 — TABLE CAPTION
        if table_caption:
            criterion, framework = self._extract_from_caption(table_caption)
            if criterion:
                return criterion, framework
        
        # PASS 2 — SECTION HEADER (first 10 lines above table)
        if surrounding_text:
            lines = surrounding_text.split('\n')[:10]
            for line in lines:
                criterion, framework = self._extract_from_text(line)
                if criterion:
                    return criterion, framework
        
        # PASS 3 — PAGE HEADER (first 5 lines of page)
        if page_text:
            lines = page_text.split('\n')[:5]
            for line in lines:
                criterion, framework = self._extract_from_text(line)
                if criterion:
                    return criterion, framework
        
        return None, None
    
    def _extract_from_caption(self, caption: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract criterion from table caption.
        
        Examples:
        - "Table 3.2.1 Research Funding" → ("3.2.1", "NAAC")
        - "Table 3.2.2: Faculty Details" → ("3.2.2", "NAAC")
        
        Args:
            caption: Table caption text
            
        Returns:
            Tuple of (criterion, framework) or (None, None)
        """
        # NAAC pattern: X.Y.Z
        naac_match = re.search(r'\b(\d\.\d\.\d)\b', caption)
        if naac_match:
            return naac_match.group(1), 'NAAC'
        
        # NBA Criterion pattern: Criterion X
        criterion_match = re.search(r'\bCriterion\s+(\d+)\b', caption, re.IGNORECASE)
        if criterion_match:
            return f"C{criterion_match.group(1)}", 'NBA'
        
        # NBA PO pattern: PO1, PO2, etc.
        po_match = re.search(r'\b(PO\d+)\b', caption, re.IGNORECASE)
        if po_match:
            return po_match.group(1).upper(), 'NBA'
        
        # NBA PEO pattern: PEO1, PEO2, etc.
        peo_match = re.search(r'\b(PEO\d+)\b', caption, re.IGNORECASE)
        if peo_match:
            return peo_match.group(1).upper(), 'NBA'
        
        return None, None
    
    def _extract_from_text(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract criterion from text line.
        
        Examples:
        - "3.2.1 Extramural Funding for Research" → ("3.2.1", "NAAC")
        - "Criterion 5: Student Support" → ("C5", "NBA")
        
        Args:
            text: Text line
            
        Returns:
            Tuple of (criterion, framework) or (None, None)
        """
        # NAAC pattern at start of line
        naac_match = re.search(r'^\s*(\d\.\d\.\d)\b', text)
        if naac_match:
            return naac_match.group(1), 'NAAC'
        
        # NAAC pattern anywhere in line
        naac_match = re.search(r'\b(\d\.\d\.\d)\b', text)
        if naac_match:
            return naac_match.group(1), 'NAAC'
        
        # NBA Criterion pattern
        criterion_match = re.search(r'\bCriterion\s+(\d+)\b', text, re.IGNORECASE)
        if criterion_match:
            return f"C{criterion_match.group(1)}", 'NBA'
        
        # NBA PO pattern
        po_match = re.search(r'\b(PO\d+)\b', text, re.IGNORECASE)
        if po_match:
            return po_match.group(1).upper(), 'NBA'
        
        # NBA PEO pattern
        peo_match = re.search(r'\b(PEO\d+)\b', text, re.IGNORECASE)
        if peo_match:
            return peo_match.group(1).upper(), 'NBA'
        
        return None, None


# Test function
if __name__ == '__main__':
    inferrer = CriterionInferrer()
    
    # Test cases
    test_cases = [
        ("Table 3.2.1 Research Funding Details", "", ""),
        ("", "", "3.2.1 Extramural Funding for Research\nTable showing details"),
        ("Criterion 5: Student Support and Progression\nTable 1", "", ""),
        ("", "Table for PO1 attainment", ""),
    ]
    
    for caption, surrounding, page in test_cases:
        criterion, framework = inferrer.infer_criterion_from_context(page, caption, surrounding)
        print(f"Caption: '{caption[:50]}...' → {framework} {criterion}")
