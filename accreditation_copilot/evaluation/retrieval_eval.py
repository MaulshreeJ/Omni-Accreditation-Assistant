"""
Retrieval Evaluation Harness - Phase E2
Evaluates retrieval quality using standard IR metrics.
"""

import json
from typing import List, Dict, Any, Tuple
from pathlib import Path


class RetrievalEvaluator:
    """
    Evaluates retrieval quality using Recall@K, Precision@K, and F1@K metrics.
    """
    
    def __init__(self, dataset_path: str = None):
        """
        Initialize evaluator with test dataset.
        
        Args:
            dataset_path: Path to evaluation dataset JSON file
        """
        self.dataset_path = dataset_path
        self.dataset = []
        
        if dataset_path and Path(dataset_path).exists():
            self.load_dataset(dataset_path)
    
    def load_dataset(self, dataset_path: str) -> None:
        """
        Load evaluation dataset from JSON file.
        
        Dataset format:
        [
            {
                "query": "NAAC 3.2.1 research funding",
                "framework": "NAAC",
                "criterion": "3.2.1",
                "expected_chunks": ["chunk_id_1", "chunk_id_2", ...]
            },
            ...
        ]
        
        Args:
            dataset_path: Path to dataset file
        """
        with open(dataset_path, 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)
        
        print(f"✓ Loaded {len(self.dataset)} evaluation queries from {dataset_path}")
    
    def recall_at_k(self, retrieved: List[str], expected: List[str], k: int) -> float:
        """
        Calculate Recall@K.
        
        Recall@K = (# of relevant items in top-K) / (# of relevant items)
        
        Args:
            retrieved: List of retrieved chunk IDs (ordered by rank)
            expected: List of expected/relevant chunk IDs
            k: Number of top results to consider
            
        Returns:
            Recall@K score (0.0 to 1.0)
        """
        if not expected:
            return 0.0
        
        top_k = set(retrieved[:k])
        relevant = set(expected)
        
        hits = len(top_k & relevant)
        return hits / len(relevant)
    
    def precision_at_k(self, retrieved: List[str], expected: List[str], k: int) -> float:
        """
        Calculate Precision@K.
        
        Precision@K = (# of relevant items in top-K) / K
        
        Args:
            retrieved: List of retrieved chunk IDs (ordered by rank)
            expected: List of expected/relevant chunk IDs
            k: Number of top results to consider
            
        Returns:
            Precision@K score (0.0 to 1.0)
        """
        if k == 0:
            return 0.0
        
        top_k = set(retrieved[:k])
        relevant = set(expected)
        
        hits = len(top_k & relevant)
        return hits / k
    
    def f1_at_k(self, retrieved: List[str], expected: List[str], k: int) -> float:
        """
        Calculate F1@K.
        
        F1@K = 2 * (Precision@K * Recall@K) / (Precision@K + Recall@K)
        
        Args:
            retrieved: List of retrieved chunk IDs (ordered by rank)
            expected: List of expected/relevant chunk IDs
            k: Number of top results to consider
            
        Returns:
            F1@K score (0.0 to 1.0)
        """
        precision = self.precision_at_k(retrieved, expected, k)
        recall = self.recall_at_k(retrieved, expected, k)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    def evaluate_query(self, retrieved_chunks: List[str], expected_chunks: List[str],
                      k: int = 5) -> Dict[str, float]:
        """
        Evaluate a single query.
        
        Args:
            retrieved_chunks: List of retrieved chunk IDs
            expected_chunks: List of expected chunk IDs
            k: Number of top results to consider
            
        Returns:
            Dictionary with recall, precision, and F1 scores
        """
        return {
            f'recall@{k}': self.recall_at_k(retrieved_chunks, expected_chunks, k),
            f'precision@{k}': self.precision_at_k(retrieved_chunks, expected_chunks, k),
            f'f1@{k}': self.f1_at_k(retrieved_chunks, expected_chunks, k)
        }
    
    def evaluate_dataset(self, retrieval_func, k: int = 5) -> Dict[str, Any]:
        """
        Evaluate retrieval on entire dataset.
        
        Args:
            retrieval_func: Function that takes (query, framework, criterion) and returns list of chunk IDs
            k: Number of top results to consider
            
        Returns:
            Dictionary with average metrics and per-query results
        """
        if not self.dataset:
            raise ValueError("No dataset loaded. Call load_dataset() first.")
        
        results = []
        total_recall = 0.0
        total_precision = 0.0
        total_f1 = 0.0
        
        for item in self.dataset:
            query = item['query']
            framework = item.get('framework', 'NAAC')
            criterion = item.get('criterion', '')
            expected = item['expected_chunks']
            
            # Retrieve chunks
            retrieved = retrieval_func(query, framework, criterion)
            
            # Evaluate
            metrics = self.evaluate_query(retrieved, expected, k=k)
            
            results.append({
                'query': query,
                'framework': framework,
                'criterion': criterion,
                'metrics': metrics,
                'num_retrieved': len(retrieved),
                'num_expected': len(expected)
            })
            
            total_recall += metrics[f'recall@{k}']
            total_precision += metrics[f'precision@{k}']
            total_f1 += metrics[f'f1@{k}']
        
        n = len(self.dataset)
        
        return {
            'average_metrics': {
                f'recall@{k}': round(total_recall / n, 3),
                f'precision@{k}': round(total_precision / n, 3),
                f'f1@{k}': round(total_f1 / n, 3)
            },
            'num_queries': n,
            'per_query_results': results
        }
    
    def print_evaluation_report(self, results: Dict[str, Any]) -> None:
        """
        Print formatted evaluation report.
        
        Args:
            results: Results from evaluate_dataset()
        """
        print("\n" + "="*80)
        print("RETRIEVAL EVALUATION REPORT")
        print("="*80)
        
        avg_metrics = results['average_metrics']
        print(f"\nDataset: {results['num_queries']} queries")
        print(f"\nAverage Metrics:")
        for metric, value in avg_metrics.items():
            print(f"  {metric}: {value:.3f}")
        
        # Show per-query breakdown
        print(f"\nPer-Query Results:")
        for i, result in enumerate(results['per_query_results'][:5], 1):  # Show first 5
            print(f"\n  Query {i}: {result['query'][:60]}...")
            print(f"    Framework: {result['framework']}, Criterion: {result['criterion']}")
            print(f"    Retrieved: {result['num_retrieved']}, Expected: {result['num_expected']}")
            for metric, value in result['metrics'].items():
                print(f"    {metric}: {value:.3f}")
        
        if len(results['per_query_results']) > 5:
            print(f"\n  ... and {len(results['per_query_results']) - 5} more queries")
        
        print("\n" + "="*80)


# Helper function to create sample dataset
def create_sample_dataset(output_path: str = "data/retrieval_eval_dataset.json") -> None:
    """
    Create a sample evaluation dataset.
    
    Args:
        output_path: Path to save dataset
    """
    sample_dataset = [
        {
            "query": "NAAC 3.2.1 extramural research funding",
            "framework": "NAAC",
            "criterion": "3.2.1",
            "expected_chunks": [
                "fa65bb57-986a-4e7d-afd9-2556b83b56c0",  # NAAC 3.2.1 definition
            ]
        },
        {
            "query": "DST research grants and funding",
            "framework": "NAAC",
            "criterion": "3.2.1",
            "expected_chunks": [
                # Institution chunks with DST funding
            ]
        },
        {
            "query": "NBA Criterion 5 student support services",
            "framework": "NBA",
            "criterion": "C5",
            "expected_chunks": [
                # NBA C5 related chunks
            ]
        }
    ]
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_dataset, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created sample dataset: {output_path}")
    print(f"  {len(sample_dataset)} queries")
    print(f"\nNote: Update expected_chunks with actual chunk IDs from your index")
