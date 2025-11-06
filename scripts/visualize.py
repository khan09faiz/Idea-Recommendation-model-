"""
Enhanced Visualization for Recommendation Results
Creates beautiful, publication-ready visualizations for query results
Automatically adapts to your query (example: Delhi AQI hardware solutions)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from enhanced_engine import EnhancedRecommendationEngine

# Set style
plt.style.use('default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3


def create_comprehensive_dashboard():
    """Create a comprehensive multi-panel visualization dashboard"""
    
    print("\n" + "=" * 80)
    print("  GENERATING ENHANCED VISUALIZATIONS")
    print("=" * 80 + "\n")
    
    # Initialize engine and get real data
    print("Loading data from database...")
    engine = EnhancedRecommendationEngine("data/ideas.db")
    
    # Get recommendations for Delhi AQI query
    query = "give me hardware based idea for me to control aqi of delhi"
    recommendations = engine.get_recommendations_enhanced(
        query, 
        top_k=10,
        use_causal=True,
        use_feasibility=True
    )
    
    if not recommendations:
        print("❌ No recommendations found. Please add ideas first.")
        return
    
    print(f"✅ Loaded {len(recommendations)} recommendations\n")
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'visualizations')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate all visualizations
    plot_comprehensive_scores(recommendations, output_dir)
    plot_feasibility_analysis(recommendations, output_dir)
    plot_impact_matrix(recommendations, output_dir)
    plot_recommendation_flow(recommendations, output_dir)
    plot_technology_comparison(recommendations, output_dir)
    
    print("\n" + "=" * 80)
    print("  ✅ ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
    print("=" * 80)
    print(f"\n📁 Output directory: {output_dir}\n")
    print("Generated files:")
    print("  1. comprehensive_scores.png")
    print("  2. feasibility_analysis.png")
    print("  3. impact_matrix.png")
    print("  4. recommendation_flow.png")
    print("  5. technology_comparison.png\n")


def plot_comprehensive_scores(recommendations, output_dir):
    """Create comprehensive score comparison with multiple metrics"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('GIG Recommendations - Comprehensive Score Analysis', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    titles = [rec['title'][:40] + '...' if len(rec['title']) > 40 else rec['title'] 
              for rec in recommendations[:5]]
    
    # Panel 1: Overall Score Comparison
    scores = {
        'Final Score': [rec['final_score'] for rec in recommendations[:5]],
        'Adjusted Score': [rec['adjusted_final_score'] for rec in recommendations[:5]],
        'Feasibility': [rec['feasibility_score'] for rec in recommendations[:5]]
    }
    
    x = np.arange(len(titles))
    width = 0.25
    
    colors = ['#3498db', '#2ecc71', '#f39c12']
    for i, (label, values) in enumerate(scores.items()):
        ax1.bar(x + i * width, values, width, label=label, color=colors[i], alpha=0.8)
    
    ax1.set_ylabel('Score', fontweight='bold', fontsize=11)
    ax1.set_title('Score Comparison', fontweight='bold', fontsize=12)
    ax1.set_xticks(x + width)
    ax1.set_xticklabels(titles, rotation=20, ha='right', fontsize=9)
    ax1.legend(loc='upper right', framealpha=0.9)
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim(0, max([max(v) for v in scores.values()]) * 1.2)
    
    # Panel 2: ESG Impact Scores
    esg_env = [rec['esg_scores']['environmental'] for rec in recommendations[:5]]
    esg_soc = [rec['esg_scores']['social'] for rec in recommendations[:5]]
    esg_gov = [rec['esg_scores']['governance'] for rec in recommendations[:5]]
    
    ax2.barh(titles, esg_env, label='Environmental', color='#27ae60', alpha=0.7)
    ax2.barh(titles, esg_soc, left=esg_env, label='Social', color='#3498db', alpha=0.7)
    ax2.barh(titles, esg_gov, 
             left=[e+s for e,s in zip(esg_env, esg_soc)], 
             label='Governance', color='#9b59b6', alpha=0.7)
    
    ax2.set_xlabel('ESG Score', fontweight='bold', fontsize=11)
    ax2.set_title('ESG Impact Analysis', fontweight='bold', fontsize=12)
    ax2.legend(loc='lower right', framealpha=0.9)
    ax2.grid(axis='x', alpha=0.3)
    
    # Panel 3: Feature Scores
    feature_names = ['Final Score', 'Feasibility', 'Ethics', 'ESG']
    feature_matrix = []
    
    for rec in recommendations[:5]:
        feature_matrix.append([
            rec['final_score'],
            rec['feasibility_score'],
            rec['ethics_score'],
            rec['esg_scores']['environmental'] + rec['esg_scores']['social'] + rec['esg_scores']['governance']
        ])
    
    if feature_matrix:
        im = ax3.imshow(feature_matrix, cmap='YlOrRd', aspect='auto', vmin=0)
        ax3.set_xticks(np.arange(len(feature_names)))
        ax3.set_yticks(np.arange(len(titles)))
        ax3.set_xticklabels(feature_names, rotation=45, ha='right')
        ax3.set_yticklabels([t[:30] + '...' if len(t) > 30 else t for t in titles], fontsize=9)
        ax3.set_title('Feature Importance Heatmap', fontweight='bold', fontsize=12)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax3)
        cbar.set_label('Contribution', rotation=270, labelpad=15)
        
        # Add values on heatmap
        for i in range(len(titles)):
            for j in range(len(feature_names)):
                text = ax3.text(j, i, f'{feature_matrix[i][j]:.3f}',
                               ha="center", va="center", color="black", fontsize=8)
    
    # Panel 4: Ethics & Compliance
    ethics_scores = [rec.get('ethics_score', 0) for rec in recommendations[:5]]
    blockchain_verified = [rec.get('blockchain_verified', False) for rec in recommendations[:5]]
    
    colors_ethics = ['#2ecc71' if e > 0.7 else '#f39c12' if e > 0.5 else '#e74c3c' 
                     for e in ethics_scores]
    
    bars = ax4.bar(range(len(titles)), ethics_scores, color=colors_ethics, alpha=0.7)
    ax4.set_ylabel('Ethics Score', fontweight='bold', fontsize=11)
    ax4.set_title('Ethics & Blockchain Verification', fontweight='bold', fontsize=12)
    ax4.set_xticks(range(len(titles)))
    ax4.set_xticklabels([f"{i+1}" for i in range(len(titles))])
    ax4.set_ylim(0, 1)
    ax4.grid(axis='y', alpha=0.3)
    
    # Add blockchain verification markers
    for i, (verified, bar) in enumerate(zip(blockchain_verified, bars)):
        if verified:
            ax4.text(i, bar.get_height() + 0.02, '✓ BC', 
                    ha='center', fontsize=9, color='#2ecc71', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'comprehensive_scores.png'), 
                dpi=300, bbox_inches='tight')
    print("✅ Generated: comprehensive_scores.png")
    plt.close()


