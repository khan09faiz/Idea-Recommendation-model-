"""Context-Aware Weight Adaptation Module"""

from typing import Dict, Any


class ContextAwareWeightAdapter:
    """Dynamically adjusts ranking weights based on context"""
    
    def __init__(self):
        # Default weights for FinalScore formula
        self.base_weights = {
            "elo": 0.15,
            "bayesian_mean": 0.15,
            "uncertainty": 0.05,
            "sentiment": 0.10,
            "provenance": 0.10,
            "freshness": 0.10,
            "trend": 0.15,
            "causal_impact": 0.10,
            "serendipity": 0.10
        }
    
    def adapt_weights(self, context: Dict[str, Any]) -> Dict[str, float]:
        """
        Adapt weights based on domain, data quality, market conditions
        
        Args:
            context: Dictionary with keys:
                - domain: str (e.g., "healthcare", "technology")
                - market_volatility: float [0, 1]
                - data_quality: float [0, 1]
                - fairness_adjustment: bool
        
        Returns:
            Adapted weight dictionary
        """
        weights = self.base_weights.copy()
        
        # Domain-specific adjustments
        domain = context.get("domain", "general")
        if domain == "technology":
            weights["trend"] *= 1.3
            weights["serendipity"] *= 1.4
        elif domain == "healthcare":
            weights["provenance"] *= 1.5
            weights["uncertainty"] *= 1.3
        elif domain == "finance":
            weights["provenance"] *= 1.4
            weights["trend"] *= 1.2
        
        # Market volatility adjustments
        volatility = context.get("market_volatility", 0.5)
        if volatility > 0.7:
            weights["trend"] *= 1.3
            weights["freshness"] *= 1.2
            weights["elo"] *= 0.9
        
        # Data quality adjustments
        quality = context.get("data_quality", 0.8)
        if quality < 0.6:
            weights["provenance"] *= 1.3
            weights["uncertainty"] *= 1.4
        
        # Fairness adjustments
        if context.get("fairness_adjustment", False):
            weights["serendipity"] *= 1.3
            weights["provenance"] *= 0.8
        
        # Normalize to sum to 1.0
        total = sum(weights.values())
        return {k: v / total for k, v in weights.items()}
