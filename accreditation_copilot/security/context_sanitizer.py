"""
D1 - Context Sanitizer
Prevents prompt injection from retrieved chunks.
"""

import re
from typing import List, Dict, Any


class ContextSanitizer:
    """Sanitize retrieved chunks to prevent prompt injection."""
    
    # Injection patterns to remove
    INJECTION_PATTERNS = [
        r'ignore\s+previous\s+instructions',
        r'system\s+prompt',
        r'developer\s+instructions',
        r'you\s+are\s+chatgpt',
        r'you\s+are\s+an?\s+ai',
        r'disregard\s+all',
        r'forget\s+everything',
        r'new\s+instructions',
        r'override\s+instructions'
    ]
    
    MAX_TOKENS_PER_CHUNK = 800
    
    def __init__(self):
        """Initialize sanitizer with compiled patterns."""
        self.injection_regex = re.compile(
            '|'.join(self.INJECTION_PATTERNS),
            re.IGNORECASE
        )
    
    def sanitize(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sanitize all retrieved chunks.
        
        Args:
            results: Retrieval results from Phase 2
            
        Returns:
            Sanitized results with clean text
        """
        sanitized = []
        
        for result in results:
            # Get text fields
            child_text = result.get('child_text', '')
            parent_context = result.get('parent_context', '')
            
            # Sanitize both
            clean_child = self._sanitize_text(child_text)
            clean_parent = self._sanitize_text(parent_context)
            
            # Create sanitized result
            sanitized_result = result.copy()
            sanitized_result['child_text'] = clean_child
            sanitized_result['parent_context'] = clean_parent
            
            sanitized.append(sanitized_result)
        
        return sanitized
    
    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize a single text string.
        
        Args:
            text: Raw text
            
        Returns:
            Sanitized text
        """
        if not text:
            return text
        
        # Remove injection patterns
        clean = self.injection_regex.sub('[REMOVED]', text)
        
        # Escape XML characters
        clean = self._escape_xml(clean)
        
        # Cap length (approximate token limit)
        clean = self._cap_length(clean)
        
        # Remove dangerous code blocks
        clean = self._remove_code_blocks(clean)
        
        return clean
    
    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters."""
        replacements = {
            '<': '&lt;',
            '>': '&gt;',
            '&': '&amp;'
        }
        
        for char, escape in replacements.items():
            text = text.replace(char, escape)
        
        return text
    
    def _cap_length(self, text: str) -> str:
        """Cap text length to approximate token limit."""
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = self.MAX_TOKENS_PER_CHUNK * 4
        
        if len(text) > max_chars:
            return text[:max_chars] + '...[truncated]'
        
        return text
    
    def _remove_code_blocks(self, text: str) -> str:
        """Remove markdown code blocks that could contain injection."""
        # Remove ```...``` blocks
        text = re.sub(r'```[\s\S]*?```', '[CODE_BLOCK_REMOVED]', text)
        
        # Remove inline code with suspicious content
        text = re.sub(r'`[^`]*(?:system|prompt|instruction)[^`]*`', '[CODE_REMOVED]', text, flags=re.IGNORECASE)
        
        return text
