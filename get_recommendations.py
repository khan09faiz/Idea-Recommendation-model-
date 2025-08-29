#!/usr/bin/env python3
"""
Simple script to get recommendations by providing your prompt
"""

import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import RecommendRequest
from src.app import hybrid_recommend

def get_my_recommendations():
    """Get personalized recommendations based on your prompt"""
    
    print("🧠 Creative Idea Recommendation System")
    print("=" * 50)
    print("� Get AI-powered recommendations for your next big idea!")
    print()
    
    # Get user prompt
    my_prompt = input("💭 Enter your idea request: ").strip()
    if not my_prompt:
        my_prompt = "AI tools for small business automation"
        print(f"   Using default: '{my_prompt}'")
    
    # Get tags with proper input handling
    tags_input = input("🏷️  Enter tags (comma-separated, or press Enter to skip): ").strip()
    my_tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()] if tags_input else []
    
    # Get number of results with error handling
    while True:
        try:
            num_input = input("📊 Number of results (default 5): ").strip()
            num_results = int(num_input) if num_input else 5
            if num_results <= 0:
                print("❌ Please enter a positive number!")
                continue
            if num_results > 20:
                print("⚠️  Maximum 20 results allowed, setting to 20.")
                num_results = 20
            break
        except ValueError:
            print("❌ Please enter a valid number (or press Enter for default 5)!")
    
    print(f"\n🔍 Searching for: '{my_prompt}'")
    if my_tags:
        print(f"🏷️  With tags: {', '.join(my_tags)}")
    else:
        print("🏷️  No specific tags")
    print(f"📊 Requesting {num_results} results...")
    print("=" * 50)
    
    # Create request
    request = RecommendRequest(
        query=my_prompt,  # Fixed: should be 'query' not 'prompt'
        user_tags=my_tags,
        k=num_results,
        diversify=True,
        generate=True
    )
    
    try:
        # Get recommendations
        results = hybrid_recommend(request)
        
        print(f"\n✅ Found {len(results)} recommendations:\n")
        
        for i, idea in enumerate(results, 1):
            print(f"{i}. 📌 {idea.title} (Score: {idea.score})")
            print(f"   📝 {idea.description}")
            print(f"   🏷️  Tags: {', '.join(idea.tags)}")
            
            if idea.id.startswith('G'):
                print("   🤖 AI-Generated Idea")
            else:
                print("   📚 Retrieved from Database")
            print()
        
        print("💾 Any AI-generated ideas have been automatically saved to your database for future use")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Tip: Make sure all dependencies are installed and Ollama is running")
        return []

if __name__ == "__main__":
    get_my_recommendations()
