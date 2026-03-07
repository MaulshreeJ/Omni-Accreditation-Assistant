"""
Phase 5 - Evidence Mapper
Maps retrieved evidence to metric dimensions for traceability.
"""

import yaml
from typing import List, Dict, Any
from pathlib import Path


class EvidenceMapper:
    """Map evidence chunks to metric dimensions."""
    
    def __init__(self, metric_maps_dir: str = "data/metric_maps"):
        """Initialize mapper with metric maps directory."""
        self.metric_maps_dir = Path(metric_maps_dir)
        self.metric_maps = {}
        self._load_metric_maps()
    
    def _load_metric_maps(self):
        """Load all metric maps from YAML files."""
        try:
            # Load NAAC map
            naac_path = self.metric_maps_dir / 'naac_metric_map.yaml'
            if naac_path.exists():
                with open(naac_path, 'r', encoding='utf-8') as f:
                    self.metric_maps['NAAC'] = yaml.safe_load(f)
            
            # Load NBA map
            nba_path = self.metric_maps_dir / 'nba_metric_map.yaml'
            if nba_path.exists():
                with open(nba_path, 'r', encoding='utf-8') as f:
                    self.metric_maps['NBA'] = yaml.safe_load(f)
                    
        except Exception as e:
            print(f"Error loading metric maps: {e}")
            self.metric_maps = {'NAAC': {}, 'NBA': {}}
    
    def map_evidence(
        self,
        results: List[Dict[str, Any]],
        framework: str,
        criterion: str
    ) -> Dict[str, Any]:
        """
        Map evidence chunks to dimensions.
        
        Args:
            results: Retrieval results with chunks
            framework: NAAC or NBA
            criterion: Criterion ID
            
        Returns:
            Mapping dict with dimension_evidence_map
        """
        # Get metric definition
        metric_def = self._get_metric_definition(framework, criterion)
        
        if not metric_def:
            return {
                'dimension_evidence_map': {},
                'dimensions_mapped': [],
                'dimensions_unmapped': []
            }
        
        # Extract dimensions
        dimensions = metric_def.get('dimensions', [])
        
        # Map each dimension to chunks
        dimension_map = {}
        dimensions_mapped = []
        dimensions_unmapped = []
        
        for dimension in dimensions:
            dim_id = dimension['id']
            keywords = dimension.get('keywords', [])
            required = dimension.get('required', False)
            
            # Find chunks containing dimension keywords
            matching_chunks = self._find_matching_chunks(results, keywords)
            
            if matching_chunks:
                dimension_map[dim_id] = matching_chunks
                dimensions_mapped.append(dim_id)
            else:
                if required:
                    dimensions_unmapped.append(dim_id)
        
        return {
            'dimension_evidence_map': dimension_map,
            'dimensions_mapped': dimensions_mapped,
            'dimensions_unmapped': dimensions_unmapped
        }
    
    def _get_metric_definition(self, framework: str, criterion: str) -> Dict[str, Any]:
        """Get metric definition from loaded maps."""
        if framework not in self.metric_maps:
            return None
        
        framework_map = self.metric_maps[framework]
        
        # Handle nested structure (NAAC/NBA as top-level key)
        if framework in framework_map:
            framework_map = framework_map[framework]
        
        return framework_map.get(criterion)
    
    def _find_matching_chunks(
        self,
        results: List[Dict[str, Any]],
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Find chunks that contain dimension keywords.
        
        Args:
            results: Retrieval results
            keywords: Dimension keywords to search for
            
        Returns:
            List of matching chunk info
        """
        matching = []
        
        for result in results:
            # Combine child and parent text
            text = result.get('child_text', '') + ' ' + result.get('parent_context', '')
            text_lower = text.lower()
            
            # Check if any keyword matches
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matching.append({
                        'chunk_id': result.get('chunk_id'),
                        'source': result.get('source'),
                        'page': result.get('page'),
                        'matched_keyword': keyword
                    })
                    break  # Only add once per chunk
        
        return matching
