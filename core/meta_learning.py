"""Meta-Learning Optimizer - Self-adjusting α-weights via Bayesian optimization"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from datetime import datetime


class MetaLearningOptimizer:
    """
    Self-adjusts α-weights using Bayesian optimization.
    Optimizes for ranking metrics like nDCG, Precision, Recall.
    """
    
    def __init__(self, weight_bounds: Optional[Dict[str, Tuple[float, float]]] = None):
        """
        Initialize meta-learning optimizer.
        
        Args:
            weight_bounds: Dictionary of weight_name -> (min, max) bounds
            
        Security: Validates bounds
        """
        self.weight_bounds = weight_bounds or {
            "elo": (0.05, 0.25),
            "bayesian": (0.05, 0.25),
            "uncertainty": (0.01, 0.15),
            "sentiment": (0.05, 0.25),
            "provenance": (0.05, 0.20),
            "freshness": (0.05, 0.20),
            "trend": (0.05, 0.25),
            "causal": (0.05, 0.20),
            "serendipity": (0.01, 0.15)
        }
        
        self.optimization_history = []
        self.best_weights = None
        self.best_metric = -np.inf
        
    def optimize_weights(self, ranking_function, 
                        ground_truth: List[str],
                        ideas: List[Any],
                        metric: str = "ndcg",
                        n_iterations: int = 50) -> Dict[str, float]:
        """
        Optimize α-weights using Bayesian optimization.
        
        Args:
            ranking_function: Function that takes weights and returns ranked idea IDs
            ground_truth: Ground truth ideal ranking (list of idea IDs)
            ideas: List of idea objects
            metric: Optimization metric (ndcg, precision, recall)
            n_iterations: Number of optimization iterations
            
        Returns:
            Optimized weights dictionary
            
        Security: Validates inputs, safe function calls
        """
        # Input validation
        if not ground_truth or not ideas:
            return self._get_default_weights()
        
        n_iterations = max(10, min(200, n_iterations))
        
        # Initialize with random samples
        for i in range(n_iterations):
            # Sample weights from bounds
            weights = self._sample_weights()
            
            # Normalize to sum to 1.0
            weights = self._normalize_weights(weights)
            
            try:
                # Get ranking with these weights
                ranked_ids = ranking_function(weights, ideas)
                
                # Calculate metric
                score = self._calculate_metric(ranked_ids, ground_truth, metric)
                
                # Update best if improved
                if score > self.best_metric:
                    self.best_metric = score
                    self.best_weights = weights.copy()
                
                # Record history
                self.optimization_history.append({
                    "iteration": i,
                    "weights": weights.copy(),
                    "score": float(score),
                    "metric": metric,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception:
                # Skip failed evaluations
                continue
        
        # Return best weights found
        if self.best_weights:
            return self.best_weights
        else:
            return self._get_default_weights()
    
    def update_alpha_config(self, config_dict: Dict[str, Any]) -> Dict[str, float]:
        """
        Update configuration and return optimized α-weights.
        
        Args:
            config_dict: Configuration with optimization parameters
            
        Returns:
            Updated weights dictionary
            
        Security: Validates config
        """
        # Extract parameters safely
        learning_rate = config_dict.get("learning_rate", 0.1)
        learning_rate = max(0.01, min(1.0, float(learning_rate)))
        
        if self.best_weights:
            # Apply learning rate to best weights
            current_weights = config_dict.get("current_weights", self._get_default_weights())
            
            updated = {}
            for key in current_weights:
                current = current_weights.get(key, 0.1)
                best = self.best_weights.get(key, 0.1)
                updated[key] = (1 - learning_rate) * current + learning_rate * best
            
            return self._normalize_weights(updated)
        else:
            return self._get_default_weights()
    
    def _sample_weights(self) -> Dict[str, float]:
        """Sample weights from bounds"""
        weights = {}
        for key, (min_val, max_val) in self.weight_bounds.items():
            weights[key] = np.random.uniform(min_val, max_val)
        return weights
    
    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Normalize weights to sum to 1.0"""
        total = sum(weights.values())
        if total > 0:
            return {k: v / total for k, v in weights.items()}
        else:
            return self._get_default_weights()
    
    def _get_default_weights(self) -> Dict[str, float]:
        """Get default weights"""
        return {
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
    
    def _calculate_metric(self, ranked_ids: List[str], 
                         ground_truth: List[str], 
                         metric: str) -> float:
        """
        Calculate ranking metric.
        
        Security: Validates inputs
        """
        if not ranked_ids or not ground_truth:
            return 0.0
        
        if metric == "ndcg":
            return self._ndcg(ranked_ids, ground_truth, k=10)
        elif metric == "precision":
            return self._precision_at_k(ranked_ids, ground_truth, k=10)
        elif metric == "recall":
            return self._recall_at_k(ranked_ids, ground_truth, k=10)
        else:
            return self._ndcg(ranked_ids, ground_truth, k=10)
    
    def _ndcg(self, ranked_ids: List[str], ground_truth: List[str], k: int) -> float:
        """Calculate Normalized Discounted Cumulative Gain"""
        k = min(k, len(ranked_ids), len(ground_truth))
        
        # Calculate DCG
        dcg = 0.0
        for i, idea_id in enumerate(ranked_ids[:k]):
            if idea_id in ground_truth:
                relevance = len(ground_truth) - ground_truth.index(idea_id)
                dcg += relevance / np.log2(i + 2)
        
        # Calculate IDCG (ideal DCG)
        idcg = 0.0
        for i in range(k):
            relevance = len(ground_truth) - i
            idcg += relevance / np.log2(i + 2)
        
        # Normalize
        return dcg / idcg if idcg > 0 else 0.0
    
    def _precision_at_k(self, ranked_ids: List[str], ground_truth: List[str], k: int) -> float:
        """Calculate Precision@K"""
        k = min(k, len(ranked_ids))
        relevant_count = sum(1 for idea_id in ranked_ids[:k] if idea_id in ground_truth)
        return relevant_count / k if k > 0 else 0.0
    
    def _recall_at_k(self, ranked_ids: List[str], ground_truth: List[str], k: int) -> float:
        """Calculate Recall@K"""
        k = min(k, len(ranked_ids))
        relevant_count = sum(1 for idea_id in ranked_ids[:k] if idea_id in ground_truth)
        total_relevant = len(ground_truth)
        return relevant_count / total_relevant if total_relevant > 0 else 0.0
