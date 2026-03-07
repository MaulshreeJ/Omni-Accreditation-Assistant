"""
Verification script for Phase 3 metadata and template fixes.
"""

import json

# Load report
with open('docs/phase3_naac_321_verbose_report.json', 'r') as f:
    report = json.load(f)

print("="*80)
print("PHASE 3 FIXES VERIFICATION")
print("="*80)

# 1. Source Type Fix
print("\n1. SOURCE TYPE FIX:")
print("   All sources should show 'framework' (not 'institution')")
all_framework = all(s['source_type'] == 'framework' for s in report['evidence_sources'])
for i, source in enumerate(report['evidence_sources'], 1):
    status = "✓" if source['source_type'] == 'framework' else "✗"
    print(f"   {status} Chunk {i}: {source['source_type']}")
print(f"   Result: {'✅ PASS' if all_framework else '❌ FAIL'}")

# 2. Evidence Score Fix
print("\n2. EVIDENCE SCORE FIX:")
print("   Average should be 0.20-0.45 for framework templates")
avg_evidence = report['avg_evidence_score']
in_range = 0.20 <= avg_evidence <= 0.45
print(f"   Average Evidence Score: {avg_evidence:.3f}")
print(f"   Expected Range: 0.20-0.45")
print(f"   Result: {'✅ PASS' if in_range else '❌ FAIL'}")

# 3. Template Penalty Applied
print("\n3. TEMPLATE PENALTY:")
print("   Framework penalty (0.6x) + Template penalty (0.7x) = 0.42x combined")
print(f"   Evidence score < 0.65 indicates framework penalty applied")
framework_penalty = avg_evidence < 0.65
print(f"   Result: {'✅ PASS' if framework_penalty else '❌ FAIL'}")

# 4. Confidence Score
print("\n4. CONFIDENCE SCORE:")
confidence = report['confidence_score']
status = report['compliance_status']
print(f"   Confidence: {confidence:.3f}")
print(f"   Status: {status}")
expected_status = status in ['Partial', 'Weak']
print(f"   Expected: Partial or Weak for framework-only")
print(f"   Result: {'✅ PASS' if expected_status else '❌ FAIL'}")

# 5. Performance
print("\n5. PERFORMANCE:")
latency = report['latency_ms']
under_target = latency < 2000
print(f"   Latency: {latency:.0f}ms")
print(f"   Target: <2000ms")
print(f"   Result: {'✅ PASS' if under_target else '❌ FAIL'}")

# 6. LLM Summary Accuracy
print("\n6. LLM SUMMARY ACCURACY:")
summary = report['evidence_summary'].lower()
has_framework = 'framework' in summary
has_institutional = 'institutional' in summary or 'no institutional' in summary
print(f"   ✓ Identifies framework templates: {'✅ YES' if has_framework else '❌ NO'}")
print(f"   ✓ Notes missing institutional data: {'✅ YES' if has_institutional else '❌ NO'}")

# Overall Result
print("\n" + "="*80)
all_pass = all([
    all_framework,
    in_range,
    framework_penalty,
    expected_status,
    under_target,
    has_framework,
    has_institutional
])
print(f"OVERALL: {'✅ ALL CHECKS PASSED' if all_pass else '❌ SOME CHECKS FAILED'}")
print("="*80)
