"""
Simple Phase 2 Test
Tests one query only.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from retrieval.retrieval_pipeline import RetrievalPipeline


async def test_single_query():
    """Test with a single query."""
    
    pipeline = RetrievalPipeline()
    
    query = "Are we compliant with NAAC 3.2.1?"
    
    print("Testing Phase 2 Retrieval Pipeline")
    print(f"Query: {query}\n")
    
    try:
        results = await pipeline.run_retrieval(query, verbose=True)
        
        print(f"\n{'='*60}")
        print("SUCCESS - Retrieved {len(results)} results")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    
    pipeline.close()


if __name__ == "__main__":
    asyncio.run(test_single_query())
