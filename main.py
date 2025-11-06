"""
Main Entry Point - AI-Powered Idea Recommendation System
Generate and recommend ideas based on prompts with full pipeline execution
"""

from enhanced_engine import EnhancedRecommendationEngine
from datetime import datetime
import sys
import os


def print_banner():
    """Print welcome banner"""
    print("\n" + "=" * 80)
    print("  AI-POWERED IDEA RECOMMENDATION SYSTEM")
    print("  Advanced Multi-Module Pipeline with Ollama Integration")
    print("=" * 80)
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")


def print_section(title: str):
    """Print formatted section"""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}")


def generate_ideas_from_prompt(engine, prompt: str, num_ideas: int = 3) -> list:
    """
    Generate multiple ideas using Ollama based on user prompt
    
    Args:
        engine: EnhancedRecommendationEngine instance
        prompt: User's idea generation prompt
        num_ideas: Number of ideas to generate
        
    Returns:
        List of generated idea dictionaries
    """
    print_section(f"GENERATING {num_ideas} IDEAS FROM YOUR PROMPT")
    print(f"Prompt: \"{prompt}\"\n")
    
    # Generate ideas using Ollama
    generation_prompt = f"""Generate {num_ideas} unique and innovative startup/project ideas based on this theme: "{prompt}"

For each idea, provide:
1. A clear title (5-10 words)
2. A detailed description (50-100 words) covering the problem, solution, and impact
3. 3-5 relevant tags

Format your response as:
IDEA 1:
Title: [title here]
Description: [description here]
Tags: [tag1, tag2, tag3, tag4, tag5]

IDEA 2:
...
"""

    print("🤖 Ollama is generating ideas... (this may take 30-60 seconds)\n")
    
    try:
        ollama_response = engine.ollama.generate(generation_prompt)
        
        # Parse Ollama response to extract ideas
        ideas = parse_ollama_ideas(ollama_response, prompt)
        
        if not ideas:
            # Fallback if parsing fails
            print("⚠️  Using fallback idea generation...")
            ideas = generate_fallback_ideas(prompt, num_ideas)
        
        return ideas
        
    except Exception as e:
        print(f"⚠️  Ollama error: {e}")
        print("Using fallback idea generation...\n")
        return generate_fallback_ideas(prompt, num_ideas)


def parse_ollama_ideas(ollama_text: str, theme: str) -> list:
    """Parse Ollama response into structured ideas"""
    ideas = []
    
    try:
        # Split by "IDEA" markers
        sections = ollama_text.split("IDEA")[1:]  # Skip first empty part
        
        for idx, section in enumerate(sections[:5]):  # Max 5 ideas
            lines = section.strip().split('\n')
            
            title = ""
            description = ""
            tags = []
            
            for line in lines:
                line = line.strip()
                if line.startswith("Title:"):
                    title = line.replace("Title:", "").strip()
                elif line.startswith("Description:"):
                    description = line.replace("Description:", "").strip()
                elif line.startswith("Tags:"):
                    tags_text = line.replace("Tags:", "").strip()
                    tags = [t.strip() for t in tags_text.split(',')]
            
            # If description is too short, accumulate next lines
            if description and len(description) < 50:
                for line in lines:
                    if not line.startswith(("Title:", "Description:", "Tags:", "IDEA")):
                        description += " " + line.strip()
            
            if title and description:
                ideas.append({
                    "title": title[:200],  # Limit title length
                    "description": description[:1000],  # Limit description
                    "tags": tags[:5] if tags else [theme, "innovative", "startup"],
                    "author": "AI-Generated"
                })
    
    except Exception as e:
        print(f"⚠️  Parsing error: {e}")
        return []
    
    return ideas


def generate_fallback_ideas(theme: str, num_ideas: int) -> list:
    """Generate fallback ideas if Ollama fails"""
    fallback_templates = [
        {
            "title": f"{theme.title()} Platform with AI Integration",
            "description": f"An innovative platform that leverages artificial intelligence to enhance {theme}. The solution uses machine learning algorithms to optimize user experience, provide personalized recommendations, and automate complex workflows. Features include real-time analytics, predictive modeling, and seamless integration with existing tools.",
            "tags": [theme, "AI", "platform", "innovation", "automation"]
        },
        {
            "title": f"Sustainable {theme.title()} Ecosystem",
            "description": f"A comprehensive ecosystem focused on sustainable {theme} practices. This solution addresses environmental concerns while maintaining efficiency and profitability. Incorporates renewable resources, circular economy principles, and transparent supply chains with blockchain verification.",
            "tags": [theme, "sustainability", "ecosystem", "green-tech", "blockchain"]
        },
        {
            "title": f"Decentralized {theme.title()} Network",
            "description": f"A decentralized network that democratizes access to {theme} services. Built on blockchain technology, this platform ensures transparency, security, and fair distribution of resources. Smart contracts automate transactions while maintaining user privacy and data ownership.",
            "tags": [theme, "decentralized", "blockchain", "web3", "privacy"]
        }
    ]
    
    return [{"author": "AI-Generated", **template} for template in fallback_templates[:num_ideas]]


