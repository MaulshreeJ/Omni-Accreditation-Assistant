"""
Criterion Registry - Phase 5 Component 1
Defines all accreditation criteria for automated evaluation.
"""

from typing import List, Dict, Any


# NAAC Criteria Registry
NAAC_CRITERIA = [
    {
        "criterion": "3.2.1",
        "description": "Grants received from Government and non-governmental agencies for research projects / endowments in the institution during the last five years",
        "query_template": "research funding grants from government and non-governmental agencies"
    },
    {
        "criterion": "3.3.1",
        "description": "Number of research papers published per teacher in the Journals notified on UGC care list during the last five years",
        "query_template": "research papers publications in UGC care journals"
    },
    {
        "criterion": "3.4.1",
        "description": "Extension activities are carried out in the neighborhood community, sensitizing students to social issues, for their holistic development, and impact thereof during the last five years",
        "query_template": "extension activities community engagement social issues"
    },
    {
        "criterion": "3.4.2",
        "description": "Awards and recognitions received for extension activities from government / government recognised bodies",
        "query_template": "awards recognitions for extension activities"
    },
    {
        "criterion": "3.5.1",
        "description": "Number of functional MoUs/linkages with institutions/ industries in India and abroad for internship, on-the-job training, project work, student / faculty exchange and collaborative research during the last five years",
        "query_template": "MoUs linkages with institutions industries for internship training research"
    }
]


# NBA Criteria Registry
NBA_CRITERIA = [
    {
        "criterion": "C5",
        "description": "Faculty information and contributions",
        "query_template": "faculty qualifications experience research publications"
    },
    {
        "criterion": "C6",
        "description": "Facilities and technical support",
        "query_template": "facilities infrastructure laboratories equipment technical support"
    },
    {
        "criterion": "C7",
        "description": "Continuous improvement",
        "query_template": "continuous improvement quality enhancement feedback mechanisms"
    }
]


# Complete registry
CRITERIA_REGISTRY = {
    "NAAC": NAAC_CRITERIA,
    "NBA": NBA_CRITERIA
}


def get_criteria(framework: str) -> List[Dict[str, Any]]:
    """
    Get all criteria for a framework.
    
    Args:
        framework: 'NAAC' or 'NBA'
        
    Returns:
        List of criterion dictionaries
        
    Raises:
        ValueError: If framework is invalid
    """
    framework = framework.upper()
    
    if framework not in CRITERIA_REGISTRY:
        raise ValueError(f"Invalid framework: {framework}. Must be 'NAAC' or 'NBA'")
    
    return CRITERIA_REGISTRY[framework]


def get_criterion(framework: str, criterion_id: str) -> Dict[str, Any]:
    """
    Get a specific criterion.
    
    Args:
        framework: 'NAAC' or 'NBA'
        criterion_id: Criterion ID (e.g., '3.2.1' or 'C5')
        
    Returns:
        Criterion dictionary
        
    Raises:
        ValueError: If criterion not found
    """
    criteria = get_criteria(framework)
    
    for criterion in criteria:
        if criterion['criterion'] == criterion_id:
            return criterion
    
    raise ValueError(f"Criterion {criterion_id} not found in {framework}")


def get_all_criteria() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all criteria for all frameworks.
    
    Returns:
        Complete criteria registry
    """
    return CRITERIA_REGISTRY


def get_criterion_count(framework: str) -> int:
    """
    Get total number of criteria for a framework.
    
    Args:
        framework: 'NAAC' or 'NBA'
        
    Returns:
        Number of criteria
    """
    return len(get_criteria(framework))
