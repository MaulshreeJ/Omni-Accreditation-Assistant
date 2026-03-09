import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from retrieval.dual_retrieval import DualRetriever
from scoring.evidence_scorer import EvidenceScorer
from scoring.confidence_calculator import ConfidenceCalculator

# Test retrieval
retriever = DualRetriever()
query = "What is the total grant received from funding agencies for research projects?"
results, inst_available = retriever.retrieve(
    query=query,
    query_variants=[query],
    framework='NAAC',
    query_type='metric',
    top_k_framework=3,
    top_k_institution=7
)

print(f"Total results: {len(results)}")
print(f"Institution available: {inst_available}")

# Count by source type
inst_count = sum(1 for r in results if r.get('source_type') == 'institution')
framework_count = sum(1 for r in results if r.get('source_type') == 'framework')
print(f"Institution chunks: {inst_count}")
print(f"Framework chunks: {framework_count}")

# Score evidence
scorer = EvidenceScorer()
evidence_scores = scorer.score(results)

print(f"\nEvidence scores count: {len(evidence_scores)}")
for i, score in enumerate(evidence_scores[:3], 1):
    print(f"{i}. Source: {score['source_type']}, Score: {score['evidence_score']}, Signals: {score['signals']}")

# Calculate confidence
calc = ConfidenceCalculator()
confidence = calc.calculate(evidence_scores, {'coverage_ratio': 1.0}, results)

print(f"\nConfidence result:")
print(f"  Confidence score: {confidence['confidence_score']}")
print(f"  Base score: {confidence['base_score']}")
print(f"  Avg evidence score: {confidence['avg_evidence_score']}")
print(f"  Avg retrieval score: {confidence['avg_retrieval_score']}")
