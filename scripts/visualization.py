"""
GIG System - Visualization Module
Generates comprehensive visualizations for evaluation results
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict
import json
import sys
import os
import codecs

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix UTF-8 encoding for Windows
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

class GIGVisualizer:
    """Generate visualizations for GIG system evaluation"""
    
    def __init__(self):
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#06A77D',
            'warning': '#F18F01',
            'danger': '#C73E1D',
            'info': '#6B4E71'
        }
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def plot_score_comparison(self, recommendations: List[Dict], save_path: str = 'scores_comparison.png'):
        """
        Create bar chart comparing scores across recommendations
        
        Args:
            recommendations: List of recommendation dictionaries
            save_path: Output file path
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Extract data
        titles = [rec['title'][:30] + '...' if len(rec['title']) > 30 else rec['title'] 
                  for rec in recommendations]
        base_scores = [rec.get('base_score', 0) for rec in recommendations]
        adjusted_scores = [rec.get('adjusted_score', 0) for rec in recommendations]
        feasibility_scores = [rec.get('feasibility_score', 0) for rec in recommendations]
        
        # Set up bar positions
        x = np.arange(len(titles))
        width = 0.25
        
        # Create bars
        bars1 = ax.bar(x - width, base_scores, width, label='Base Score', 
                       color=self.colors['primary'], alpha=0.8)
        bars2 = ax.bar(x, adjusted_scores, width, label='Adjusted Score',
                       color=self.colors['success'], alpha=0.8)
        bars3 = ax.bar(x + width, feasibility_scores, width, label='Feasibility',
                       color=self.colors['warning'], alpha=0.8)
        
        # Customize plot
        ax.set_xlabel('Recommendations', fontsize=12, fontweight='bold')
        ax.set_ylabel('Score', fontsize=12, fontweight='bold')
        ax.set_title('GIG Score Comparison Across Recommendations', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(titles, rotation=15, ha='right')
        ax.legend(loc='upper right', framealpha=0.9)
        ax.set_ylim(0, 1.0)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Score comparison chart saved to: {save_path}")
        plt.close()
    
    def plot_esg_radar(self, recommendations: List[Dict], save_path: str = 'esg_radar.png'):
        """
        Create radar chart for ESG scores
        
        Args:
            recommendations: List of recommendation dictionaries
            save_path: Output file path
        """
        fig, axes = plt.subplots(1, len(recommendations), figsize=(15, 5), 
                                 subplot_kw=dict(projection='polar'))
        
        if len(recommendations) == 1:
            axes = [axes]
        
        categories = ['Environmental', 'Social', 'Governance']
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # Close the circle
        
        for idx, (ax, rec) in enumerate(zip(axes, recommendations)):
            # Extract ESG scores
            esg_scores = rec.get('esg_scores', {})
            values = [
                esg_scores.get('environmental', 0),
                esg_scores.get('social', 0),
                esg_scores.get('governance', 0)
            ]
            values += values[:1]  # Close the circle
            
            # Plot
            ax.plot(angles, values, 'o-', linewidth=2, color=self.colors['success'])
            ax.fill(angles, values, alpha=0.25, color=self.colors['success'])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=9)
            ax.set_ylim(0, 1.0)
            ax.set_title(f"Rank #{idx+1}: {rec['title'][:25]}...", 
                        fontsize=10, fontweight='bold', pad=15)
            ax.grid(True, alpha=0.3)
        
        plt.suptitle('ESG Scores Radar Chart', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"ESG radar chart saved to: {save_path}")
        plt.close()
    
    def plot_feature_importance(self, recommendations: List[Dict], save_path: str = 'feature_importance.png'):
        """
        Create heatmap of feature importance across recommendations
        
        Args:
            recommendations: List of recommendation dictionaries
            save_path: Output file path
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Extract features
        all_features = set()
        for rec in recommendations:
            all_features.update(rec.get('top_features', {}).keys())
        
        features = sorted(list(all_features))
        titles = [f"Rank #{i+1}" for i in range(len(recommendations))]
        
        # Create feature matrix
        feature_matrix = np.zeros((len(recommendations), len(features)))
        for i, rec in enumerate(recommendations):
            top_features = rec.get('top_features', {})
            for j, feature in enumerate(features):
                feature_matrix[i, j] = top_features.get(feature, 0)
        
        # Create heatmap
        im = ax.imshow(feature_matrix.T, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)
        
        # Customize plot
        ax.set_xticks(np.arange(len(titles)))
        ax.set_yticks(np.arange(len(features)))
        ax.set_xticklabels(titles)
        ax.set_yticklabels(features)
        ax.set_xlabel('Recommendations', fontsize=12, fontweight='bold')
        ax.set_ylabel('Features', fontsize=12, fontweight='bold')
        ax.set_title('Feature Importance Heatmap', fontsize=14, fontweight='bold', pad=20)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Importance Score', fontsize=10)
        
        # Add value annotations
        for i in range(len(titles)):
            for j in range(len(features)):
                text = ax.text(i, j, f'{feature_matrix[i, j]:.3f}',
                              ha="center", va="center", color="black", fontsize=8)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Feature importance heatmap saved to: {save_path}")
        plt.close()
    
    def plot_blockchain_timeline(self, blockchain_data: Dict, save_path: str = 'blockchain_timeline.png'):
        """
        Create timeline visualization of blockchain integrity
        
        Args:
            blockchain_data: Blockchain summary dictionary
            save_path: Output file path
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
        
        # Extract data
        total_blocks = blockchain_data.get('summary', {}).get('total_blocks', 0)
        unique_ideas = blockchain_data.get('summary', {}).get('unique_ideas', 0)
        chain_valid = blockchain_data.get('integrity', {}).get('valid', False)
        
        # Plot 1: Block creation timeline
        blocks = list(range(1, total_blocks + 1))
        timestamps = list(range(len(blocks)))
        
        ax1.plot(blocks, timestamps, 'o-', color=self.colors['primary'], 
                linewidth=2, markersize=8, label='Blocks Created')
        ax1.fill_between(blocks, 0, timestamps, alpha=0.2, color=self.colors['primary'])
        ax1.set_xlabel('Block Number', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Sequence', fontsize=12, fontweight='bold')
        ax1.set_title('Blockchain Block Creation Timeline', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')
        
        # Add genesis block marker
        ax1.axvline(x=1, color=self.colors['danger'], linestyle='--', 
                   linewidth=2, alpha=0.7, label='Genesis Block')
        ax1.text(1, timestamps[-1] * 0.9, 'Genesis Block', 
                rotation=90, va='top', ha='right', fontsize=9, color=self.colors['danger'])
        
        # Plot 2: Integrity status
        categories = ['Total Blocks', 'Unique Ideas', 'Chain Valid']
        values = [total_blocks, unique_ideas, int(chain_valid)]
        colors = [self.colors['primary'], self.colors['success'], 
                 self.colors['success'] if chain_valid else self.colors['danger']]
        
        bars = ax2.barh(categories, values, color=colors, alpha=0.8)
        ax2.set_xlabel('Count / Status', fontsize=12, fontweight='bold')
        ax2.set_title('Blockchain Integrity Summary', fontsize=13, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{width}' if width > 1 else ('Valid' if width == 1 else 'Invalid'),
                    ha='left', va='center', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Blockchain timeline saved to: {save_path}")
        plt.close()
    
    def plot_performance_metrics(self, metrics: Dict, save_path: str = 'performance_metrics.png'):
        """
        Create comprehensive performance metrics dashboard
        
        Args:
            metrics: Dictionary of performance metrics
            save_path: Output file path
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        fig.suptitle('GIG System Performance Dashboard', fontsize=16, fontweight='bold')        # Plot 1: Recommendation Quality (top-left)
        ax1 = axes[0, 0]
        quality_metrics = ['nDCG@3', 'MAP@3', 'Precision@3']
        quality_values = [
            metrics.get('ndcg', 0.8654),
            metrics.get('map', 1.0),
            metrics.get('precision', 1.0)
        ]
        bars1 = ax1.bar(quality_metrics, quality_values, color=self.colors['success'], alpha=0.8)
        ax1.set_ylabel('Score', fontsize=11, fontweight='bold')
        ax1.set_title('Recommendation Quality', fontsize=12, fontweight='bold')
        ax1.set_ylim(0, 1.1)
        ax1.axhline(y=0.8, color='red', linestyle='--', alpha=0.5, label='Threshold (0.8)')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Plot 2: Diversity & Novelty (top-right)
        ax2 = axes[0, 1]
        diversity_metrics = ['ILD', 'Serendipity', 'Coverage']
        diversity_values = [
            metrics.get('ild', 0.647),
            metrics.get('serendipity', 0.089),
            metrics.get('coverage', 1.0)
        ]
        bars2 = ax2.bar(diversity_metrics, diversity_values, color=self.colors['warning'], alpha=0.8)
        ax2.set_ylabel('Score', fontsize=11, fontweight='bold')
        ax2.set_title('Diversity & Novelty', fontsize=12, fontweight='bold')
        ax2.set_ylim(0, 1.1)
        ax2.grid(axis='y', alpha=0.3)
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Plot 3: System Integrity (bottom-left)
        ax3 = axes[1, 0]
        integrity_categories = ['Database\nValidity', 'Blockchain\nVerification', 'Bias\nDetection']
        integrity_values = [
            metrics.get('database_validity', 1.0),
            metrics.get('blockchain_verification', 1.0),
            1.0 - metrics.get('bias_detected', 0.0)
        ]
        bars3 = ax3.bar(integrity_categories, integrity_values, 
                       color=[self.colors['success'], self.colors['info'], self.colors['primary']], 
                       alpha=0.8)
        ax3.set_ylabel('Success Rate', fontsize=11, fontweight='bold')
        ax3.set_title('System Integrity', fontsize=12, fontweight='bold')
        ax3.set_ylim(0, 1.1)
        ax3.axhline(y=1.0, color='green', linestyle='--', alpha=0.5, label='Perfect (1.0)')
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)
        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1%}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Plot 4: Performance Latency (bottom-right)
        ax4 = axes[1, 1]
        latency_stages = ['Idea\nAddition', 'Recommendation\nRetrieval', 'Full\nPipeline']
        latency_values = [
            metrics.get('idea_addition_latency', 0.22),
            metrics.get('recommendation_latency', 0.28),
            metrics.get('full_pipeline_latency', 1.5)
        ]
        bars4 = ax4.bar(latency_stages, latency_values, color=self.colors['secondary'], alpha=0.8)
        ax4.set_ylabel('Time (seconds)', fontsize=11, fontweight='bold')
        ax4.set_title('System Latency', fontsize=12, fontweight='bold')
        ax4.axhline(y=1.0, color='orange', linestyle='--', alpha=0.5, label='1s Threshold')
        ax4.legend()
        ax4.grid(axis='y', alpha=0.3)
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}s', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Performance dashboard saved to: {save_path}")
        plt.close()
    
    def plot_standards_compliance(self, compliance_data: Dict, save_path: str = 'standards_compliance.png'):
        """
        Create pie chart and bar chart for standards compliance
        
        Args:
            compliance_data: Dictionary of compliance scores
            save_path: Output file path
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Overall compliance pie chart
        categories = list(compliance_data.keys())
        scores = list(compliance_data.values())
        colors_list = [self.colors['success'], self.colors['primary'], 
                      self.colors['info'], self.colors['warning'], self.colors['secondary']]
        
        wedges, texts, autotexts = ax1.pie(scores, labels=categories, autopct='%1.1f%%',
                                           colors=colors_list[:len(categories)], startangle=90,
                                           textprops={'fontsize': 10, 'weight': 'bold'})
        ax1.set_title('Standards Compliance Distribution', fontsize=13, fontweight='bold', pad=20)
        
        # Plot 2: Compliance scores bar chart
        bars = ax2.barh(categories, scores, color=colors_list[:len(categories)], alpha=0.8)
        ax2.set_xlabel('Compliance Score (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Standards Compliance Scores', fontsize=13, fontweight='bold')
        ax2.set_xlim(0, 100)
        ax2.axvline(x=90, color='green', linestyle='--', alpha=0.5, label='Target (90%)')
        ax2.legend()
        ax2.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax2.text(width + 1, bar.get_y() + bar.get_height()/2.,
                    f'{width:.1f}%', ha='left', va='center', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Standards compliance chart saved to: {save_path}")
        plt.close()


def generate_all_visualizations():
    """Generate all visualizations with sample Delhi AQI data"""
    
    visualizer = GIGVisualizer()    # Sample recommendations (from run_evaluation.py results)
    recommendations = [
        {
            'title': 'Smart Air Purification Towers with AI Control',
            'base_score': 0.6085,
            'adjusted_score': 0.5099,
            'feasibility_score': 0.3990,
            'esg_scores': {
                'environmental': 0.3333,
                'social': 0.0000,
                'governance': 0.0000
            },
            'top_features': {
                'elo': 0.1500,
                'trend': 0.1275,
                'freshness': 0.1000
            }
        },
        {
            'title': 'Vehicle Emission Monitoring Hardware System',
            'base_score': 0.5919,
            'adjusted_score': 0.4939,
            'feasibility_score': 0.3762,
            'esg_scores': {
                'environmental': 0.3333,
                'social': 0.0000,
                'governance': 0.3333
            },
            'top_features': {
                'elo': 0.1500,
                'freshness': 0.1000,
                'serendipity': 0.0990
            }
        },
        {
            'title': 'IoT Air Quality Sensor Network for Delhi NCR',
            'base_score': 0.5694,
            'adjusted_score': 0.4793,
            'feasibility_score': 0.3853,
            'esg_scores': {
                'environmental': 0.0000,
                'social': 0.0000,
                'governance': 0.0000
            },
            'top_features': {
                'elo': 0.1500,
                'trend': 0.1050,
                'freshness': 0.1000
            }
        }
    ]
    
    # Blockchain data
    blockchain_data = {
        'summary': {
            'total_blocks': 4,
            'unique_ideas': 3
        },
        'integrity': {
            'valid': True
        }
    }
    
    # Performance metrics
    metrics = {
        'ndcg': 0.8654,
        'map': 1.0,
        'precision': 1.0,
        'ild': 0.647,
        'serendipity': 0.089,
        'coverage': 1.0,
        'database_validity': 1.0,
        'blockchain_verification': 1.0,
        'bias_detected': 0.0,
        'idea_addition_latency': 0.22,
        'recommendation_latency': 0.28,
        'full_pipeline_latency': 1.5
    }
    
    # Compliance data
    compliance_data = {
        'IEEE Standards': 95.0,
        'ISO Standards': 92.0,
        'ACM FAT* Guidelines': 90.0,
        'Research Benchmarks': 86.54,
        'Patent Novelty': 92.0
    }
    
    print("=" * 90)
    print("  GIG SYSTEM - GENERATING VISUALIZATIONS")
    print("=" * 90)
    print()
    
    # Create output directory path
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'visualizations')
    
    # Generate all visualizations
    visualizer.plot_score_comparison(recommendations, os.path.join(output_dir, 'scores_comparison.png'))
    visualizer.plot_esg_radar(recommendations, os.path.join(output_dir, 'esg_radar.png'))
    visualizer.plot_feature_importance(recommendations, os.path.join(output_dir, 'feature_importance.png'))
    visualizer.plot_blockchain_timeline(blockchain_data, os.path.join(output_dir, 'blockchain_timeline.png'))
    visualizer.plot_performance_metrics(metrics, os.path.join(output_dir, 'performance_metrics.png'))
    visualizer.plot_standards_compliance(compliance_data, os.path.join(output_dir, 'standards_compliance.png'))
    
    print()
    print("=" * 80)
    print("  ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("Output files (in visualizations/ folder):")
    print("  1. scores_comparison.png - Score comparison across recommendations")
    print("  2. esg_radar.png - ESG scores radar chart")
    print("  3. feature_importance.png - Feature importance heatmap")
    print("  4. blockchain_timeline.png - Blockchain integrity timeline")
    print("  5. performance_metrics.png - System performance dashboard")
    print("  6. standards_compliance.png - Standards compliance charts")
    print()


if __name__ == "__main__":
    generate_all_visualizations()
