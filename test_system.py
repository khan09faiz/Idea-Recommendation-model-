"""
Simple test script to verify the system works end-to-end
"""

from enhanced_engine import EnhancedRecommendationEngine

print("=" * 80)
print("TESTING ADYA SYSTEM")
print("=" * 80)

# Initialize
print("\n1. Initializing engine...")
engine = EnhancedRecommendationEngine(db_path="test_ideas.db", ollama_model="llama3.2:1b")
print("✅ Engine initialized")

# Add a simple idea
print("\n2. Adding a test idea...")
try:
    result = engine.add_idea_enhanced(
        title="Solar Panel Recycling Innovation",
        description="A breakthrough technology for recycling solar panels efficiently using AI-powered sorting and chemical processes. Reduces environmental impact and recovers valuable materials.",
        author="Test User",
        tags=["solar", "recycling", "sustainability", "AI"]
    )
    print(f"✅ Idea added successfully!")
    print(f"   ID: {result['idea_id']}")
    print(f"   Ethics: {result['ethics_assessment']['ethical_score']:.3f}")
    print(f"   Feasibility: {result['feasibility_analysis']['feasibility_score']:.3f}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Get recommendations
print("\n3. Getting recommendations...")
try:
    recs = engine.get_recommendations_enhanced(
        query="sustainable solar technology",
        top_k=3,
        use_causal=True,
        use_feasibility=True
    )
    
    if recs:
        print(f"✅ Got {len(recs)} recommendations")
        for rec in recs:
            print(f"\n  #{rec['rank']}: {rec['title']}")
            print(f"     Score: {rec['adjusted_final_score']:.4f}")
    else:
        print("⚠️  No recommendations (database might be empty)")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Show stats
print("\n4. System statistics...")
try:
    report = engine.generate_comprehensive_report()
    print(f"   Total Ideas: {report['base_audit']['total_ideas']}")
    print(f"   Blockchain Blocks: {report['blockchain']['summary']['total_blocks']}")
    print(f"   Chain Valid: {report['blockchain']['integrity']['valid']}")
except Exception as e:
    print(f"⚠️  Could not generate report: {e}")

print("\n" + "=" * 80)
print("✅ TEST COMPLETED")
print("=" * 80)
