"""Idea Twin Generator - Generates counterfactual twin variants"""

from typing import Dict, List, Any
import numpy as np
import hashlib


class IdeaTwinGenerator:
    """
    Generates "counterfactual twin" idea variants predicted to rank higher.
    Creates synthetic variations by perturbing features.
    """
    
    def __init__(self):
        """Initialize twin generator"""
        self.twin_history = []
        
    def generate_twin(self, idea_id: str, original_idea: Dict[str, Any],
                     target_improvement: float = 0.2) -> Dict[str, Any]:
        """
        Generate a counterfactual twin idea predicted to rank higher.
        
        Args:
            idea_id: Original idea identifier
            original_idea: Dictionary with idea features
            target_improvement: Target score improvement [0, 1]
            
        Returns:
            Dictionary with twin idea and predicted improvements
            
        Security: Validates inputs, safe perturbations
        """
        # Input validation
        safe_idea_id = str(idea_id)[:100]
        target_improvement = max(0.0, min(1.0, float(target_improvement)))
        
        if not original_idea or not isinstance(original_idea, dict):
            return {"error": "Invalid original idea"}
        
        # Generate twin by improving key features
        twin_features = self._perturb_features(original_idea, target_improvement)
        
        # Generate twin ID
        twin_id = self._generate_twin_id(safe_idea_id)
        
        # Predict performance improvement
        predicted_score = self._predict_twin_score(original_idea, twin_features)
        
        # Generate explanation
        improvements = self._explain_improvements(original_idea, twin_features)
        
        twin = {
            "twin_id": twin_id,
            "original_id": safe_idea_id,
            "twin_features": twin_features,
            "predicted_score_improvement": float(predicted_score),
            "improvements": improvements,
            "twin_title": self._generate_twin_title(original_idea, improvements),
            "twin_description": self._generate_twin_description(original_idea, improvements)
        }
        
        # Record in history
        self.twin_history.append({
            "original_id": safe_idea_id,
            "twin_id": twin_id,
            "target_improvement": target_improvement
        })
        
        return twin
    
    def compare_performance(self, original_idea: Dict[str, Any],
                          twin_idea: Dict[str, Any],
                          ranking_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Compare performance between original and twin.
        
        Args:
            original_idea: Original idea dictionary
            twin_idea: Twin idea dictionary
            ranking_scores: Score components dictionary
            
        Returns:
            Comparison dictionary
            
        Security: Safe comparison calculations
        """
        # Extract scores
        original_score = original_idea.get("final_score", 0.0)
        twin_score = twin_idea.get("predicted_score_improvement", 0.0)
        
        # Calculate actual improvement
        actual_improvement = twin_score - original_score
        improvement_percentage = (actual_improvement / original_score * 100) if original_score > 0 else 0
        
        # Component-wise comparison
        component_improvements = {}
        for component, score in ranking_scores.items():
            original_component = original_idea.get(component, 0.0)
            twin_features = twin_idea.get("twin_features", {})
            twin_component = twin_features.get(component, original_component)
            
            if isinstance(original_component, (int, float)) and isinstance(twin_component, (int, float)):
                delta = twin_component - original_component
                component_improvements[component] = {
                    "original": float(original_component),
                    "twin": float(twin_component),
                    "delta": float(delta),
                    "improvement_pct": (delta / original_component * 100) if original_component != 0 else 0
                }
        
        return {
            "original_score": float(original_score),
            "twin_score": float(twin_score),
            "actual_improvement": float(actual_improvement),
            "improvement_percentage": float(improvement_percentage),
            "component_improvements": component_improvements,
            "recommendation": self._generate_recommendation(actual_improvement)
        }
    
    def _perturb_features(self, original: Dict[str, Any], 
                         target_improvement: float) -> Dict[str, float]:
        """
        Perturb features to create improved twin.
        
        Security: Bounded perturbations, validates ranges
        """
        twin = {}
        
        # Features to improve
        improvable_features = {
            "sentiment": target_improvement * 0.3,
            "trend": target_improvement * 0.25,
            "feasibility_score": target_improvement * 0.2,
            "esg_total": target_improvement * 0.15,
            "provenance": target_improvement * 0.1
        }
        
        for feature, improvement in improvable_features.items():
            original_value = original.get(feature, 0.5)
            
            # Validate original value
            if not isinstance(original_value, (int, float)):
                original_value = 0.5
            
            # Apply improvement
            new_value = min(1.0, original_value + improvement)
            twin[feature] = float(new_value)
        
        # Copy unchanged features
        for key, value in original.items():
            if key not in twin and isinstance(value, (int, float, str)):
                twin[key] = value
        
        return twin
    
    def _predict_twin_score(self, original: Dict[str, Any],
                           twin: Dict[str, float]) -> float:
        """
        Predict score improvement for twin.
        
        Security: Safe arithmetic, bounded output
        """
        original_score = original.get("final_score", 0.5)
        
        # Calculate weighted improvement across features
        improvement = 0.0
        weights = {
            "sentiment": 0.15,
            "trend": 0.15,
            "feasibility_score": 0.2,
            "esg_total": 0.15,
            "provenance": 0.1
        }
        
        for feature, weight in weights.items():
            orig_val = original.get(feature, 0.5)
            twin_val = twin.get(feature, orig_val)
            
            if isinstance(orig_val, (int, float)) and isinstance(twin_val, (int, float)):
                delta = twin_val - orig_val
                improvement += delta * weight
        
        # Predicted new score
        predicted = original_score + improvement
        
        return float(np.clip(predicted, 0.0, 1.0))
    
    def _explain_improvements(self, original: Dict[str, Any],
                            twin: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate human-readable improvement explanations"""
        improvements = []
        
        feature_names = {
            "sentiment": "Sentiment Score",
            "trend": "Market Trend Alignment",
            "feasibility_score": "Economic Feasibility",
            "esg_total": "ESG Impact",
            "provenance": "Data Source Quality"
        }
        
        for feature, readable_name in feature_names.items():
            orig_val = original.get(feature, 0.5)
            twin_val = twin.get(feature, orig_val)
            
            if isinstance(orig_val, (int, float)) and isinstance(twin_val, (int, float)):
                delta = twin_val - orig_val
                
                if delta > 0.01:  # Only significant improvements
                    improvements.append({
                        "feature": feature,
                        "name": readable_name,
                        "original": float(orig_val),
                        "improved": float(twin_val),
                        "delta": float(delta),
                        "explanation": f"Improved {readable_name} from {orig_val:.2f} to {twin_val:.2f}"
                    })
        
        # Sort by delta descending
        improvements.sort(key=lambda x: x["delta"], reverse=True)
        
        return improvements
    
    def _generate_twin_title(self, original: Dict[str, Any],
                            improvements: List[Dict[str, Any]]) -> str:
        """Generate title for twin idea"""
        original_title = original.get("title", "Idea")
        
        if improvements:
            top_improvement = improvements[0]["name"]
            return f"Enhanced {original_title} (Optimized for {top_improvement})"
        else:
            return f"Enhanced {original_title}"
    
    def _generate_twin_description(self, original: Dict[str, Any],
                                   improvements: List[Dict[str, Any]]) -> str:
        """Generate description for twin idea"""
        original_desc = original.get("description", "")
        
        improvement_text = "This enhanced version improves: "
        improvement_list = [imp["name"] for imp in improvements[:3]]
        improvement_text += ", ".join(improvement_list)
        
        return f"{original_desc}\n\n[Twin Enhancement]: {improvement_text}"
    
    def _generate_twin_id(self, original_id: str) -> str:
        """Generate unique ID for twin"""
        twin_seed = f"{original_id}_twin_{np.random.randint(1000, 9999)}"
        return hashlib.sha256(twin_seed.encode()).hexdigest()[:16]
    
    def _generate_recommendation(self, improvement: float) -> str:
        """Generate recommendation based on improvement"""
        if improvement > 0.2:
            return "Significant improvement - strong twin candidate"
        elif improvement > 0.1:
            return "Moderate improvement - viable twin"
        elif improvement > 0.0:
            return "Minor improvement - marginal twin"
        else:
            return "No improvement - twin not recommended"
