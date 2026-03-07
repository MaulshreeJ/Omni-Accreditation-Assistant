"""
D4 - JSON Schema Validator
Validates LLM output against Pydantic schema.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field, validator


class ComplianceOutput(BaseModel):
    """Pydantic schema for compliance auditor output."""
    
    evidence_summary: str = Field(..., min_length=10, description="Summary of evidence found")
    gaps: List[str] = Field(..., min_items=0, description="List of gaps identified")
    recommendation: str = Field(..., min_length=10, description="Actionable recommendations")
    
    @validator('evidence_summary')
    def validate_summary(cls, v):
        """Ensure summary is meaningful."""
        if len(v.strip()) < 10:
            raise ValueError("Evidence summary too short")
        return v.strip()
    
    @validator('gaps')
    def validate_gaps(cls, v):
        """Ensure gaps is a list."""
        if not isinstance(v, list):
            return [str(v)]
        return [str(gap).strip() for gap in v if gap]
    
    @validator('recommendation')
    def validate_recommendation(cls, v):
        """Ensure recommendation is meaningful."""
        if isinstance(v, list):
            v = ' | '.join(v)
        if len(v.strip()) < 10:
            raise ValueError("Recommendation too short")
        return v.strip()


class JsonValidator:
    """Validate LLM output against schema."""
    
    def validate(self, llm_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate LLM output against Pydantic schema.
        
        Args:
            llm_output: Raw output from ComplianceAuditor
            
        Returns:
            Validated and normalized output
        """
        try:
            # Validate with Pydantic
            validated = ComplianceOutput(**llm_output)
            
            # Return as dict
            return validated.dict()
            
        except Exception as e:
            print(f"Validation error: {e}")
            
            # Attempt to salvage partial data
            return self._salvage_output(llm_output)
    
    def _salvage_output(self, llm_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to salvage partial output.
        
        Args:
            llm_output: Raw output that failed validation
            
        Returns:
            Best-effort salvaged output
        """
        salvaged = {
            'evidence_summary': llm_output.get('evidence_summary', 'Unable to generate summary'),
            'gaps': llm_output.get('gaps', ['Validation failed']),
            'recommendation': llm_output.get('recommendation', 'Review evidence manually')
        }
        
        # Ensure gaps is a list
        if not isinstance(salvaged['gaps'], list):
            salvaged['gaps'] = [str(salvaged['gaps'])]
        
        # Ensure recommendation is a string
        if isinstance(salvaged['recommendation'], list):
            salvaged['recommendation'] = ' | '.join(salvaged['recommendation'])
        
        return salvaged
