"""Counterfactual Ranking Engine Module"""

from typing import List, Dict, Any
import numpy as np


class CounterfactualRankingEngine:
    """Generates multiple 'what-if' ranking scenarios"""
    
    def __init__(self):
        self.scenarios = {}
    
    def generate_scenario(self, ideas: List, scenario_name: str,
                         weight_adjustments: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate ranking under different weight scenarios
        
        Args:
            ideas: List of Idea objects
            scenario_name: Name of scenario
            weight_adjustments: Weight multipliers (e.g., {"sentiment": 2.0})
            
        Returns:
            Reranked ideas list
        """
        scored_ideas = []
        
        for idea in ideas:
            # Default score components
            components = {
                "elo": idea.elo_score,
                "bayesian": idea.bayesian_mean,
                "uncertainty": idea.bayesian_std,
                "sentiment": idea.sentiment,
                "provenance": idea.provenance_score,
                "freshness": 1.0,  # Placeholder
                "trend": idea.trend_score,
                "causal": 0.0,  # Placeholder
                "serendipity": 0.0  # Placeholder
            }
            
            # Apply adjustments
            base_weights = {
                "elo": 0.15,
                "bayesian": 0.15,
                "uncertainty": 0.05,
                "sentiment": 0.15,
                "provenance": 0.1,
                "freshness": 0.1,
                "trend": 0.15,
                "causal": 0.1,
                "serendipity": 0.05
            }
            
            adjusted_weights = {}
            for k, v in base_weights.items():
                multiplier = weight_adjustments.get(k, 1.0)
                adjusted_weights[k] = v * multiplier
            
            # Renormalize
            total = sum(adjusted_weights.values())
            adjusted_weights = {k: v / total for k, v in adjusted_weights.items()}
            
            # Calculate score
            score = sum(components[k] * adjusted_weights[k] for k in components.keys())
            
            scored_ideas.append({
                "idea_id": idea.idea_id,
                "title": idea.title,
                "score": score,
                "components": components,
                "weights": adjusted_weights
            })
        
        # Sort descending
        scored_ideas.sort(key=lambda x: x["score"], reverse=True)
        
        # Store scenario
        self.scenarios[scenario_name] = scored_ideas
        
        return scored_ideas
    
    def compare_scenarios(self, scenario_names: List[str]) -> Dict[str, Any]:
        """
        Compare ranking stability across scenarios
        
        Args:
            scenario_names: List of scenario names to compare
            
        Returns:
            Comparison report
        """
        if not scenario_names or not all(s in self.scenarios for s in scenario_names):
            return {"error": "Invalid scenario names"}
        
        # Extract rankings
        rankings = {}
        for name in scenario_names:
            rankings[name] = [item["idea_id"] for item in self.scenarios[name]]
        
        # Calculate rank correlation (Kendall tau simplified)
        correlations = {}
        for i, s1 in enumerate(scenario_names):
            for s2 in scenario_names[i+1:]:
                rank1 = rankings[s1]
                rank2 = rankings[s2]
                
                # Count inversions
                inversions = 0
                for idx1, id1 in enumerate(rank1):
                    for idx2, id2 in enumerate(rank1[idx1+1:], start=idx1+1):
                        if id1 in rank2 and id2 in rank2:
                            pos1_s2 = rank2.index(id1)
                            pos2_s2 = rank2.index(id2)
                            if pos1_s2 > pos2_s2:
                                inversions += 1
                
                total_pairs = len(rank1) * (len(rank1) - 1) / 2
                correlation = 1 - (2 * inversions / total_pairs) if total_pairs > 0 else 1.0
                correlations[f"{s1}_vs_{s2}"] = correlation
        
        return {
            "scenarios": scenario_names,
            "correlations": correlations,
            "average_correlation": np.mean(list(correlations.values())) if correlations else 0.0
        }
    
    def sensitivity_analysis(self, ideas: List, feature: str) -> List[Dict[str, Any]]:
        """
        Analyze sensitivity to single feature perturbation
        
        Args:
            ideas: List of Idea objects
            feature: Feature name to perturb
            
        Returns:
            Sensitivity results
        """
        results = []
        
        for delta in [-0.2, -0.1, 0.0, 0.1, 0.2]:
            scenario_name = f"{feature}_delta_{delta}"
            weight_adjustments = {feature: 1.0 + delta}
            ranked = self.generate_scenario(ideas, scenario_name, weight_adjustments)
            
            results.append({
                "delta": delta,
                "top_5": [r["idea_id"] for r in ranked[:5]],
                "avg_score": np.mean([r["score"] for r in ranked])
            })
        
        return results
