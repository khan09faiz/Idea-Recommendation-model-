"""
User Feedback System - Collect ratings and update recommendations
Implements Federated Learning and Meta-Learning updates
"""

import sys
from enhanced_engine import EnhancedRecommendationEngine
from datetime import datetime

def display_banner():
    print("\n" + "="*80)
    print("  GIG - USER FEEDBACK SYSTEM")
    print("  Rate ideas and help the system learn your preferences")
    print("="*80 + "\n")

def display_ideas(ideas):
    """Display ideas in a numbered list"""
    print("\n" + "─"*80)
    print("  AVAILABLE IDEAS TO RATE")
    print("─"*80 + "\n")
    
    for i, idea in enumerate(ideas, 1):
        print(f"{i}. {idea.title}")
        print(f"   ID: {idea.idea_id}")
        print(f"   Current Elo: {idea.elo_rating:.0f}")
        print(f"   Tags: {', '.join(idea.tags[:3])}")
        print()

def get_user_rating(idea_title):
    """Get rating from user with validation"""
    print(f"\n📊 Rating for: {idea_title}")
    print("─"*80)
    
    while True:
        try:
            rating = int(input("Rate this idea (1-5 stars, 5 = best): ").strip())
            if 1 <= rating <= 5:
                return rating
            else:
                print("❌ Please enter a number between 1 and 5")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n⚠️  Feedback cancelled")
            return None

def get_comparison_preference(idea1, idea2):
    """Get user preference between two ideas"""
    print("\n" + "="*80)
    print("  COMPARE TWO IDEAS")
    print("="*80)
    print(f"\nA. {idea1.title}")
    print(f"   Tags: {', '.join(idea1.tags[:3])}")
    print(f"\nB. {idea2.title}")
    print(f"   Tags: {', '.join(idea2.tags[:3])}")
    
    while True:
        choice = input("\nWhich idea is better? (A/B/Equal): ").strip().upper()
        if choice in ['A', 'B', 'EQUAL']:
            return choice
        print("❌ Please enter A, B, or Equal")

