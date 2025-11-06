"""Fairness and Robustness Module"""

from typing import List, Dict, Any
from collections import defaultdict


class FairnessAndRobustnessModule:
    """Detects bias, ensures fairness, filters adversarial inputs"""
    
    def __init__(self):
        self.bias_thresholds = {
            "source_imbalance": 0.7,
            "domain_concentration": 0.6
        }
    
    def detect_bias(self, ideas: List) -> Dict[str, Any]:
        """
        Detect bias by source, domain, or other attributes
        
        Args:
            ideas: List of Idea objects
            
        Returns:
            Bias detection report
        """
        if not ideas:
            return {"bias_detected": False}
        
        # Source distribution (using provenance as proxy)
        prov_scores = [idea.provenance_score for idea in ideas]
        high_prov = sum(1 for p in prov_scores if p > 0.7)
        source_imbalance = high_prov / len(ideas)
        
        # Tag/domain concentration
        all_tags = []
        for idea in ideas:
            all_tags.extend(idea.tags)
        
        if all_tags:
            tag_counts = defaultdict(int)
            for tag in all_tags:
                tag_counts[tag] += 1
            max_tag_ratio = max(tag_counts.values()) / len(all_tags)
        else:
            max_tag_ratio = 0
        
        bias_detected = (
            source_imbalance > self.bias_thresholds["source_imbalance"] or
            max_tag_ratio > self.bias_thresholds["domain_concentration"]
        )
        
        return {
            "bias_detected": bias_detected,
            "source_imbalance": source_imbalance,
            "domain_concentration": max_tag_ratio,
            "recommendations": [
                "Increase diversity in data sources",
                "Balance representation across domains"
            ] if bias_detected else []
        }
    
    def filter_adversarial(self, idea) -> bool:
        """
        Detect spammy or manipulative inputs
        
        Args:
            idea: Idea object
            
        Returns:
            True if legitimate, False if adversarial
        """
        # Check for keyword stuffing
        words = idea.description.lower().split()
        if len(words) > 10:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:
                return False
        
        # Check for unrealistic scores
        if idea.sentiment > 0.95 and idea.trend_score > 0.95:
            return False
        
        # Check for empty content
        if len(idea.description.strip()) < 20:
            return False
        
        return True
    
    def rebalance_weights(self, weights: Dict[str, float],
                         bias_report: Dict[str, Any]) -> Dict[str, float]:
        """
        Adjust weights to mitigate detected bias
        
        Args:
            weights: Current weight dictionary
            bias_report: Bias detection report
            
        Returns:
            Rebalanced weights
        """
        if not bias_report["bias_detected"]:
            return weights
        
        adjusted = weights.copy()
        
        # Reduce provenance weight if source imbalance
        if bias_report["source_imbalance"] > self.bias_thresholds["source_imbalance"]:
            adjusted["provenance"] *= 0.7
            adjusted["serendipity"] *= 1.3
        
        # Boost diversity if domain concentration
        if bias_report["domain_concentration"] > self.bias_thresholds["domain_concentration"]:
            adjusted["serendipity"] *= 1.4
        
        # Renormalize
        total = sum(adjusted.values())
        return {k: v / total for k, v in adjusted.items()}
