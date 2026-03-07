"""
Test dimension checking directly
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scoring.dimension_checker import DimensionChecker

# Initialize
checker = DimensionChecker()

# Mock retrieval results with institution evidence
results = [
    {
        'chunk_id': '1',
        'source_type': 'institution',
        'child_text': 'Total Research Funding (2020-2024) 1.2 Crore Externally Funded Projects 8 Funding Agencies UGC, AICTE',
        'parent_context': ''
    },
    {
        'chunk_id': '2',
        'source_type': 'institution',
        'child_text': 'Metric: Total Research Funding Value: 1.2 Crore',
        'parent_context': ''
    },
    {
        'chunk_id': '3',
        'source_type': 'framework',
        'child_text': 'NAAC framework text about research funding',
        'parent_context': ''
    }
]

# Check coverage
coverage = checker.check(results, 'NAAC', '3.2.1')

print("\n=== DIMENSION COVERAGE TEST ===")
print(f"Metric Name: {coverage.get('metric_name')}")
print(f"Required Dimensions: {coverage.get('required_dimensions')}")
print(f"Dimensions Covered: {coverage.get('dimensions_covered')}")
print(f"Dimensions Missing: {coverage.get('dimensions_missing')}")
print(f"Coverage Ratio: {coverage.get('coverage_ratio')}")
print(f"Institution Evidence Available: {coverage.get('institution_evidence_available')}")

print("\n=== PER-CHUNK HITS ===")
for chunk_id, dims in coverage.get('per_chunk_hits', {}).items():
    print(f"Chunk {chunk_id}: {dims}")
