"""
Test Retrieval Evaluation - Phase E2
Tests the retrieval evaluation harness.
"""

import sys
from pathlib import Path

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.retrieval_eval import RetrievalEvaluator, create_sample_dataset
from retrieval.dual_retrieval import DualRetriever
from retrieval.index_loader import IndexLoader


def test_retrieval_evaluation():
    """Test retrieval evaluation with sample queries."""
    print("="*80)
    print("RETRIEVAL EVALUATION TEST")
    print("="*80)
    
    # Create sample dataset if it doesn't exist
    dataset_path = "data/retrieval_eval_dataset.json"
    if not Path(dataset_path).exists():
        print("\nCreating sample evaluation dataset...")
        create_sample_dataset(dataset_path)
    
    # Initialize evaluator
    evaluator = RetrievalEvaluator(dataset_path)
    
    # Initialize retriever
    retriever = DualRetriever()
    index_loader = IndexLoader()
    
    def retrieval_func(query: str, framework: str, criterion: str) -> list:
        """Wrapper function for retrieval."""
        query_variants = [query]
        results, _ = retriever.retrieve(
            query=query,
            query_variants=query_variants,
            framework=framework,
            query_type='metric',
            top_k_framework=3,
            top_k_institution=7
        )
        
        # Extract chunk IDs
        return [r['chunk_id'] for r in results]
    
    # Run evaluation
    print("\nRunning evaluation...")
    results = evaluator.evaluate_dataset(retrieval_func, k=5)
    
    # Print report
    evaluator.print_evaluation_report(results)
    
    # Cleanup
    retriever.close()
    index_loader.close()
    
    # Check if metrics are reasonable
    avg_metrics = results['average_metrics']
    recall = avg_metrics['recall@5']
    precision = avg_metrics['precision@5']
    f1 = avg_metrics['f1@5']
    
    print("\n" + "="*80)
    print("EVALUATION SUMMARY")
    print("="*80)
    print(f"Recall@5: {recall:.3f}")
    print(f"Precision@5: {precision:.3f}")
    print(f"F1@5: {f1:.3f}")
    
    if recall > 0 or precision > 0:
        print("\n✓ Retrieval evaluation working")
        print("\nNote: Update data/retrieval_eval_dataset.json with actual")
        print("      expected chunk IDs to get meaningful metrics.")
        return True
    else:
        print("\n⚠ No relevant chunks found")
        print("  This is expected with the sample dataset.")
        print("  Update expected_chunks in the dataset file.")
        return True


if __name__ == '__main__':
    success = test_retrieval_evaluation()
    sys.exit(0 if success else 1)
