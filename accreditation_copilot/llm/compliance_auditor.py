"""
D3 - Compliance Auditor
Groq LLM call for compliance synthesis.
Refactored from scoring/synthesizer.py with security enhancements.
"""

import json
from typing import List, Dict, Any
from utils.groq_pool import GroqKeyPool


class ComplianceAuditor:
    """Generate compliance explanation using Groq LLM."""
    
    def __init__(self):
        """Initialize auditor with Groq pool."""
        self.groq_pool = GroqKeyPool()
    
    def audit(
        self,
        prompt: str,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Call Groq LLM for compliance auditing.
        
        Args:
            prompt: Structured XML prompt from PromptBuilder
            max_retries: Maximum retry attempts
            
        Returns:
            Dict with evidence_summary, gaps, recommendation
        """
        for attempt in range(max_retries + 1):
            try:
                response, _ = self.groq_pool.completion(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a compliance analysis expert. Analyze evidence and provide structured JSON output only."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,
                    max_tokens=800
                )
                
                # Parse JSON response
                content = response.choices[0].message.content.strip()
                
                # Extract JSON if wrapped in markdown
                if content.startswith('```'):
                    content = content.split('```')[1]
                    if content.startswith('json'):
                        content = content[4:]
                    content = content.strip()
                
                # Parse JSON
                result = json.loads(content)
                
                # Validate required fields
                required_fields = ['evidence_summary', 'gaps', 'recommendation']
                if all(field in result for field in required_fields):
                    return result
                else:
                    if attempt < max_retries:
                        print(f"Missing required fields, retry {attempt + 1}/{max_retries}")
                        continue
                    else:
                        return self._fallback_response()
                
            except json.JSONDecodeError as e:
                if attempt < max_retries:
                    print(f"JSON parse error, retry {attempt + 1}/{max_retries}: {e}")
                    continue
                else:
                    print(f"JSON parse failed after {max_retries} retries")
                    return self._fallback_response()
            
            except Exception as e:
                print(f"Audit error: {e}")
                return self._fallback_response()
        
        return self._fallback_response()
    
    def _fallback_response(self) -> Dict[str, Any]:
        """Fallback response if LLM fails."""
        return {
            'evidence_summary': 'Unable to generate synthesis due to processing error.',
            'gaps': ['Synthesis generation failed'],
            'recommendation': 'Retry analysis or review evidence manually.'
        }
