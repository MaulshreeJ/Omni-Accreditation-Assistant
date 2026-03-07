"""
LangSmith Trace Logging - Phase E1
Instruments the pipeline with tracing for observability.
"""

import os
import time
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from the accreditation_copilot directory
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed

# Try to import LangSmith, but make it optional
try:
    from langsmith import Client, traceable
    from langsmith.run_helpers import get_current_run_tree
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    traceable = lambda func: func  # No-op decorator if LangSmith not available


class TraceManager:
    """
    Manages tracing for the accreditation copilot pipeline.
    
    Captures:
    - Query and expanded queries
    - Retrieved chunks and scores
    - Reranker scores and final rankings
    - Dimension hits and evidence scores
    - Confidence scores
    - LLM prompts and outputs
    - Latency per stage
    """
    
    def __init__(self, project_name: str = "accreditation-copilot"):
        """
        Initialize trace manager.
        
        Args:
            project_name: LangSmith project name
        """
        self.project_name = project_name
        
        # Check for API key
        api_key = os.getenv("LANGCHAIN_API_KEY")
        tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
        
        self.enabled = LANGSMITH_AVAILABLE and api_key is not None and tracing_enabled
        
        if self.enabled:
            self.client = Client()
            print(f"✓ LangSmith tracing enabled")
            print(f"  Project: {project_name}")
            print(f"  API Key: {api_key[:20]}..." if api_key else "  API Key: Not set")
        else:
            self.client = None
            if not LANGSMITH_AVAILABLE:
                print("⚠ LangSmith not installed. Install with: pip install langsmith")
            elif not api_key:
                print("⚠ LangSmith tracing disabled (LANGCHAIN_API_KEY not set)")
            elif not tracing_enabled:
                print("⚠ LangSmith tracing disabled (LANGCHAIN_TRACING_V2 not set to true)")
            else:
                print("⚠ LangSmith tracing disabled")
    
    @contextmanager
    def trace_stage(self, stage_name: str, **metadata):
        """
        Context manager for tracing a pipeline stage.
        
        Args:
            stage_name: Name of the stage (e.g., "retrieval", "reranking")
            **metadata: Additional metadata to log
            
        Yields:
            Dict to store stage outputs
        """
        start_time = time.time()
        outputs = {}
        
        try:
            yield outputs
        finally:
            elapsed = time.time() - start_time
            outputs['latency_ms'] = round(elapsed * 1000, 2)
            
            # Log to console if tracing disabled
            if not self.enabled:
                print(f"  [{stage_name}] {elapsed:.3f}s")
    
    def log_query_run(self, query: str, framework: str, criterion: str, 
                     run_data: Dict[str, Any]) -> None:
        """
        Log a complete query run with all stages.
        
        Args:
            query: Original query
            framework: NAAC or NBA
            criterion: Criterion ID
            run_data: Dictionary containing all stage outputs
        """
        if not self.enabled:
            return
        
        # Log summary
        print(f"\n✓ Trace logged to LangSmith (project: {self.project_name})")
        print(f"  Query: {query}")
        print(f"  Framework: {framework}, Criterion: {criterion}")
        print(f"  Total latency: {run_data.get('total_latency_ms', 0):.0f}ms")


# Global trace manager instance
_trace_manager = None


def get_trace_manager() -> TraceManager:
    """Get or create global trace manager."""
    global _trace_manager
    if _trace_manager is None:
        _trace_manager = TraceManager()
    return _trace_manager


def enable_tracing(project_name: str = "accreditation-copilot"):
    """
    Enable tracing for the pipeline.
    
    Args:
        project_name: LangSmith project name
    """
    global _trace_manager
    _trace_manager = TraceManager(project_name=project_name)


def disable_tracing():
    """Disable tracing."""
    global _trace_manager
    if _trace_manager:
        _trace_manager.enabled = False


@traceable(name="query_execution")
def trace_query_execution(query: str, framework: str, criterion: str, 
                         execution_func, **kwargs) -> Any:
    """
    Trace a complete query execution.
    
    Args:
        query: Original query
        framework: NAAC or NBA
        criterion: Criterion ID
        execution_func: Function to execute
        **kwargs: Additional arguments for execution_func
        
    Returns:
        Result from execution_func
    """
    tracer = get_trace_manager()
    
    if not tracer.enabled:
        # Just execute without tracing
        return execution_func(query=query, framework=framework, 
                            criterion=criterion, **kwargs)
    
    # Execute with tracing
    start_time = time.time()
    result = execution_func(query=query, framework=framework, 
                          criterion=criterion, **kwargs)
    total_latency = time.time() - start_time
    
    # Log trace
    run_data = {
        'query': query,
        'framework': framework,
        'criterion': criterion,
        'total_latency_ms': round(total_latency * 1000, 2),
        'result': result
    }
    
    tracer.log_query_run(query, framework, criterion, run_data)
    
    return result


@traceable(name="retrieval")
def trace_retrieval(query: str, query_variants: List[str], 
                   retrieved_chunks: List[Dict]) -> Dict[str, Any]:
    """
    Trace retrieval stage.
    
    Args:
        query: Original query
        query_variants: Expanded query variants
        retrieved_chunks: Retrieved chunks with scores
        
    Returns:
        Trace data
    """
    return {
        'query': query,
        'query_variants': query_variants,
        'num_chunks': len(retrieved_chunks),
        'chunk_ids': [c.get('chunk_id') for c in retrieved_chunks],
        'scores': [c.get('fused_score', 0) for c in retrieved_chunks]
    }


@traceable(name="reranking")
def trace_reranking(chunks: List[Dict], reranked_chunks: List[Dict]) -> Dict[str, Any]:
    """
    Trace reranking stage.
    
    Args:
        chunks: Input chunks
        reranked_chunks: Reranked chunks with scores
        
    Returns:
        Trace data
    """
    return {
        'num_input': len(chunks),
        'num_output': len(reranked_chunks),
        'reranker_scores': [c.get('reranker_score', 0) for c in reranked_chunks],
        'final_scores': [c.get('final_score', 0) for c in reranked_chunks],
        'top_chunk_ids': [c.get('chunk_id') for c in reranked_chunks[:5]]
    }


@traceable(name="scoring")
def trace_scoring(dimension_coverage: Dict, evidence_scores: List[Dict],
                 confidence_score: float) -> Dict[str, Any]:
    """
    Trace scoring stage.
    
    Args:
        dimension_coverage: Dimension coverage analysis
        evidence_scores: Evidence scores per chunk
        confidence_score: Final confidence score
        
    Returns:
        Trace data
    """
    return {
        'coverage_ratio': dimension_coverage.get('coverage_ratio', 0),
        'dimensions_covered': dimension_coverage.get('dimensions_covered', []),
        'dimensions_missing': dimension_coverage.get('dimensions_missing', []),
        'num_evidence_chunks': len(evidence_scores),
        'confidence_score': confidence_score
    }


@traceable(name="llm_synthesis")
def trace_llm_synthesis(prompt: str, output: str, model: str) -> Dict[str, Any]:
    """
    Trace LLM synthesis stage.
    
    Args:
        prompt: LLM prompt
        output: LLM output
        model: Model name
        
    Returns:
        Trace data
    """
    return {
        'model': model,
        'prompt_length': len(prompt),
        'output_length': len(output),
        'prompt_preview': prompt[:200] + '...' if len(prompt) > 200 else prompt,
        'output_preview': output[:200] + '...' if len(output) > 200 else output
    }
