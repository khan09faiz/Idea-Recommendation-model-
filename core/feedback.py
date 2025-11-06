"""User Feedback and Fine-Tuning Module"""

from datetime import datetime
from typing import Dict, List
import numpy as np


class UserFeedbackFineTuner:
    """Collects feedback and fine-tunes ranking parameters"""
    
    def __init__(self, learning_rate: float = 0.1):
        """
        Initialize feedback system
        
        Args:
            learning_rate: Learning rate for parameter updates
        """
        self.learning_rate = learning_rate
        self.feedback_history: List[Dict] = []
    
    def collect_feedback(self, idea_id: str, relevance: float, novelty: float,
                        feasibility: float, usefulness: float,
                        implicit_signal: Dict = None):
        """
        Collect explicit and implicit user feedback
        
        Args:
            idea_id: Idea identifier
            relevance: Relevance rating ∈ [0, 1]
            novelty: Novelty rating ∈ [0, 1]
            feasibility: Feasibility rating ∈ [0, 1]
            usefulness: Usefulness rating ∈ [0, 1]
            implicit_signal: Optional dict with clicks, time_spent, etc.
        """
        feedback = {
            "idea_id": idea_id,
            "relevance": relevance,
            "novelty": novelty,
            "feasibility": feasibility,
            "usefulness": usefulness,
            "implicit": implicit_signal or {},
            "timestamp": datetime.now()
        }
        self.feedback_history.append(feedback)
    
    def update_idea_parameters(self, idea, feedback: Dict):
        """
        Update Elo and Bayesian parameters based on feedback
        
        Args:
            idea: Idea object
            feedback: Feedback dictionary
            
        Returns:
            Updated idea object
        """
        # Aggregate feedback score
        avg_score = (
            feedback["relevance"] + feedback["novelty"] +
            feedback["feasibility"] + feedback["usefulness"]
        ) / 4.0
        
        # Update Elo rating (treat as competitive match)
        expected = 1.0 / (1.0 + 10 ** ((1500 - idea.elo_rating) / 400))
        idea.elo_rating += 32 * (avg_score - expected)
        
        # Update Bayesian mean (exponential moving average)
        idea.bayesian_mean = (
            (1 - self.learning_rate) * idea.bayesian_mean +
            self.learning_rate * avg_score
        )
        
        # Reduce uncertainty with more feedback
        idea.uncertainty *= 0.95
        
        return idea
    
    def get_feedback_stats(self, idea_id: str) -> Dict:
        """
        Get aggregated feedback statistics for an idea
        
        Args:
            idea_id: Idea identifier
            
        Returns:
            Statistics dictionary
        """
        feedbacks = [f for f in self.feedback_history if f["idea_id"] == idea_id]
        
        if not feedbacks:
            return {"count": 0}
        
        return {
            "count": len(feedbacks),
            "avg_relevance": np.mean([f["relevance"] for f in feedbacks]),
            "avg_novelty": np.mean([f["novelty"] for f in feedbacks]),
            "avg_feasibility": np.mean([f["feasibility"] for f in feedbacks]),
            "avg_usefulness": np.mean([f["usefulness"] for f in feedbacks])
        }
    
    def fine_tune_weights(self, current_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Fine-tune ranking weights based on accumulated feedback
        
        Args:
            current_weights: Current weight dictionary
            
        Returns:
            Adjusted weights
        """
        if not self.feedback_history:
            return current_weights
        
        # Simple gradient-based adjustment
        # Ideas with high relevance boost corresponding weights
        avg_relevance = np.mean([f["relevance"] for f in self.feedback_history])
        
        adjusted = current_weights.copy()
        if avg_relevance < 0.5:
            # Boost provenance and trend if relevance is low
            adjusted["provenance"] *= 1.1
            adjusted["trend"] *= 1.1
        
        # Normalize
        total = sum(adjusted.values())
        return {k: v / total for k, v in adjusted.items()}
