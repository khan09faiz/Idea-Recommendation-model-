"""
FAISS Index Management Utility
Provides tools to manage, rebuild, and inspect FAISS index
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import IdeaDatabase, FAISS_AVAILABLE
import numpy as np


def check_faiss_status(db_path: str = "data/ideas.db"):
    """Check FAISS availability and index status"""
    print("\n" + "=" * 60)
    print("  FAISS INDEX STATUS")
    print("=" * 60 + "\n")
    
    print(f"FAISS Library: {'✅ Available' if FAISS_AVAILABLE else '❌ Not Installed'}")
    
    if not FAISS_AVAILABLE:
        print("\n💡 To install FAISS:")
        print("   pip install faiss-cpu")
        print("   (or 'faiss-gpu' for GPU support)")
        return
    
    # Check database
    db = IdeaDatabase(db_path, use_faiss=True)
    ideas = db.get_all_ideas()
    
    print(f"Database: {db_path}")
    print(f"Total Ideas: {len(ideas)}")
    print(f"FAISS Enabled: {'Yes' if db.use_faiss else 'No'}")
    print(f"FAISS Index Built: {'Yes' if db.faiss_index is not None else 'No'}")
    
    if db.faiss_index is not None:
        print(f"Index Dimension: {db.embedding_dim}")
        print(f"Indexed Ideas: {db.faiss_index.ntotal}")
        print(f"Index Type: {type(db.faiss_index).__name__}")
    
    # Search method being used
    if len(ideas) >= 100 and db.faiss_index is not None:
        print(f"\n🚀 Search Method: FAISS (optimized for large datasets)")
    else:
        print(f"\n📊 Search Method: Simple Cosine Similarity")
        if len(ideas) < 100:
            print(f"   (FAISS will activate at 100+ ideas)")
    
    db.close()
    print("\n" + "=" * 60 + "\n")


def rebuild_index(db_path: str = "data/ideas.db"):
    """Force rebuild FAISS index"""
    if not FAISS_AVAILABLE:
        print("❌ FAISS not available. Install with: pip install faiss-cpu")
        return
    
    print("\n🔄 Rebuilding FAISS index...")
    db = IdeaDatabase(db_path, use_faiss=True)
    db.rebuild_faiss_index()
    
    ideas = db.get_all_ideas()
    print(f"✅ Index rebuilt successfully!")
    print(f"   Total ideas: {len(ideas)}")
    if db.faiss_index:
        print(f"   Indexed: {db.faiss_index.ntotal}")
    
    db.close()


def benchmark_search(db_path: str = "data/ideas.db", query: str = "test query"):
    """Benchmark FAISS vs simple search"""
    if not FAISS_AVAILABLE:
        print("❌ FAISS not available for benchmarking")
        return
    
    print("\n" + "=" * 60)
    print("  SEARCH PERFORMANCE BENCHMARK")
    print("=" * 60 + "\n")
    
    # Test with FAISS
    import time
    from core.ollama_interface import OllamaInterface
    
    ollama = OllamaInterface()
    query_emb = ollama.generate_embedding(query)
    
    # FAISS search
    db_faiss = IdeaDatabase(db_path, use_faiss=True)
    start = time.time()
    results_faiss = db_faiss.search_similar(query_emb, top_k=10)
    time_faiss = time.time() - start
    db_faiss.close()
    
    # Simple search
    db_simple = IdeaDatabase(db_path, use_faiss=False)
    start = time.time()
    results_simple = db_simple.search_similar(query_emb, top_k=10)
    time_simple = time.time() - start
    db_simple.close()
    
    print(f"Query: '{query}'")
    print(f"\nFAISS Search:")
    print(f"  Time: {time_faiss*1000:.2f}ms")
    print(f"  Results: {len(results_faiss)}")
    
    print(f"\nSimple Search:")
    print(f"  Time: {time_simple*1000:.2f}ms")
    print(f"  Results: {len(results_simple)}")
    
    if time_faiss < time_simple:
        speedup = time_simple / time_faiss
        print(f"\n🚀 FAISS is {speedup:.2f}x faster!")
    else:
        print(f"\n📊 Simple search is faster for small datasets")
    
    print("\n" + "=" * 60 + "\n")


def show_index_info(db_path: str = "data/ideas.db"):
    """Show detailed FAISS index information"""
    if not FAISS_AVAILABLE:
        print("❌ FAISS not available")
        return
    
    import faiss
    
    db = IdeaDatabase(db_path, use_faiss=True)
    
    print("\n" + "=" * 60)
    print("  DETAILED INDEX INFORMATION")
    print("=" * 60 + "\n")
    
    if db.faiss_index is None:
        print("❌ No FAISS index built")
        print(f"   Reason: Dataset too small ({len(db.get_all_ideas())} ideas, need 100+)")
        db.close()
        return
    
    index = db.faiss_index
    
    print(f"Index Type: {type(index).__name__}")
    print(f"Dimension: {index.d}")
    print(f"Total Vectors: {index.ntotal}")
    print(f"Is Trained: {index.is_trained}")
    print(f"Metric Type: Inner Product (Cosine Similarity)")
    
    # Memory usage estimation
    memory_per_vector = index.d * 4  # 4 bytes per float32
    total_memory = memory_per_vector * index.ntotal / (1024 * 1024)  # MB
    print(f"\nMemory Usage: ~{total_memory:.2f} MB")
    
    # ID mapping
    print(f"\nID Mapping:")
    print(f"  FAISS indices: 0 to {len(db.faiss_id_map)-1}")
    print(f"  Maps to: {len(db.faiss_id_map)} idea IDs")
    
    db.close()
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FAISS Index Management")
    parser.add_argument("command", choices=["status", "rebuild", "benchmark", "info"],
                       help="Command to execute")
    parser.add_argument("--db", default="data/ideas.db", help="Database path")
    parser.add_argument("--query", default="test query", help="Query for benchmark")
    
    args = parser.parse_args()
    
    if args.command == "status":
        check_faiss_status(args.db)
    elif args.command == "rebuild":
        rebuild_index(args.db)
    elif args.command == "benchmark":
        benchmark_search(args.db, args.query)
    elif args.command == "info":
        show_index_info(args.db)
