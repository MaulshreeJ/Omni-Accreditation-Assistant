"""
D2 - Secure XML Prompt Builder
Builds structured prompts with strict XML boundaries.
"""

from typing import List, Dict, Any


class PromptBuilder:
    """Build secure XML-structured prompts for LLM."""
    
    def build_compliance_prompt(
        self,
        query: str,
        criterion: str,
        framework: str,
        metric_name: str,
        confidence: Dict[str, Any],
        coverage: Dict[str, Any],
        sanitized_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Build secure XML prompt for compliance auditing.
        
        Args:
            query: User query
            criterion: Criterion ID
            framework: NAAC or NBA
            metric_name: Full metric name
            confidence: Confidence scores
            coverage: Dimension coverage
            sanitized_chunks: Sanitized evidence chunks
            
        Returns:
            XML-structured prompt string
        """
        # Build system instructions
        system_instructions = self._build_system_instructions()
        
        # Build hypothetical ideal answer
        hypothetical = self._build_hypothetical_ideal(framework, criterion, metric_name)
        
        # Build retrieved context
        context = self._build_retrieved_context(sanitized_chunks)
        
        # Build output schema
        schema = self._build_output_schema()
        
        # Assemble full prompt
        prompt = f"""<SYSTEM_INSTRUCTIONS>
{system_instructions}
</SYSTEM_INSTRUCTIONS>

<USER_QUERY>
{query}
</USER_QUERY>

<CRITERION_INFO>
Framework: {framework}
Criterion: {criterion}
Metric: {metric_name}
Confidence Score: {confidence['confidence_score']:.3f} ({confidence['status']})
Dimensions Covered: {', '.join(coverage['dimensions_covered']) if coverage['dimensions_covered'] else 'None'}
Dimensions Missing: {', '.join(coverage['dimensions_missing']) if coverage['dimensions_missing'] else 'None'}
</CRITERION_INFO>

<HYPOTHETICAL_IDEAL>
{hypothetical}
</HYPOTHETICAL_IDEAL>

<RETRIEVED_CONTEXT>
{context}
</RETRIEVED_CONTEXT>

<OUTPUT_SCHEMA>
{schema}
</OUTPUT_SCHEMA>"""
        
        return prompt
    
    def _build_system_instructions(self) -> str:
        """Build system instructions section."""
        return """You are a compliance auditing expert for educational accreditation.

Your responsibilities:
1. Analyze retrieved evidence chunks
2. Summarize what evidence was found
3. Identify gaps in the evidence
4. Provide actionable recommendations

Critical rules:
- Use ONLY the retrieved evidence provided
- Do NOT invent or fabricate data
- Do NOT contradict the confidence score
- Do NOT determine compliance status (already calculated)
- If only templates/guidelines found, state "no institutional evidence found"
- Be precise and factual"""
    
    def _build_hypothetical_ideal(self, framework: str, criterion: str, metric_name: str) -> str:
        """Build hypothetical ideal answer section."""
        return f"""For {framework} {criterion} ({metric_name}), ideal evidence would include:
- Specific institutional data with numbers and dates
- Documented proof from institutional records
- Clear mapping to all required dimensions
- Verifiable sources with page references

The retrieved evidence should demonstrate actual institutional compliance, not just framework guidelines."""
    
    def _build_retrieved_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build retrieved context section with sanitized chunks."""
        if not chunks:
            return "No evidence chunks retrieved."
        
        context_parts = []
        
        for i, chunk in enumerate(chunks[:5], 1):  # Top 5 chunks
            child_text = chunk.get('child_text', '')[:500]  # Limit length
            source = chunk.get('source', 'Unknown')
            page = chunk.get('page', 'N/A')
            source_type = chunk.get('source_type', 'unknown')
            
            context_parts.append(
                f"""<EVIDENCE_{i}>
Source: {source}
Page: {page}
Type: {source_type}
Text: {child_text}...
</EVIDENCE_{i}>"""
            )
        
        return '\n\n'.join(context_parts)
    
    def _build_output_schema(self) -> str:
        """Build output schema specification."""
        return """Return ONLY valid JSON with these exact fields:

{
  "evidence_summary": "Brief summary of what evidence was found (2-3 sentences)",
  "gaps": ["List", "of", "missing", "information"],
  "recommendation": "Actionable next steps for compliance"
}

Do NOT include:
- confidence_score (already calculated)
- compliance_status (already calculated)
- coverage_ratio (already calculated)

Return ONLY the JSON object, no markdown, no additional text."""
