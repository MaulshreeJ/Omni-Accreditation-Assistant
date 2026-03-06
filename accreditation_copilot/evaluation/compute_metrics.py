"""
Retrieval Metrics Evaluation Script
Computes Precision@k, Recall@k, F1 Score, and MRR using the existing retrieval pipeline.

Usage:
    python evaluation/compute_metrics.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from retrieval.dual_retrieval import DualRetriever
from retrieval.query_expander import QueryExpander
from models.model_manager import get_model_manager


# Evaluation queries with ground truth relevance
EVAL_QUERIES = [
    {
        "query": "extramural funding for research",
        "framework": "NAAC",
        "query_type": "metric",
        "relevant_keywords": ["funding", "extramural", "research", "grant", "project", "amount"]
    },
    {
        "query": "research publications and journals",
        "framework": "NAAC",
        "query_type": "metric",
        "relevant_keywords": ["publication", "journal", "scopus", "research", "paper", "article"]
    },
    {
        "query": "faculty qualifications and credentials",
        "framework": "NAAC",
        "query_type": "metric",
        "relevant_keywords": ["faculty", "qualification", "phd", "professor", "credential", "degree"]
    },
    {
        "query": "student support services and facilities",
        "framework": "NAAC",
        "query_type": "metric",
        "relevant_keywords": ["student", "support", "service", "facility", "welfare", "assistance"]
    },
    {
        "query": "infrastructure and learning resources",
        "framework": "NAAC",
        "query_type": "metric",
        "relevant_keywords": ["infrastructure", "library", "laboratory", "resource", "facility", "equipment"]
    },
    {
        "query": "curriculum design and development",
        "framework": "NAAC",
        "query_type": "metric",
        "relevant_keywords": ["curriculum", "syllabus", "course", "program", "design", "development"]
    },
    {
        "query": "student performance and outcomes",
        "framework": "NAAC",
        "query_type": "metric",
        "relevant_keywords": ["student", "performance", "result", "outcome", "achievement", "pass"]
    },
    {
        "query": "quality assurance mechanisms",
        "framework": "NAAC",
        "query_type": "policy",
        "relevant_keywords": ["quality", "assurance", "iqac", "mechanism", "monitoring", "evaluation"]
    }
]


def compute_metrics(top_k=5):
    """
    Compute retrieval metrics using the existing pipeline.
    
    Args:
        top_k: Number of top results to consider
        
    Returns:
        Dictionary with computed metrics
    """
    print("\n" + "="*80)
    print("RETRIEVAL METRICS EVALUATION")
    print("="*80)
    print(f"\nInitializing retrieval pipeline...")
    
    # Initialize components
    model_manager = get_model_manager()
    dual_retriever = DualRetriever(model_manager=model_manager)
    query_expander = QueryExpander()
    
    print(f"✓ Pipeline initialized")
    print(f"✓ Evaluating {len(EVAL_QUERIES)} queries with top_k={top_k}")
    
    # Metrics storage
    precisions = []
    recalls = []
    f1_scores = []
    reciprocal_ranks = []
    
    print("\n" + "-"*80)
    print("Processing queries...")
    print("-"*80)
    
    for idx, item in enumerate(EVAL_QUERIES, 1):
        query = item["query"]
        framework = item["framework"]
        query_type = item["query_type"]
        relevant_keywords = item["relevant_keywords"]
        
        print(f"\n[{idx}/{len(EVAL_QUERIES)}] Query: {query}")
        print(f"     Framework: {framework}, Type: {query_type}")
        
        # Expand query
        query_variants = query_expander.expand_query(query, framework)
        
        # Retrieve using dual retrieval
        results, _ = dual_retriever.retrieve(
            query=query,
            query_variants=query_variants,
            framework=framework,
            query_type=query_type,
            top_k_framework=3,
            top_k_institution=7
        )
        
        # Extract retrieved texts (lowercase for matching)
        retrieved_texts = []
        for r in results[:top_k]:
            text = r.get('text', '').lower()
            if not text:
                # Fallback: try to get text from child_text
                text = r.get('child_text', '').lower()
            retrieved_texts.append(text)
        
        # Count relevant chunks found
        relevant_found = 0
        first_relevant_rank = None
        
        for rank, text in enumerate(retrieved_texts, start=1):
            # Check if any relevant keyword appears in the text
            if any(keyword.lower() in text for keyword in relevant_keywords):
                relevant_found += 1
                if first_relevant_rank is None:
                    first_relevant_rank = rank
        
        # Compute metrics for this query
        precision = relevant_found / top_k if top_k > 0 else 0.0
        recall = relevant_found / len(relevant_keywords) if len(relevant_keywords) > 0 else 0.0
        
        if precision + recall > 0:
            f1 = 2 * precision * recall / (precision + recall)
        else:
            f1 = 0.0
        
        if first_relevant_rank:
            reciprocal_rank = 1.0 / first_relevant_rank
        else:
            reciprocal_rank = 0.0
        
        # Store metrics
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1)
        reciprocal_ranks.append(reciprocal_rank)
        
        # Print per-query results
        print(f"     Retrieved: {len(results[:top_k])} chunks")
        print(f"     Relevant found: {relevant_found}/{len(relevant_keywords)}")
        print(f"     Precision@{top_k}: {precision:.3f}")
        print(f"     Recall@{top_k}: {recall:.3f}")
        print(f"     F1@{top_k}: {f1:.3f}")
        print(f"     MRR: {reciprocal_rank:.3f}")
    
    # Compute average metrics
    avg_precision = sum(precisions) / len(precisions) if precisions else 0.0
    avg_recall = sum(recalls) / len(recalls) if recalls else 0.0
    avg_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0
    avg_mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
    
    # Cleanup
    dual_retriever.close()
    
    return {
        'precision': avg_precision,
        'recall': avg_recall,
        'f1': avg_f1,
        'mrr': avg_mrr,
        'num_queries': len(EVAL_QUERIES),
        'top_k': top_k
    }


def print_final_metrics(metrics):
    """
    Print final metrics in screenshot-friendly format.
    
    Args:
        metrics: Dictionary with computed metrics
    """
    print("\n" + "="*80)
    print("RETRIEVAL EVALUATION RESULTS")
    print("="*80)
    
    print(f"\nDataset: {metrics['num_queries']} queries")
    print(f"Top-K: {metrics['top_k']}")
    
    print("\n" + "-"*80)
    print("AVERAGE METRICS")
    print("-"*80)
    
    print(f"\nPrecision@{metrics['top_k']} : {metrics['precision']:.3f}")
    print(f"Recall@{metrics['top_k']}    : {metrics['recall']:.3f}")
    print(f"F1 Score@{metrics['top_k']}  : {metrics['f1']:.3f}")
    print(f"MRR            : {metrics['mrr']:.3f}")
    
    print("\n" + "="*80)
    print("METRICS SUMMARY (Screenshot-Friendly)")
    print("="*80)
    
    print(f"""
