"""
Test the complete audit flow to see where source_type is lost
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from audit.criterion_auditor import CriterionAuditor
from models.model_manager import get_model_manager
import json

# Initialize
model_manager = get_model_manager()
auditor = CriterionAuditor(model_manager=model_manager, enable_cache=False)

# Run audit
result = auditor.audit_criterion(
    criterion_id="3.2.1",
    framework="NAAC",
    query_template="What are the requirements for NAAC A+?",
    description="Research Publications and Awards"
)

print("\n=== AUDIT RESULT ===")
print(f"Confidence: {result.get('confidence_score', 0)}")
print(f"Coverage: {result.get('coverage_ratio', 0)}")
print(f"Evidence Count: {result.get('evidence_count', 0)}")
print(f"Institution Evidence Available: {result.get('institution_evidence_available', False)}")

print("\n=== EVIDENCE SOURCES ===")
for i, source in enumerate(result.get('evidence_sources', [])[:5], 1):
    print(f"\n{i}. {source.get('source', 'unknown')}")
    print(f"   Source Type: {source.get('source_type', 'MISSING')}")
    print(f"   Page: {source.get('page', '?')}")
    print(f"   Score: {source.get('reranker_score', 0)}")

print("\n=== DIMENSION COVERAGE ===")
print(f"Covered: {result.get('dimensions_covered', [])}")
print(f"Missing: {result.get('dimensions_missing', [])}")
print(f"Coverage Ratio: {result.get('coverage_ratio', 0)}")

# Save full result for inspection
with open('audit_debug_result.json', 'w') as f:
    json.dump(result, f, indent=2)
    print("\n\nFull result saved to audit_debug_result.json")
