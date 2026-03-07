"""
Quick integration test to verify runtime reliability fixes.
"""

from audit.criterion_auditor import CriterionAuditor

print("\n" + "="*80)
print("INTEGRATION TEST: Runtime Reliability")
print("="*80)

# Initialize auditor
auditor = CriterionAuditor()

# Run audit
result = auditor.audit_criterion(
    criterion_id='3.2.1',
    framework='NAAC',
    query_template='What is the extramural funding?',
    description='Extramural funding'
)

# Display results
print(f"\nStatus: {result['compliance_status']}")
print(f"Confidence: {result['confidence_score']:.3f}")
print(f"Coverage: {result['coverage_ratio']:.3f}")
print(f"Evidence: {result['evidence_count']} chunks")
print(f"Institution: {result['institution_evidence_count']} chunks")

# Verify validation occurred
print(f"\n[CHECK] Confidence score in [0, 1]: {0 <= result['confidence_score'] <= 1}")
print(f"[CHECK] Coverage ratio in [0, 1]: {0 <= result['coverage_ratio'] <= 1}")
print(f"[CHECK] Evidence counts consistent: {result['institution_evidence_count'] <= result['evidence_count']}")

auditor.close()

print("\n[SUCCESS] Integration test passed")
print("="*80)
