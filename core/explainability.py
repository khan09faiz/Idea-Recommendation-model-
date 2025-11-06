"""Explainability Engine Module"""

from typing import List, Dict, Any
from datetime import datetime


class ExplainabilityEngine:
    """Generates counterfactual explanations and feature importance"""
    
    def __init__(self):
        self.explanation_ratings = []
    
    def generate_counterfactuals(self, idea, current_rank: int,
                                scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate 'what-if' counterfactual scenarios
        
        Args:
            idea: Idea object
            current_rank: Current ranking position
            scores: Score components dictionary
            
        Returns:
            List of counterfactual explanations
        """
        counterfactuals = []
        
        # Sentiment perturbation
        if "sentiment" in scores:
            delta = 0.2
            new_val = min(1.0, scores["sentiment"] + delta)
            rank_change = int((new_val - scores["sentiment"]) * 15)
            counterfactuals.append({
                "feature": "sentiment",
                "current_value": scores["sentiment"],
                "new_value": new_val,
                "change": f"+{delta}",
                "rank_change": f"+{rank_change}",
                "explanation": f"If sentiment increased by {delta}, rank would improve by ~{rank_change} positions"
            })
        
        # Trend perturbation
        if "trend" in scores:
            delta = 0.15
            new_val = min(1.0, scores["trend"] + delta)
            rank_change = int((new_val - scores["trend"]) * 20)
            counterfactuals.append({
                "feature": "trend",
                "current_value": scores["trend"],
                "new_value": new_val,
                "change": f"+{delta}",
                "rank_change": f"+{rank_change}",
                "explanation": f"If market trend score increased by {delta}, rank would improve by ~{rank_change} positions"
            })
        
        # Provenance perturbation
        if "provenance" in scores:
            delta = 0.2
            new_val = min(1.0, scores["provenance"] + delta)
            rank_change = int((new_val - scores["provenance"]) * 12)
            counterfactuals.append({
                "feature": "provenance",
                "current_value": scores["provenance"],
                "new_value": new_val,
                "change": f"+{delta}",
                "rank_change": f"+{rank_change}",
                "explanation": f"If data source quality improved by {delta}, rank would improve by ~{rank_change} positions"
            })
        
        return counterfactuals
    
    def explain_top_features(self, scores: Dict[str, float],
                           weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Identify and explain top contributing features
        
        Args:
            scores: Score components
            weights: Weight coefficients
            
        Returns:
            List of feature contributions
        """
        contributions = []
        
        for feature, score in scores.items():
            weight = weights.get(feature, 0.0)
            contribution = score * weight
            contributions.append({
                "feature": feature,
                "score": score,
                "weight": weight,
                "contribution": contribution,
                "explanation": f"{feature}: {score:.3f} × {weight:.3f} = {contribution:.3f}"
            })
        
        # Sort by contribution descending
        contributions.sort(key=lambda x: x["contribution"], reverse=True)
        return contributions[:5]
    
    def generate_factor_breakdown(self, scores: Dict[str, float],
                                  weights: Dict[str, float],
                                  final_score: float) -> Dict[str, Any]:
        """
        Generate JSON-style factor breakdown
        
        Args:
            scores: Score components
            weights: Weight coefficients
            final_score: Computed final score
            
        Returns:
            Breakdown dictionary
        """
        breakdown = {
            "FinalScore": final_score,
            "Components": {}
        }
        
        for feature, score in scores.items():
            weight = weights.get(feature, 0.0)
            contribution = score * weight
            breakdown["Components"][feature] = {
                "value": score,
                "weight": weight,
                "contribution": contribution,
                "percentage": (contribution / final_score * 100) if final_score > 0 else 0
            }
        
        return breakdown
    
    def collect_explanation_rating(self, idea_id: str, rating: float):
        """
        Collect user feedback on explanation clarity
        
        Args:
            idea_id: Idea identifier
            rating: Clarity rating ∈ [0, 1]
        """
        self.explanation_ratings.append({
            "idea_id": idea_id,
            "rating": rating,
            "timestamp": datetime.now()
        })