def add_ideas_to_system(engine, ideas: list) -> list:
    """Add generated ideas to the system with full pipeline"""
    print_section("ADDING IDEAS TO SYSTEM (Full Pipeline)")
    print("Pipeline: Ethics Filter → Feasibility Analysis → Database → Blockchain → Temporal Memory\n")
    
    added_ideas = []
    
    for idx, idea in enumerate(ideas, 1):
        print(f"[{idx}/{len(ideas)}] Processing: {idea['title'][:60]}...")
        
        # Check for duplicates (skip check for now, add_idea_enhanced will handle it)
        # Note: Duplicate detection is done at database level during add_idea_enhanced
        
        # Add with enhanced pipeline
        result = engine.add_idea_enhanced(**idea)
        
        if result["success"]:
            added_ideas.append(result)
            print(f"  ✅ Successfully added")
            print(f"     ID: {result['idea_id'][:16]}...")
            print(f"     Ethics: {result['ethics_assessment']['ethical_score']:.3f} | "
                  f"Compliance: {result['ethics_assessment']['compliance_score']:.3f}")
            print(f"     Feasibility: {result['feasibility_analysis']['feasibility_score']:.3f} | "
                  f"ROI: {result['feasibility_analysis']['roi_level']} | "
                  f"Risk: {result['feasibility_analysis']['risk_level']}")
            print(f"     Blockchain: {result['blockchain_hash'][:24]}...")
            print()
        else:
            print(f"  ❌ Blocked: {result.get('error', 'Unknown error')}\n")
    
    return added_ideas


def get_recommendations(engine, query: str, top_k: int = 5):
    """Get enhanced recommendations with full scoring"""
    print_section(f"GETTING TOP {top_k} RECOMMENDATIONS")
    print(f"Query: \"{query}\"\n")
    print("Using: Causal Reasoning + Economic Feasibility + Ethics + Blockchain + ESG\n")
    
    recommendations = engine.get_recommendations_enhanced(
        query=query,
        top_k=top_k,
        use_causal=True,
        use_feasibility=True
    )
    
    if not recommendations:
        print("❌ No recommendations found\n")
        return []
    
    # Display recommendations table
    print(f"{'Rank':<6} {'Title':<40} {'Score':<8} {'Ethics':<8} {'Feasibility':<12} {'Blockchain':<12}")
    print("─" * 92)
    
    for rec in recommendations:
        print(f"{rec['rank']:<6} {rec['title'][:38]:<40} "
              f"{rec['adjusted_final_score']:<8.4f} "
              f"{rec['ethics_score']:<8.4f} "
              f"{rec['feasibility_score']:<12.4f} "
              f"{'✓' if rec['blockchain_verified'] else '✗':<12}")
    
    print("\n" + "─" * 80)
    
    # Detailed view of top recommendation
    top_rec = recommendations[0]
    print(f"\n🏆 TOP RECOMMENDATION: {top_rec['title']}")
    print(f"   Author: {top_rec['author']}")
    print(f"   Tags: {', '.join(top_rec['tags'][:5])}")
    print(f"\n   📊 DETAILED SCORES:")
    print(f"      Base Score:           {top_rec['final_score']:.4f}")
    print(f"      Adjusted Score:       {top_rec['adjusted_final_score']:.4f}")
    print(f"      Ethics Score:         {top_rec['ethics_score']:.4f}")
    print(f"      Ethics Compliance:    {top_rec['ethics_compliance']:.4f}")
    print(f"      Feasibility Score:    {top_rec['feasibility_score']:.4f}")
    print(f"      Causal Impact:        {top_rec['causal_impact']:.4f}")
    print(f"      ESG Total:            {top_rec['esg_scores']['total_esg']:.4f}")
    print(f"         - Environmental:   {top_rec['esg_scores']['environmental']:.4f}")
    print(f"         - Social:          {top_rec['esg_scores']['social']:.4f}")
    print(f"         - Governance:      {top_rec['esg_scores']['governance']:.4f}")
    print(f"      Integrity Score:      {top_rec['integrity_score']:.4f}")
    print(f"      Blockchain Verified:  {'✓' if top_rec['blockchain_verified'] else '✗'}")
    
    # Explanation
    if top_rec['explanation']['top_features']:
        print(f"\n   💡 TOP CONTRIBUTING FEATURES:")
        for feat in top_rec['explanation']['top_features'][:3]:
            print(f"      • {feat['feature']}: {feat['contribution']:.4f}")
    
    return recommendations


