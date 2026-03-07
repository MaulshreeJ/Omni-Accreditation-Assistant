"""
C4 - Compliance Synthesizer
Single LLM call for generating compliance explanation.
Uses Groq for fast inference.

REFACTORED: Now uses D1-D5 security/validation layers.
"""

import json
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from security.context_sanitizer import ContextSanitizer
from security.prompt_builder import PromptBuilder
from llm.compliance_auditor import ComplianceAuditor
from validation.json_validator import JsonValidator


class ComplianceSynthesizer:
    """Generate compliance explanation using LLM with security layers."""
    
    def __init__(self):
        """Initialize synthesizer with D1-D5 components."""
        self.sanitizer = ContextSanitizer()  # D1
        self.prompt_builder = PromptBuilder()  # D2
        self.auditor = ComplianceAuditor()  # D3
        self.validator = JsonValidator()  # D4
    
    def generate(
        self,
        criterion: str,
        framework: str,
        confidence: Dict[str, Any],
        coverage: Dict[str, Any],
        results: List[Dict[str, Any]],
        evidence_scores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate compliance explanation using D1-D5 layers.
        
        Args:
            criterion: Criterion ID
            framework: 'NAAC' or 'NBA'
            confidence: Output from ConfidenceCalculator
            coverage: Output from DimensionChecker
            results: Phase 2 retrieval results
            evidence_scores: Output from EvidenceScorer
            
        Returns:
            Validated synthesis with explanation, gaps, and recommendations
        """
        # D1: Sanitize context
        sanitized_results = self.sanitizer.sanitize(results)
        
        # D2: Build secure XML prompt
        prompt = self.prompt_builder.build_compliance_prompt(
            query="",  # Not needed in prompt
            criterion=criterion,
            framework=framework,
            metric_name=coverage.get('metric_name', 'Unknown'),
            confidence=confidence,
            coverage=coverage,
            sanitized_chunks=sanitized_results
        )
        
        # D3: Call Groq auditor
        llm_output = self.auditor.audit(prompt, max_retries=2)
        
        # D4: Validate JSON schema
        validated_output = self.validator.validate(llm_output)
        
        return validated_output

