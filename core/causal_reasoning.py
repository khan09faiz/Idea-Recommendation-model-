"""Causal Reasoning Module - Identifies true drivers of success"""

from typing import Dict, List, Any, Optional
import numpy as np
from collections import defaultdict


class CausalReasoningModule:
    """
    Lightweight causal inference for identifying success drivers.
    Uses simplified Bayesian network approach without heavy dependencies.
    """
    
    def __init__(self):
        """Initialize causal reasoning module"""
        self.causal_graph = {}  # variable -> list of parents
        self.conditional_probs = {}  # P(X|Parents(X))
        self.causal_effects = {}  # (cause, effect) -> impact score
        
    def fit_causal_model(self, features: Dict[str, List[float]], 
                        outcomes: List[float]) -> None:
        """
        Fit causal model from features to outcomes.
        
        Args:
            features: Dictionary of feature_name -> [values]
            outcomes: List of outcome values
            
        Security: Validates input types and ranges
        """
        # Input validation
        if not features or not outcomes:
            raise ValueError("Features and outcomes cannot be empty")
        
        feature_lengths = [len(v) for v in features.values()]
        if len(set(feature_lengths + [len(outcomes)])) > 1:
            raise ValueError("All features and outcomes must have same length")
        
        # Build simplified causal structure using correlation
        n_samples = len(outcomes)
        outcome_array = np.array(outcomes)
        
        for feature_name, feature_values in features.items():
            feature_array = np.array(feature_values)
            
            # Validate ranges
            if not np.all(np.isfinite(feature_array)):
                raise ValueError(f"Feature {feature_name} contains invalid values")
            
            # Calculate correlation as proxy for causal strength
            if np.std(feature_array) > 0 and np.std(outcome_array) > 0:
                correlation = np.corrcoef(feature_array, outcome_array)[0, 1]
                
                # Store causal effect estimate
                self.causal_effects[(feature_name, "outcome")] = abs(correlation)
                
                # Store in graph
                if "outcome" not in self.causal_graph:
                    self.causal_graph["outcome"] = []
                if abs(correlation) > 0.3:  # Threshold for significance
                    self.causal_graph["outcome"].append(feature_name)
    
    def estimate_causal_effect(self, variable_a: str, variable_b: str) -> float:
        """
        Estimate causal effect from variable_a to variable_b.
        
        Args:
            variable_a: Cause variable
            variable_b: Effect variable
            
        Returns:
            Causal effect magnitude [0, 1]
            
        Security: Returns 0 for invalid variable names
        """
        # Input validation
        if not isinstance(variable_a, str) or not isinstance(variable_b, str):
            return 0.0
        
        effect = self.causal_effects.get((variable_a, variable_b), 0.0)
        
        # Validate output range
        return max(0.0, min(1.0, effect))
    
    def explain_causal_path(self, idea_id: str, 
                           idea_features: Dict[str, float]) -> Dict[str, Any]:
        """
        Explain causal path from features to outcome for an idea.
        
        Args:
            idea_id: Idea identifier
            idea_features: Dictionary of feature values for this idea
            
        Returns:
            Dictionary with causal explanation
            
        Security: Sanitizes idea_id and validates features
        """
        # Input sanitization
        safe_idea_id = str(idea_id)[:100]  # Limit length
        
        if not idea_features:
            return {
                "idea_id": safe_idea_id,
                "causal_paths": [],
                "total_causal_impact": 0.0
            }
        
        causal_paths = []
        total_impact = 0.0
        
        # Build causal explanation
        for feature_name, feature_value in idea_features.items():
            # Validate feature value
            if not isinstance(feature_value, (int, float)) or not np.isfinite(feature_value):
                continue
            
            effect = self.estimate_causal_effect(feature_name, "outcome")
            
            if effect > 0.1:  # Only include significant effects
                contribution = effect * feature_value
                total_impact += contribution
                
                causal_paths.append({
                    "feature": feature_name,
                    "value": float(feature_value),
                    "causal_strength": float(effect),
                    "contribution": float(contribution),
                    "explanation": f"{feature_name} causally contributes {contribution:.3f} to outcome"
                })
        
        # Sort by contribution
        causal_paths.sort(key=lambda x: x["contribution"], reverse=True)
        
        return {
            "idea_id": safe_idea_id,
            "causal_paths": causal_paths[:5],  # Top 5 paths
            "total_causal_impact": float(total_impact),
            "causal_confidence": min(1.0, total_impact)
        }
    
    def compute_causal_impact_score(self, idea_features: Dict[str, float]) -> float:
        """
        Compute overall causal impact score for an idea.
        
        Args:
            idea_features: Dictionary of feature values
            
        Returns:
            Causal impact score [0, 1]
            
        Security: Validates all inputs and clamps output
        """
        explanation = self.explain_causal_path("temp", idea_features)
        score = explanation["total_causal_impact"]
        
        # Normalize and clamp
        normalized = score / (1.0 + score)  # Sigmoid-like normalization
        return max(0.0, min(1.0, normalized))
