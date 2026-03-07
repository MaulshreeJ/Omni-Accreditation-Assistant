"""
Phase E Tracing Demonstration
Shows LangSmith tracing in action with a sample query.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from observability.tracer import get_trace_manager, trace_retrieval, trace_reranking, trace_scoring


def demo_tracing():
    """Demonstrate Phase E tracing capabilities."""
    
    print("="*80)
    print("PHASE E TRACING DEMONSTRATION")
    print("="*80)
    
    # Initialize trace manager
    tracer = get_trace_manager()
    
    print(f"\n✓ Trace Manager Status:")
    print(f"  Tracing enabled: {tracer.enabled}")
    print(f"  Project: {tracer.project_name}")
    
    if tracer.enabled:
        print(f"  LangSmith API: Connected")
        print(f"  Traces will be sent to LangSmith dashboard")
    else:
        print(f"  LangSmith API: Not configured (graceful degradation)")
        print(f"  Traces will be logged to console only")
    
    # Simulate a query execution with tracing
    print("\n" + "="*80)
    print("SIMULATING QUERY EXECUTION WITH TRACING")
    print("="*80)
    
    query = "NAAC 3.2.1 research funding from DST"
    framework = "NAAC"
    criterion = "3.2.1"
    
    print(f"\nQuery: {query}")
    print(f"Framework: {framework}")
    print(f"Criterion: {criterion}")
    
    # Stage 1: Retrieval
    print("\n[Stage 1: Retrieval]")
    with tracer.trace_stage("retrieval", query=query) as outputs:
        # Simulate retrieval
        query_variants = [
            query,
            "DST research funding NAAC 3.2.1",
            "research grants from Department of Science and Technology"
        ]
        
        retrieved_chunks = [
            {"chunk_id": "inst-001", "text": "DST funded AI research...", "fused_score": 0.92},
            {"chunk_id": "inst-002", "text": "SERB grant for ML...", "fused_score": 0.88},
            {"chunk_id": "fw-naac-321", "text": "NAAC 3.2.1 definition...", "fused_score": 0.85},
        ]
        
        outputs['query_variants'] = query_variants
        outputs['num_chunks'] = len(retrieved_chunks)
        outputs['chunk_ids'] = [c['chunk_id'] for c in retrieved_chunks]
        
        # Use trace function
        trace_data = trace_retrieval(query, query_variants, retrieved_chunks)
        
        print(f"  Retrieved: {len(retrieved_chunks)} chunks")
        print(f"  Query variants: {len(query_variants)}")
    
    # Stage 2: Reranking
    print("\n[Stage 2: Reranking]")
    with tracer.trace_stage("reranking") as outputs:
        # Simulate reranking with evidence weights
        reranked_chunks = [
            {"chunk_id": "inst-001", "reranker_score": 0.95, "evidence_weight": 3.0, "final_score": 2.85},
            {"chunk_id": "inst-002", "reranker_score": 0.90, "evidence_weight": 3.0, "final_score": 2.70},
            {"chunk_id": "fw-naac-321", "reranker_score": 0.88, "evidence_weight": 0.6, "final_score": 0.53},
        ]
        
        outputs['num_reranked'] = len(reranked_chunks)
        outputs['top_chunk'] = reranked_chunks[0]['chunk_id']
        
        # Use trace function
        trace_data = trace_reranking(retrieved_chunks, reranked_chunks)
        
        print(f"  Reranked: {len(reranked_chunks)} chunks")
        print(f"  Top chunk: {reranked_chunks[0]['chunk_id']}")
        print(f"  Evidence weights applied: institution=3.0x, framework=0.6x")
    
    # Stage 3: Scoring
    print("\n[Stage 3: Scoring]")
    with tracer.trace_stage("scoring") as outputs:
        # Simulate scoring
        dimension_coverage = {
            "coverage_ratio": 0.85,
            "dimensions_covered": ["funding_amount", "funding_agency", "research_area"],
            "dimensions_missing": ["duration"]
        }
        
        evidence_scores = [
            {"chunk_id": "inst-001", "score": 0.92},
            {"chunk_id": "inst-002", "score": 0.88}
        ]
        
        confidence_score = 0.87
        
        outputs['coverage_ratio'] = dimension_coverage['coverage_ratio']
        outputs['confidence'] = confidence_score
        
        # Use trace function
        trace_data = trace_scoring(dimension_coverage, evidence_scores, confidence_score)
        
        print(f"  Coverage: {dimension_coverage['coverage_ratio']:.1%}")
        print(f"  Confidence: {confidence_score:.2f}")
        print(f"  Evidence chunks: {len(evidence_scores)}")
    
    # Stage 4: LLM Synthesis
    print("\n[Stage 4: LLM Synthesis]")
    with tracer.trace_stage("llm_synthesis") as outputs:
        # Simulate LLM call
        prompt = f"Analyze compliance for {criterion}..."
        llm_output = "The institution demonstrates strong compliance..."
        
        outputs['prompt_length'] = len(prompt)
        outputs['output_length'] = len(llm_output)
        
        print(f"  Prompt: {len(prompt)} chars")
        print(f"  Output: {len(llm_output)} chars")
    
    # Summary
    print("\n" + "="*80)
    print("TRACING SUMMARY")
    print("="*80)
    
    if tracer.enabled:
        print("\n✓ Traces sent to LangSmith successfully")
        print(f"  View traces at: https://smith.langchain.com/")
        print(f"  Project: {tracer.project_name}")
    else:
        print("\n✓ Tracing completed (console mode)")
        print("  To enable LangSmith:")
        print("    1. Set LANGCHAIN_API_KEY in .env")
        print("    2. Set LANGCHAIN_TRACING_V2=true")
        print("    3. Install: pip install langsmith")
    
    print("\n✓ All stages traced successfully")
    print("  • Retrieval: Query expansion + chunk retrieval")
    print("  • Reranking: Evidence weight application")
    print("  • Scoring: Dimension coverage + confidence")
    print("  • LLM Synthesis: Prompt + output generation")


if __name__ == '__main__':
    demo_tracing()
