"""Multi-Focused View Ranking Module"""

from typing import List, Dict, Tuple
from collections import defaultdict


class MultiFocusedViewRanker:
    """Provides multiple ranking perspectives and consensus blending"""
    
    def __init__(self):
        # Define different view perspectives
        self.views = {
            "user_focused": {
                "elo": 0.3,
                "bayesian_mean": 0.3,
                "sentiment": 0.2,
                "freshness": 0.2
            },
            "market_focused": {
                "trend": 0.4,
                "provenance": 0.3,
                "causal_impact": 0.3
            },
            "swot_focused": {
                "bayesian_mean": 0.25,
                "uncertainty": 0.15,
                "provenance": 0.3,
                "causal_impact": 0.3
            }
        }
    
    def rank_by_view(self, ideas: List, view: str, scores: Dict[str, Dict[str, float]]) -> List[Tuple[str, float]]:
        """
        Rank ideas according to specific perspective
        
        Args:
            ideas: List of Idea objects
            view: View name ("user_focused", "market_focused", "swot_focused")
            scores: Dictionary mapping idea_id to score components
            
        Returns:
            List of (idea_id, view_score) tuples, sorted descending
        """
        if view not in self.views:
            view = "user_focused"
        
        weights = self.views[view]
        ranked = []
        
        for idea in ideas:
            idea_scores = scores.get(idea.idea_id, {})
            view_score = sum(
                weights.get(k, 0) * idea_scores.get(k, 0)
                for k in weights
            )
            ranked.append((idea.idea_id, view_score))
        
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked
    
    def blend_views(self, view_rankings: Dict[str, List[Tuple[str, float]]],
                   blend_weights: Dict[str, float] = None) -> List[Tuple[str, float]]:
        """
        Blend multiple view rankings into consensus ranking
        
        Args:
            view_rankings: Dictionary mapping view name to ranking list
            blend_weights: Optional custom blend weights per view
            
        Returns:
            Consensus ranking list
        """
        if blend_weights is None:
            # Equal weight for all views
            blend_weights = {view: 1.0 / len(view_rankings) for view in view_rankings}
        
        # Aggregate scores across views
        aggregated = defaultdict(float)
        for view, rankings in view_rankings.items():
            weight = blend_weights.get(view, 0.0)
            for idea_id, score in rankings:
                aggregated[idea_id] += weight * score
        
        # Sort by aggregated score
        final = [(idea_id, score) for idea_id, score in aggregated.items()]
        final.sort(key=lambda x: x[1], reverse=True)
        return final
