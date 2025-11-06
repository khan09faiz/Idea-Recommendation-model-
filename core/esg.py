"""Sustainability and ESG Scoring Module"""

from typing import List, Dict, Any


class SustainabilityAndESGScorer:
    """Scores ideas on ESG (Environmental, Social, Governance)"""
    
    def __init__(self):
        self.esg_keywords = {
            "environmental": ["climate", "carbon", "renewable", "sustainable", "green", "eco"],
            "social": ["equity", "diversity", "inclusion", "community", "fair", "ethical"],
            "governance": ["transparency", "compliance", "accountability", "integrity", "audit"]
        }
    
    def compute_esg_score(self, idea) -> Dict[str, float]:
        """
        Compute ESG score from idea content
        
        Args:
            idea: Idea object
            
        Returns:
            Dictionary with E, S, G scores and total
        """
        text = (idea.title + " " + idea.description).lower()
        
        e_score = sum(1 for kw in self.esg_keywords["environmental"] if kw in text)
        s_score = sum(1 for kw in self.esg_keywords["social"] if kw in text)
        g_score = sum(1 for kw in self.esg_keywords["governance"] if kw in text)
        
        # Normalize to [0, 1]
        e_normalized = min(1.0, e_score / 3.0)
        s_normalized = min(1.0, s_score / 3.0)
        g_normalized = min(1.0, g_score / 3.0)
        
        total_score = (e_normalized + s_normalized + g_normalized) / 3.0
        
        return {
            "environmental": e_normalized,
            "social": s_normalized,
            "governance": g_normalized,
            "total_esg": total_score
        }
    
    def rank_by_esg(self, ideas: List, dimension: str = "total_esg") -> List[Dict[str, Any]]:
        """
        Rank ideas by ESG dimension
        
        Args:
            ideas: List of Idea objects
            dimension: ESG dimension (environmental, social, governance, total_esg)
            
        Returns:
            Sorted list of ideas with ESG scores
        """
        scored = []
        for idea in ideas:
            esg = self.compute_esg_score(idea)
            scored.append({
                "idea_id": idea.idea_id,
                "title": idea.title,
                "esg_scores": esg,
                "rank_score": esg.get(dimension, 0.0)
            })
        
        scored.sort(key=lambda x: x["rank_score"], reverse=True)
        return scored
    
    def aggregate_with_esg(self, final_score: float, esg_score: float,
                          esg_weight: float = 0.15) -> float:
        """
        Integrate ESG score into final ranking
        
        Args:
            final_score: Base final score
            esg_score: Total ESG score
            esg_weight: Weight for ESG component
            
        Returns:
            Adjusted final score
        """
        return final_score * (1 - esg_weight) + esg_score * esg_weight