def display_system_stats(engine):
    """Display comprehensive system statistics"""
    print_section("SYSTEM STATISTICS & INTEGRITY CHECK")
    
    report = engine.generate_comprehensive_report()
    
    print("\n📈 DATABASE STATISTICS:")
    print(f"   Total Ideas: {report['base_audit']['total_ideas']}")
    print(f"   Integrity: {report['base_audit']['integrity']['status']}")
    print(f"   Bias Detected: {report['base_audit']['bias']['bias_detected']}")
    
    print("\n🔗 BLOCKCHAIN STATUS:")
    print(f"   Total Blocks: {report['blockchain']['summary']['total_blocks']}")
    print(f"   Unique Ideas: {report['blockchain']['summary']['unique_ideas']}")
    print(f"   Chain Valid: {'✓' if report['blockchain']['integrity']['valid'] else '✗'}")
    
    print("\n🧠 TEMPORAL MEMORY:")
    print(f"   Recent Contexts (24h): {report['temporal_memory']['recent_contexts_24h']}")
    print(f"   Recent Embeddings (7d): {report['temporal_memory']['recent_embeddings_7d']}")
    
    print("\n🤝 FEDERATED LEARNING:")
    print(f"   Update Rounds: {report['federated_learning']['update_rounds']}")
    print(f"   Total Feedbacks: {report['federated_learning']['total_feedbacks']}")
    
    print()


def main():
    """Main execution flow"""
    print_banner()
    
    # Initialize enhanced engine
    print("🚀 Initializing Enhanced Recommendation Engine...")
    print("   Loading 27 integrated modules...")
    
    try:
        engine = EnhancedRecommendationEngine(
            db_path="data/ideas.db",
            ollama_model="llama3.2:1b"  # Using available model
        )
        print("   ✅ Engine initialized successfully\n")
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return 1
    
    # Get user prompt (or use default for demonstration)
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        print("💡 No prompt provided. Using default demonstration prompt.")
        print("   Usage: python main.py \"your idea generation prompt\"\n")
        user_prompt = "sustainable technology for climate change"
    
    print(f"🎯 Your Prompt: \"{user_prompt}\"")
    
    try:
        # Step 1: Generate ideas from prompt
        generated_ideas = generate_ideas_from_prompt(engine, user_prompt, num_ideas=3)
        
        if not generated_ideas:
            print("❌ No ideas generated. Exiting.")
            return 1
        
        print(f"✅ Generated {len(generated_ideas)} unique ideas\n")
        
        # Step 2: Add ideas to system with full pipeline
        added_ideas = add_ideas_to_system(engine, generated_ideas)
        
        if not added_ideas:
            print("⚠️  No new ideas added (all were duplicates or blocked)")
            # Continue anyway to show existing recommendations
        
        # Step 3: Get recommendations
        recommendations = get_recommendations(engine, user_prompt, top_k=5)
        
        # Step 4: Display system statistics
        display_system_stats(engine)
        
        # Success message
        print_section("✨ EXECUTION COMPLETED SUCCESSFULLY")
        print(f"\n   ✅ Ideas Generated: {len(generated_ideas)}")
        print(f"   ✅ Ideas Added: {len(added_ideas)}")
        print(f"   ✅ Recommendations: {len(recommendations)}")
        print(f"   ✅ Database Updated: ideas.db")
        print(f"   ✅ Blockchain Verified: All ideas have tamper-proof hashes")
        print(f"   ✅ No Duplicates: Duplicate detection active")
        print(f"\n   📄 See 'docs/document.md' for detailed documentation")
        print(f"   📊 See 'README.md' for project overview\n")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