╔════════════════════════════════════════╗
║       RETRIEVAL METRICS RESULTS        ║
╠════════════════════════════════════════╣
║  Precision@{metrics['top_k']} : {metrics['precision']:.3f}                  ║
║  Recall@{metrics['top_k']}    : {metrics['recall']:.3f}                  ║
║  F1 Score@{metrics['top_k']}  : {metrics['f1']:.3f}                  ║
║  MRR          : {metrics['mrr']:.3f}                  ║
╠════════════════════════════════════════╣
║  Queries      : {metrics['num_queries']:<3}                        ║
║  Top-K        : {metrics['top_k']:<3}                        ║
╚════════════════════════════════════════╝
""")
    
    print("="*80)
    
    # Interpretation
    print("\nMETRICS INTERPRETATION:")
    print("-"*80)
    
    if metrics['precision'] >= 0.7:
        print("✓ Precision: GOOD - Most retrieved results are relevant")
    elif metrics['precision'] >= 0.5:
        print("○ Precision: FAIR - About half of retrieved results are relevant")
    else:
        print("✗ Precision: NEEDS IMPROVEMENT - Many irrelevant results retrieved")
    
    if metrics['recall'] >= 0.7:
        print("✓ Recall: GOOD - Most relevant documents are retrieved")
    elif metrics['recall'] >= 0.5:
        print("○ Recall: FAIR - About half of relevant documents are retrieved")
    else:
        print("✗ Recall: NEEDS IMPROVEMENT - Many relevant documents are missed")
    
    if metrics['f1'] >= 0.7:
        print("✓ F1 Score: GOOD - Balanced precision and recall")
    elif metrics['f1'] >= 0.5:
        print("○ F1 Score: FAIR - Moderate balance between precision and recall")
    else:
        print("✗ F1 Score: NEEDS IMPROVEMENT - Poor balance between precision and recall")
    
    if metrics['mrr'] >= 0.7:
        print("✓ MRR: GOOD - Relevant results appear early in rankings")
    elif metrics['mrr'] >= 0.5:
        print("○ MRR: FAIR - Relevant results appear in middle of rankings")
    else:
        print("✗ MRR: NEEDS IMPROVEMENT - Relevant results appear late in rankings")
    
    print("\n" + "="*80)


def main():
    """Main execution function."""
    try:
        # Compute metrics
        metrics = compute_metrics(top_k=5)
        
        # Print results
        print_final_metrics(metrics)
        
        print("\n✓ Evaluation complete!")
        print("\nNote: This evaluation uses keyword-based relevance matching.")
        print("For production use, consider creating a labeled dataset with")
        print("explicit chunk IDs for more accurate evaluation.")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
