"""Economic Feasibility Analyzer - ROI & Risk Assessment"""

from typing import Dict, Any, Tuple
import numpy as np


class EconomicFeasibilityAnalyzer:
    """
    Analyzes economic feasibility with ROI and risk assessment.
    Implements Pareto optimization between ROI and risk.
    """
    
    def __init__(self):
        """Initialize feasibility analyzer"""
        self.roi_history = []
        self.risk_history = []
        
    def estimate_roi(self, idea_features: Dict[str, float]) -> float:
        """
        Estimate Return on Investment.
        
        Args:
            idea_features: Dictionary with keys like 'market_size', 'cost', 'revenue_potential'
            
        Returns:
            ROI score [0, 1]
            
        Security: Validates inputs and prevents division by zero
        """
        # Input validation
        if not idea_features:
            return 0.5  # Neutral default
        
        # Extract relevant features with safe defaults
        market_size = self._safe_extract(idea_features, 'market_size', 0.5)
        revenue_potential = self._safe_extract(idea_features, 'revenue_potential', 0.5)
        cost = self._safe_extract(idea_features, 'cost', 0.5)
        trend_score = self._safe_extract(idea_features, 'trend', 0.5)
        sentiment = self._safe_extract(idea_features, 'sentiment', 0.0)
        
        # Normalize sentiment from [-1, 1] to [0, 1]
        sentiment_norm = (sentiment + 1.0) / 2.0
        
        # Calculate ROI with weighted components
        # Higher market size and revenue, lower cost = higher ROI
        roi_raw = (
            0.3 * market_size +
            0.3 * revenue_potential +
            0.2 * (1.0 - cost) +  # Inverse cost
            0.1 * trend_score +
            0.1 * sentiment_norm
        )
        
        # Apply sigmoid for smoothing
        roi = 1.0 / (1.0 + np.exp(-5 * (roi_raw - 0.5)))
        
        return float(np.clip(roi, 0.0, 1.0))
    
    def estimate_risk(self, idea_features: Dict[str, float]) -> float:
        """
        Estimate risk level.
        
        Args:
            idea_features: Dictionary with risk indicators
            
        Returns:
            Risk score [0, 1] where higher = more risky
            
        Security: Validates inputs and range
        """
        if not idea_features:
            return 0.5  # Neutral default
        
        # Extract risk factors
        uncertainty = self._safe_extract(idea_features, 'uncertainty', 0.3)
        complexity = self._safe_extract(idea_features, 'complexity', 0.5)
        market_volatility = self._safe_extract(idea_features, 'volatility', 0.5)
        regulatory_risk = self._safe_extract(idea_features, 'regulatory_risk', 0.3)
        
        # Lower provenance = higher risk
        provenance = self._safe_extract(idea_features, 'provenance', 0.7)
        provenance_risk = 1.0 - provenance
        
        # Aggregate risk score
        risk_raw = (
            0.25 * uncertainty +
            0.2 * complexity +
            0.2 * market_volatility +
            0.15 * regulatory_risk +
            0.2 * provenance_risk
        )
        
        return float(np.clip(risk_raw, 0.0, 1.0))
    
    def compute_pareto_score(self, roi: float, risk: float) -> float:
        """
        Compute Pareto-optimal score balancing ROI and risk.
        
        Args:
            roi: ROI score [0, 1]
            risk: Risk score [0, 1]
            
        Returns:
            Pareto score [0, 1]
            
        Security: Validates input ranges
        """
        # Input validation
        roi = float(np.clip(roi, 0.0, 1.0))
        risk = float(np.clip(risk, 0.0, 1.0))
        
        # Pareto optimization: maximize ROI, minimize risk
        # Using risk-adjusted return concept
        if risk > 0.9:
            # Very high risk - heavy penalty
            pareto = roi * 0.1
        else:
            # Risk-adjusted ROI with diminishing penalty
            risk_penalty = 1.0 - (risk * 0.7)  # Risk reduces score by up to 70%
            pareto = roi * risk_penalty
        
        return float(np.clip(pareto, 0.0, 1.0))
    
    def analyze_feasibility(self, idea_features: Dict[str, float]) -> Dict[str, Any]:
        """
        Complete feasibility analysis.
        
        Args:
            idea_features: Dictionary of idea features
            
        Returns:
            Dictionary with ROI, risk, Pareto score, and explanation
            
        Security: Comprehensive input validation
        """
        # Estimate components
        roi = self.estimate_roi(idea_features)
        risk = self.estimate_risk(idea_features)
        pareto = self.compute_pareto_score(roi, risk)
        
        # Store history
        self.roi_history.append(roi)
        self.risk_history.append(risk)
        
        # Generate explanation
        risk_level = "Low" if risk < 0.3 else "Medium" if risk < 0.7 else "High"
        roi_level = "Low" if roi < 0.3 else "Medium" if roi < 0.7 else "High"
        
        recommendation = self._generate_recommendation(roi, risk, pareto)
        
        return {
            "roi": float(roi),
            "risk": float(risk),
            "pareto_score": float(pareto),
            "feasibility_score": float(pareto),  # Alias for integration
            "roi_level": roi_level,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "explanation": f"ROI: {roi_level} ({roi:.2f}), Risk: {risk_level} ({risk:.2f})"
        }
    
    def _safe_extract(self, features: Dict[str, float], key: str, default: float) -> float:
        """
        Safely extract and validate feature value.
        
        Args:
            features: Feature dictionary
            key: Key to extract
            default: Default value if missing
            
        Returns:
            Validated float value
        """
        value = features.get(key, default)
        
        # Validate type
        if not isinstance(value, (int, float)):
            return default
        
        # Validate range
        if not np.isfinite(value):
            return default
        
        return float(np.clip(value, 0.0, 1.0))
    
    def _generate_recommendation(self, roi: float, risk: float, pareto: float) -> str:
        """Generate investment recommendation"""
        if pareto > 0.7:
            return "Strong investment candidate"
        elif pareto > 0.5:
            if risk > 0.6:
                return "Promising but requires risk mitigation"
            else:
                return "Good investment candidate"
        elif pareto > 0.3:
            return "Moderate potential - proceed with caution"
        else:
            return "High risk or low return - not recommended"
