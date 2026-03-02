"""
Framework Router - Phase 2
Routes queries to appropriate framework and query type.
"""

import re
from typing import Dict


class FrameworkRouter:
    """
    Routes queries to NAAC or NBA framework and determines query type.
    """
    
    def __init__(self):
        # Framework keywords
        self.naac_keywords = [
            'naac', 'ssr', 'aqar', 'dvv', 'raf', 'cgpa', 'qif',
            'university', 'college', 'autonomous'
        ]
        
        self.nba_keywords = [
            'nba', 'sar', 'tier', 'po', 'peo', 'pso', 'obe',
            'program outcome', 'attainment', 'engineering', 'technical'
        ]
        
        # Query type keywords
        self.prequalifier_keywords = [
            'eligibility', 'minimum requirement', 'prerequisite',
            'qualification', 'pre-qualifier', 'prequalifier'
        ]
        
        self.policy_keywords = [
            'appeal', 'visit process', 'accreditation period',
            'validity', 'procedure', 'timeline', 'fee',
            'application process', 'how to apply', 'duration'
        ]
    
    def route_framework(self, query: str) -> Dict[str, str]:
        """
        Route query to framework and determine query type.
        
        Args:
            query: User query
            
        Returns:
            Dict with 'framework' and 'query_type'
        """
        query_lower = query.lower()
        
        # Detect framework
        naac_score = sum(1 for kw in self.naac_keywords if kw in query_lower)
        nba_score = sum(1 for kw in self.nba_keywords if kw in query_lower)
        
        # Check for explicit metric patterns
        has_naac_metric = bool(re.search(r'\b\d\.\d\.\d\b', query))
        has_nba_po = bool(re.search(r'\b(PO|PEO|PSO)\d+\b', query, re.IGNORECASE))
        
        if has_naac_metric:
            naac_score += 3
        if has_nba_po:
            nba_score += 3
        
        # Determine framework
        if nba_score > naac_score:
            framework = 'NBA'
        elif naac_score > nba_score:
            framework = 'NAAC'
        else:
            # Default to NAAC if ambiguous
            framework = 'NAAC'
        
        # Detect query type
        prequalifier_score = sum(1 for kw in self.prequalifier_keywords if kw in query_lower)
        policy_score = sum(1 for kw in self.policy_keywords if kw in query_lower)
        
        if prequalifier_score > 0:
            query_type = 'prequalifier'
        elif policy_score > 0:
            query_type = 'policy'
        else:
            # Default to metric
            query_type = 'metric'
        
        return {
            'framework': framework,
            'query_type': query_type
        }


# Test function
if __name__ == "__main__":
    router = FrameworkRouter()
    
    test_queries = [
        "Are we compliant with NAAC 3.2.1?",
        "What are the minimum faculty requirements for NBA Tier-II?",
        "How long is NBA accreditation valid?",
        "What is PO1 attainment calculation?"
    ]
    
    for query in test_queries:
        result = router.route_framework(query)
        print(f"Query: {query}")
        print(f"  Framework: {result['framework']}, Type: {result['query_type']}\n")