def main():
    display_banner()
    
    # Initialize engine
    print("🚀 Loading recommendation engine...")
    engine = EnhancedRecommendationEngine()
    print(f"✅ Loaded {len(engine.db.get_all_ideas())} ideas\n")
    
    ideas = engine.db.get_all_ideas()
    
    if not ideas:
        print("❌ No ideas found in database. Add some ideas first!")
        return
    
    print("Choose feedback mode:")
    print("1. Rate individual ideas (for Elo updates)")
    print("2. Compare ideas pairwise (for preference learning)")
    print("3. Select your top 3 ideas (for meta-learning)")
    print("4. Exit")
    
    choice = input("\nYour choice (1-4): ").strip()
    
    if choice == "1":
        # Individual rating mode
        display_ideas(ideas)
        
        print(f"\n📝 Rate as many ideas as you want (or type 'done' to finish)")
        
        rated_count = 0
        for i, idea in enumerate(ideas, 1):
            rate_choice = input(f"\nRate idea #{i}? (y/n/done): ").strip().lower()
            
            if rate_choice == 'done':
                break
            elif rate_choice != 'y':
                continue
            
            rating = get_user_rating(idea.title)
            if rating is None:
                break
            
            # Calculate Elo adjustment based on rating
            # 5 stars = +32, 4 stars = +16, 3 stars = 0, 2 stars = -16, 1 star = -32
            elo_change = (rating - 3) * 16
            
            old_elo = idea.elo_rating
            new_elo = max(800, min(2200, idea.elo_rating + elo_change))  # Clamp between 800-2200
            
            # Update Elo in database manually
            import sqlite3
            conn = sqlite3.connect(engine.db.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE ideas SET elo_rating = ? WHERE idea_id = ?", 
                          (new_elo, idea.idea_id))
            conn.commit()
            conn.close()
            
            idea.elo_rating = new_elo  # Update object too
            print(f"   ✅ Updated Elo: {old_elo:.0f} → {new_elo:.0f} ({elo_change:+.0f})")
            
            # Add to federated learning
            feedback_data = {
                "idea_id": idea.idea_id,
                "rating": rating,
                "timestamp": datetime.now().isoformat()
            }
            engine.federated_feedback.add_local_feedback(feedback_data)
            
            rated_count += 1
        
        if rated_count > 0:
            # Aggregate federated learning
            print(f"\n🤝 Aggregating {rated_count} ratings...")
            global_model = engine.federated_feedback.aggregate_updates()
            print(f"✅ Federated learning updated! Total rounds: {len(engine.federated_feedback.update_history)}")
        
        print(f"\n✅ Rated {rated_count} ideas successfully!")
    
    elif choice == "2":
        # Pairwise comparison mode
        print("\n📊 Pairwise Comparison Mode")
        print("   We'll show you pairs of ideas. Choose which is better.\n")
        
        if len(ideas) < 2:
            print("❌ Need at least 2 ideas for comparison")
            return
        
        comparisons = 0
        max_comparisons = min(5, len(ideas) * (len(ideas) - 1) // 4)
        
        import random
        for _ in range(max_comparisons):
            idea1, idea2 = random.sample(ideas, 2)
            
            preference = get_comparison_preference(idea1, idea2)
            
            # Update Elo based on comparison using standard Elo formula
            K = 32  # K-factor
            expected_a = 1 / (1 + 10 ** ((idea2.elo_rating - idea1.elo_rating) / 400))
            expected_b = 1 / (1 + 10 ** ((idea1.elo_rating - idea2.elo_rating) / 400))
            
            if preference == 'A':
                score_a, score_b = 1.0, 0.0
            elif preference == 'B':
                score_a, score_b = 0.0, 1.0
            else:  # Equal
                score_a, score_b = 0.5, 0.5
            
            new_elo1 = idea1.elo_rating + K * (score_a - expected_a)
            new_elo2 = idea2.elo_rating + K * (score_b - expected_b)
            
            # Update in database
            import sqlite3
            conn = sqlite3.connect(engine.db.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE ideas SET elo_rating = ? WHERE idea_id = ?", 
                          (new_elo1, idea1.idea_id))
            cursor.execute("UPDATE ideas SET elo_rating = ? WHERE idea_id = ?", 
                          (new_elo2, idea2.idea_id))
            conn.commit()
            conn.close()
            
            print(f"\n✅ Updated Elos:")
            print(f"   {idea1.title}: {idea1.elo_rating:.0f} → {new_elo1:.0f}")
            print(f"   {idea2.title}: {idea2.elo_rating:.0f} → {new_elo2:.0f}")
            
            # Add to federated learning
            feedback_data = {
                "idea1_id": idea1.idea_id,
                "idea2_id": idea2.idea_id,
                "preference": preference,
                "timestamp": datetime.now().isoformat()
            }
            engine.federated_feedback.add_local_feedback(feedback_data)
            
            comparisons += 1
            
            if comparisons < max_comparisons:
                continue_choice = input("\nContinue comparing? (y/n): ").strip().lower()
                if continue_choice != 'y':
                    break
        
        if comparisons > 0:
            print(f"\n🤝 Aggregating {comparisons} comparisons...")
            global_model = engine.federated_feedback.aggregate_updates()
            print(f"✅ Federated learning updated! Total rounds: {len(engine.federated_feedback.update_history)}")
        
        print(f"\n✅ Completed {comparisons} comparisons!")
    
    elif choice == "3":
        # Meta-learning mode - select top ideas
        display_ideas(ideas)
        
        print("\n🎯 Meta-Learning: Select Your Top 3 Ideas")
        print("   Enter the numbers of your 3 favorite ideas (e.g., 1 3 5)")
        
        while True:
            try:
                selections = input("\nYour top 3 (space-separated numbers): ").strip().split()
                if len(selections) != 3:
                    print("❌ Please enter exactly 3 numbers")
                    continue
                
                indices = [int(s) - 1 for s in selections]
                if all(0 <= i < len(ideas) for i in indices):
                    top_ideas = [ideas[i] for i in indices]
                    break
                else:
                    print(f"❌ Numbers must be between 1 and {len(ideas)}")
            except ValueError:
                print("❌ Please enter valid numbers")
        
        print("\n🎯 Running meta-learning optimization...")
        
        # Create ground truth labels (top ideas = 1.0, others = 0.0)
        ground_truth = {}
        for idea in ideas:
            ground_truth[idea.idea_id] = 1.0 if idea in top_ideas else 0.0
        
        # Run meta-learning optimization
        initial_params = {
            "elo_weight": 0.15,
            "sentiment_weight": 0.10,
            "trend_weight": 0.12,
            "provenance_weight": 0.08,
            "freshness_weight": 0.10
        }
        
        optimized_params = engine.meta_learning.optimize_hyperparameters(
            ideas, ground_truth, initial_params
        )
        
        print("\n✅ Meta-learning completed!")
        print("\n📊 Optimized Parameters:")
        for param, value in optimized_params.items():
            initial = initial_params.get(param, 0.0)
            change = ((value - initial) / initial * 100) if initial > 0 else 0
            print(f"   {param}: {initial:.3f} → {value:.3f} ({change:+.1f}%)")
        
        print(f"\n✅ Meta-learning runs: {len(engine.meta_learning.optimization_history)}")
        print(f"   Best nDCG: {engine.meta_learning.best_metric:.4f}")
        
        # Update engine weights
        print("\n💡 You can now use these optimized weights in future recommendations!")
    
    else:
        print("\n👋 Exiting feedback system")
        return
    
    # Show updated statistics
    print("\n" + "="*80)
    print("  LEARNING STATISTICS")
    print("="*80)
    print(f"\n🤝 Federated Learning:")
    print(f"   Update Rounds: {len(engine.federated_feedback.update_history)}")
    print(f"   Total Feedback: {len(engine.federated_feedback.local_updates)}")
    
    print(f"\n🎯 Meta-Learning:")
    print(f"   Optimization Runs: {len(engine.meta_learning.optimization_history)}")
    if engine.meta_learning.best_metric > -float('inf'):
        print(f"   Best nDCG: {engine.meta_learning.best_metric:.4f}")
    
    print("\n✅ Your feedback has been recorded and the system has learned!")
    print("   Future recommendations will be more personalized.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Feedback cancelled by user")
        sys.exit(0)