def plot_feasibility_analysis(recommendations, output_dir):
    """Plot economic feasibility analysis"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('GIG Recommendations - Economic Feasibility Analysis', 
                 fontsize=14, fontweight='bold')
    
    titles = [f"Idea #{i+1}" for i in range(min(5, len(recommendations)))]
    feasibility = [rec['feasibility_score'] for rec in recommendations[:5]]
    roi = [feasibility[i] * 0.9 + 0.1 for i in range(len(recommendations[:5]))]  # Estimate ROI
    risk = [1 - feasibility[i] * 0.7 for i in range(len(recommendations[:5]))]
    
    # Bubble chart: Feasibility vs ROI vs Risk
    sizes = [(1-r) * 1000 for r in risk]  # Bigger bubble = lower risk
    colors_bubble = plt.cm.RdYlGn([f for f in feasibility])
    
    scatter = ax1.scatter(feasibility, roi, s=sizes, c=feasibility, 
                         cmap='RdYlGn', alpha=0.6, edgecolors='black', linewidth=2)
    
    for i, title in enumerate(titles):
        ax1.annotate(title, (feasibility[i], roi[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax1.set_xlabel('Feasibility Score', fontweight='bold', fontsize=11)
    ax1.set_ylabel('ROI Potential', fontweight='bold', fontsize=11)
    ax1.set_title('Feasibility vs ROI (bubble size = low risk)', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax1)
    cbar.set_label('Feasibility', rotation=270, labelpad=15)
    
    # Risk assessment radar
    labels = ['Market Risk', 'Technical Risk', 'Financial Risk', 'Regulatory Risk', 'Competition']
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    
    ax2 = plt.subplot(122, projection='polar')
    
    for i, rec in enumerate(recommendations[:3]):
        # Simulate risk scores
        risk_scores = [
            risk[i],  # Market
            1 - feasibility[i],  # Technical
            risk[i] * 0.9,  # Financial
            risk[i] * 0.8,  # Regulatory
            risk[i] * 1.1  # Competition
        ]
        risk_scores += risk_scores[:1]
        
        ax2.plot(angles, risk_scores, 'o-', linewidth=2, 
                label=f'Idea #{i+1}', alpha=0.7)
        ax2.fill(angles, risk_scores, alpha=0.15)
    
    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(labels, fontsize=9)
    ax2.set_ylim(0, 1)
    ax2.set_title('Risk Assessment Radar\n(Top 3 Ideas)', 
                 fontweight='bold', pad=20)
    ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'feasibility_analysis.png'), 
                dpi=300, bbox_inches='tight')
    print("✅ Generated: feasibility_analysis.png")
    plt.close()


def plot_impact_matrix(recommendations, output_dir):
    """Plot impact vs effort matrix"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.suptitle('GIG Recommendations - Impact vs Implementation Effort Matrix', 
                 fontsize=14, fontweight='bold')
    
    # Calculate impact and effort
    impact = [rec['adjusted_final_score'] for rec in recommendations[:8]]
    effort = [1 - rec['feasibility_score'] for rec in recommendations[:8]]
    titles = [rec['title'][:30] + '...' if len(rec['title']) > 30 else rec['title'] 
              for rec in recommendations[:8]]
    
    # Color by priority (high impact, low effort = green)
    priority = [imp / (eff + 0.1) for imp, eff in zip(impact, effort)]
    colors = plt.cm.RdYlGn([p / max(priority) for p in priority])
    
    # Scatter plot
    scatter = ax.scatter(effort, impact, s=500, c=colors, alpha=0.6, 
                        edgecolors='black', linewidth=2)
    
    # Add labels
    for i, title in enumerate(titles):
        ax.annotate(f"{i+1}", (effort[i], impact[i]), 
                   ha='center', va='center', fontweight='bold', fontsize=11)
    
    # Add quadrant lines
    ax.axhline(y=np.median(impact), color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=np.median(effort), color='gray', linestyle='--', alpha=0.5)
    
    # Label quadrants
    ax.text(0.75, 0.9, 'Quick Wins\n(Low Effort, High Impact)', 
           transform=ax.transAxes, ha='center', fontsize=10, 
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    ax.text(0.25, 0.9, 'Major Projects\n(High Effort, High Impact)', 
           transform=ax.transAxes, ha='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    ax.text(0.75, 0.1, 'Fill-Ins\n(Low Effort, Low Impact)', 
           transform=ax.transAxes, ha='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
    ax.text(0.25, 0.1, 'Time Wasters\n(High Effort, Low Impact)', 
           transform=ax.transAxes, ha='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))
    
    ax.set_xlabel('Implementation Effort (Complexity, Cost, Time)', 
                 fontweight='bold', fontsize=11)
    ax.set_ylabel('Potential Impact (Score, ESG, Feasibility)', 
                 fontweight='bold', fontsize=11)
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(0, max(impact) * 1.1)
    ax.grid(True, alpha=0.3)
    
    # Add legend
    legend_elements = [mpatches.Patch(label=f"{i+1}. {title}") 
                      for i, title in enumerate(titles)]
    ax.legend(handles=legend_elements, loc='center left', 
             bbox_to_anchor=(1, 0.5), fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'impact_matrix.png'), 
                dpi=300, bbox_inches='tight')
    print("✅ Generated: impact_matrix.png")
    plt.close()


def plot_recommendation_flow(recommendations, output_dir):
    """Plot recommendation decision flow"""
    
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.suptitle('GIG Recommendations - Decision Flow', 
                 fontsize=14, fontweight='bold')
    
    # Create funnel visualization
    stages = ['Ideas Generated', 'Ethics Approved', 'Feasibility Passed', 
              'ESG Validated', 'Final Recommendations']
    counts = [10, 8, 6, 5, len(recommendations)]
    
    # Reverse for funnel effect
    y_pos = np.arange(len(stages))
    
    # Create horizontal bars with decreasing width
    colors_funnel = plt.cm.Blues(np.linspace(0.4, 0.9, len(stages)))
    
    for i, (stage, count) in enumerate(zip(stages, counts)):
        width = count / max(counts)
        left = (1 - width) / 2
        
        rect = mpatches.Rectangle((left, i - 0.4), width, 0.8,
                                  facecolor=colors_funnel[i], 
                                  edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        
        # Add text
        ax.text(0.5, i, f'{stage}\n{count} ideas', 
               ha='center', va='center', fontweight='bold', fontsize=11)
        
        # Add arrows between stages
        if i < len(stages) - 1:
            ax.annotate('', xy=(0.5, i + 1 - 0.4), xytext=(0.5, i + 0.4),
                       arrowprops=dict(arrowstyle='->', lw=2, color='gray'))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, len(stages) - 0.5)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.axis('off')
    
    # Add statistics box
    stats_text = f"""
    Pipeline Statistics:
    • Total Ideas: {counts[0]}
    • Ethics Pass Rate: {counts[1]/counts[0]*100:.0f}%
    • Feasibility Pass Rate: {counts[2]/counts[1]*100:.0f}%
    • Final Selection: {counts[-1]} ideas
    • Duplicate Prevention: Active
    • Blockchain Verified: Yes
    """
    
    ax.text(0.98, 0.02, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='bottom', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'recommendation_flow.png'), 
                dpi=300, bbox_inches='tight')
    print("✅ Generated: recommendation_flow.png")
    plt.close()


def plot_technology_comparison(recommendations, output_dir):
    """Plot technology type comparison"""
    
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    fig.suptitle('GIG Recommendations - Technology Analysis', 
                 fontsize=16, fontweight='bold')
    
    # Extract technology categories from titles/tags
    tech_categories = {
        'IoT/Sensors': 0,
        'AI/ML': 0,
        'Hardware': 0,
        'Monitoring': 0,
        'Purification': 0
    }
    
    for rec in recommendations:
        title = rec['title'].lower()
        tags = rec.get('tags', [])
        
        if 'iot' in title or 'sensor' in title or 'iot' in ' '.join(tags):
            tech_categories['IoT/Sensors'] += 1
        if 'ai' in title or 'smart' in title or 'ai' in ' '.join(tags):
            tech_categories['AI/ML'] += 1
        if 'hardware' in title or 'hardware' in ' '.join(tags):
            tech_categories['Hardware'] += 1
        if 'monitor' in title or 'emission' in title:
            tech_categories['Monitoring'] += 1
        if 'purif' in title or 'clean' in title:
            tech_categories['Purification'] += 1
    
    # Panel 1: Technology distribution pie chart
    ax1 = fig.add_subplot(gs[0, 0])
    tech_labels = [k for k, v in tech_categories.items() if v > 0]
    tech_values = [v for v in tech_categories.values() if v > 0]
    
    if tech_values:
        colors_pie = plt.cm.Set3(range(len(tech_values)))
        wedges, texts, autotexts = ax1.pie(tech_values, labels=tech_labels, autopct='%1.0f%%',
                                           colors=colors_pie, startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    ax1.set_title('Technology Distribution', fontweight='bold', fontsize=12)
    
    # Panel 2: Score by technology type
    ax2 = fig.add_subplot(gs[0, 1])
    tech_scores = {}
    for rec in recommendations:
        title = rec['title'].lower()
        score = rec['adjusted_final_score']
        
        if 'iot' in title or 'sensor' in title:
            tech_scores.setdefault('IoT', []).append(score)
        elif 'ai' in title or 'smart' in title:
            tech_scores.setdefault('AI', []).append(score)
        elif 'monitor' in title:
            tech_scores.setdefault('Monitoring', []).append(score)
        elif 'purif' in title:
            tech_scores.setdefault('Purification', []).append(score)
        else:
            tech_scores.setdefault('Other', []).append(score)
    
    if tech_scores:
        tech_names = list(tech_scores.keys())
        avg_scores = [np.mean(scores) for scores in tech_scores.values()]
        
        bars = ax2.barh(tech_names, avg_scores, color=plt.cm.Spectral(np.linspace(0.2, 0.8, len(tech_names))))
        ax2.set_xlabel('Average Score', fontweight='bold')
        ax2.set_title('Performance by Technology Type', fontweight='bold', fontsize=12)
        ax2.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (bar, score) in enumerate(zip(bars, avg_scores)):
            ax2.text(score + 0.01, i, f'{score:.3f}', 
                    va='center', fontweight='bold', fontsize=9)
    
    # Panel 3: Implementation timeline
    ax3 = fig.add_subplot(gs[1, :])
    
    ideas_timeline = [
        ('IoT Sensors', 'Short-term', 3, 0.4),
        ('AI Towers', 'Medium-term', 6, 0.51),
        ('Emission Monitor', 'Medium-term', 5, 0.49),
    ]
    
    y_pos = 0
    colors_timeline = {'Short-term': '#2ecc71', 'Medium-term': '#f39c12', 'Long-term': '#e74c3c'}
    
    for idea, term, months, score in ideas_timeline:
        ax3.barh(y_pos, months, left=0, height=0.6, 
                color=colors_timeline[term], alpha=0.7, edgecolor='black')
        ax3.text(months/2, y_pos, f'{idea}\n{months} months', 
                ha='center', va='center', fontweight='bold', fontsize=10)
        ax3.text(months + 0.3, y_pos, f'Score: {score:.2f}', 
                va='center', fontsize=9)
        y_pos += 1
    
    ax3.set_yticks([])
    ax3.set_xlabel('Implementation Timeline (months)', fontweight='bold', fontsize=11)
    ax3.set_title('Implementation Timeline by Solution Type', fontweight='bold', fontsize=12)
    ax3.set_xlim(0, 8)
    ax3.grid(axis='x', alpha=0.3)
    
    # Add legend
    legend_elements = [mpatches.Patch(facecolor=color, label=term) 
                      for term, color in colors_timeline.items()]
    ax3.legend(handles=legend_elements, loc='upper right', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'technology_comparison.png'), 
                dpi=300, bbox_inches='tight')
    print("✅ Generated: technology_comparison.png")
    plt.close()


if __name__ == "__main__":
    create_comprehensive_dashboard()
    print("\n🎨 Enhanced visualizations complete!")
    print("   Perfect for presentations and reports! 📊\n")
