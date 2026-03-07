"""
Test Feedback Store - Phase E3
Tests the reviewer feedback storage system.
"""

import sys
from pathlib import Path

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent))

from feedback.feedback_store import FeedbackStore, add_batch_feedback


def test_feedback_store():
    """Test feedback store functionality."""
    print("="*80)
    print("FEEDBACK STORE TEST")
    print("="*80)
    
    # Create test feedback store
    test_db = "data/test_feedback.db"
    store = FeedbackStore(test_db)
    
    # Clear any existing data
    store.clear_all()
    
    print("\n1. Testing add_feedback()...")
    
    # Add sample feedback
    feedback_id_1 = store.add_feedback(
        query="NAAC 3.2.1 research funding",
        framework="NAAC",
        criterion="3.2.1",
        chunk_id="fa65bb57-986a-4e7d-afd9-2556b83b56c0",
        rating="relevant",
        reviewer_id="reviewer-1",
        comment="Exact criterion definition - highly relevant"
    )
    
    feedback_id_2 = store.add_feedback(
        query="NAAC 3.2.1 research funding",
        framework="NAAC",
        criterion="3.2.1",
        chunk_id="3de8ab0e-da23-4b8f-aad2-8b288b693ebe",
        rating="relevant",
        reviewer_id="reviewer-1",
        comment="Institution evidence with DST funding"
    )
    
    feedback_id_3 = store.add_feedback(
        query="NAAC 3.2.1 research funding",
        framework="NAAC",
        criterion="3.2.1",
        chunk_id="irrelevant-chunk-123",
        rating="irrelevant",
        reviewer_id="reviewer-1",
        comment="Not related to research funding"
    )
    
    print(f"✓ Added 3 feedback records (IDs: {feedback_id_1}, {feedback_id_2}, {feedback_id_3})")
    
    print("\n2. Testing get_feedback_for_query()...")
    query_feedback = store.get_feedback_for_query("NAAC 3.2.1 research funding")
    print(f"✓ Retrieved {len(query_feedback)} feedback records for query")
    
    print("\n3. Testing get_feedback_for_chunk()...")
    chunk_feedback = store.get_feedback_for_chunk("fa65bb57-986a-4e7d-afd9-2556b83b56c0")
    print(f"✓ Retrieved {len(chunk_feedback)} feedback records for chunk")
    
    print("\n4. Testing get_feedback_by_rating()...")
    relevant_feedback = store.get_feedback_by_rating("relevant")
    irrelevant_feedback = store.get_feedback_by_rating("irrelevant")
    print(f"✓ Relevant: {len(relevant_feedback)}, Irrelevant: {len(irrelevant_feedback)}")
    
    print("\n5. Testing get_feedback_stats()...")
    stats = store.get_feedback_stats()
    print(f"✓ Total feedback: {stats['total_feedback']}")
    print(f"  By rating: {stats['by_rating']}")
    print(f"  By framework: {stats['by_framework']}")
    
    print("\n6. Testing add_batch_feedback()...")
    batch_feedback = [
        {
            "query": "NBA C5 student support",
            "framework": "NBA",
            "criterion": "C5",
            "chunk_id": "nba-chunk-1",
            "rating": "relevant",
            "reviewer_id": "reviewer-2",
            "comment": "Good NBA example"
        },
        {
            "query": "NBA C5 student support",
            "framework": "NBA",
            "criterion": "C5",
            "chunk_id": "nba-chunk-2",
            "rating": "missing",
            "reviewer_id": "reviewer-2",
            "comment": "Expected chunk not retrieved"
        }
    ]
    
    added = add_batch_feedback(store, batch_feedback)
    print(f"✓ Added {added} feedback records in batch")
    
    print("\n7. Testing export_feedback()...")
    export_path = "data/feedback_export.json"
    store.export_feedback(export_path)
    
    # Final stats
    final_stats = store.get_feedback_stats()
    
    print("\n" + "="*80)
    print("FEEDBACK STORE TEST SUMMARY")
    print("="*80)
    print(f"Total feedback records: {final_stats['total_feedback']}")
    print(f"By rating:")
    for rating, count in final_stats['by_rating'].items():
        print(f"  {rating}: {count}")
    print(f"\nBy framework:")
    for framework, count in final_stats['by_framework'].items():
        print(f"  {framework}: {count}")
    
    print("\n✓ All feedback store tests passed")
    
    # Cleanup
    store.close()
    
    return True


if __name__ == '__main__':
    success = test_feedback_store()
    sys.exit(0 if success else 1)
