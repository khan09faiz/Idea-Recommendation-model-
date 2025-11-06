"""Evaluation Dashboard - Quantitative validation and metrics"""

from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import json


class EvaluationDashboard:
    """
    Quantitative validation with nDCG, Precision, Recall, Diversity, Fairness metrics.
    Supports train/test split and cross-validation.
    """
    
    def __init__(self):
        """Initialize evaluation dashboard"""
        self.evaluation_history = []
        
    def evaluate_ranking(self, ranked_ids: List[str],
                        ground_truth: List[str],
                        k_values: List[int] = [5, 10, 20]) -> Dict[str, Any]:
        """
        Comprehensive ranking evaluation.
        
        Args:
            ranked_ids: List of ranked idea IDs (predicted ranking)
            ground_truth: List of ground truth idea IDs (ideal ranking)
            k_values: List of K values for @K metrics
            
        Returns:
            Dictionary with all metrics
            
        Security: Validates inputs
        """
        # Input validation
        if not ranked_ids or not ground_truth:
            return {"error": "Empty rankings"}
        
        k_values = [max(1, min(len(ranked_ids), k)) for k in k_values]
        
        metrics = {
            "ndcg": {},
            "precision": {},
            "recall": {},
            "f1": {},
            "diversity": self._calculate_diversity(ranked_ids),
            "fairness_index": self._calculate_fairness(ranked_ids),
            "coverage": self._calculate_coverage(ranked_ids, ground_truth),
            "timestamp": datetime.now().isoformat()
        }
        
        # Calculate metrics for each K
        for k in k_values:
            metrics["ndcg"][f"@{k}"] = self._ndcg_at_k(ranked_ids, ground_truth, k)
            metrics["precision"][f"@{k}"] = self._precision_at_k(ranked_ids, ground_truth, k)
            metrics["recall"][f"@{k}"] = self._recall_at_k(ranked_ids, ground_truth, k)
            
            # F1 score
            p = metrics["precision"][f"@{k}"]
            r = metrics["recall"][f"@{k}"]
            metrics["f1"][f"@{k}"] = (2 * p * r / (p + r)) if (p + r) > 0 else 0.0
        
        # Store in history
        self.evaluation_history.append(metrics)
        
        return metrics
    
    def cross_validate(self, ideas: List[Any], ranking_function,
                      n_folds: int = 5) -> Dict[str, Any]:
        """
        Perform k-fold cross-validation.
        
        Args:
            ideas: List of idea objects
            ranking_function: Function that ranks ideas
            n_folds: Number of cross-validation folds
            
        Returns:
            Dictionary with cross-validation results
            
        Security: Safe fold splitting
        """
        n_folds = max(2, min(10, n_folds))
        
        if len(ideas) < n_folds:
            return {"error": "Not enough ideas for cross-validation"}
        
        # Shuffle ideas
        shuffled_ideas = ideas.copy()
        np.random.shuffle(shuffled_ideas)
        
        # Split into folds
        fold_size = len(shuffled_ideas) // n_folds
        folds = []
        
        for i in range(n_folds):
            start_idx = i * fold_size
            end_idx = start_idx + fold_size if i < n_folds - 1 else len(shuffled_ideas)
            folds.append(shuffled_ideas[start_idx:end_idx])
        
        # Evaluate each fold
        fold_results = []
        
        for fold_idx in range(n_folds):
            # Use one fold as test, others as train
            test_fold = folds[fold_idx]
            train_folds = [f for i, f in enumerate(folds) if i != fold_idx]
            train_ideas = [idea for fold in train_folds for idea in fold]
            
            # Rank test fold
            try:
                test_ids = [idea.idea_id for idea in test_fold]
                ranked_ids = ranking_function(train_ideas, test_fold)
                
                # Evaluate (using test_ids as ground truth for simplicity)
                metrics = self.evaluate_ranking(ranked_ids, test_ids, k_values=[5, 10])
                fold_results.append(metrics)
            except Exception:
                continue
        
        # Aggregate results
        if fold_results:
            aggregated = self._aggregate_fold_results(fold_results)
            aggregated["n_folds"] = len(fold_results)
            return aggregated
        else:
            return {"error": "Cross-validation failed"}
    
    def train_test_split(self, ideas: List[Any], test_ratio: float = 0.2) -> tuple:
        """
        Split ideas into train and test sets.
        
        Args:
            ideas: List of idea objects
            test_ratio: Ratio of test set
            
        Returns:
            Tuple of (train_ideas, test_ideas)
            
        Security: Validates ratio
        """
        test_ratio = max(0.1, min(0.5, float(test_ratio)))
        
        shuffled = ideas.copy()
        np.random.shuffle(shuffled)
        
        split_idx = int(len(shuffled) * (1 - test_ratio))
        train = shuffled[:split_idx]
        test = shuffled[split_idx:]
        
        return train, test
    
    def generate_report(self, metrics: Dict[str, Any],
                       format: str = "text") -> str:
        """
        Generate human-readable evaluation report.
        
        Args:
            metrics: Metrics dictionary
            format: Output format (text, html, json)
            
        Returns:
            Formatted report string
            
        Security: Safe formatting
        """
        if format == "json":
            return json.dumps(metrics, indent=2)
        elif format == "html":
            return self._generate_html_report(metrics)
        else:
            return self._generate_text_report(metrics)
    
    def _ndcg_at_k(self, ranked_ids: List[str], ground_truth: List[str], k: int) -> float:
        """Calculate NDCG@K"""
        k = min(k, len(ranked_ids), len(ground_truth))
        
        # DCG
        dcg = 0.0
        for i, idea_id in enumerate(ranked_ids[:k]):
            if idea_id in ground_truth:
                relevance = len(ground_truth) - ground_truth.index(idea_id)
                dcg += relevance / np.log2(i + 2)
        
        # IDCG
        idcg = 0.0
        for i in range(k):
            relevance = len(ground_truth) - i
            idcg += relevance / np.log2(i + 2)
        
        return float(dcg / idcg) if idcg > 0 else 0.0
    
    def _precision_at_k(self, ranked_ids: List[str], ground_truth: List[str], k: int) -> float:
        """Calculate Precision@K"""
        k = min(k, len(ranked_ids))
        relevant = sum(1 for idea_id in ranked_ids[:k] if idea_id in ground_truth)
        return float(relevant / k) if k > 0 else 0.0
    
    def _recall_at_k(self, ranked_ids: List[str], ground_truth: List[str], k: int) -> float:
        """Calculate Recall@K"""
        k = min(k, len(ranked_ids))
        relevant = sum(1 for idea_id in ranked_ids[:k] if idea_id in ground_truth)
        total_relevant = len(ground_truth)
        return float(relevant / total_relevant) if total_relevant > 0 else 0.0
    
    def _calculate_diversity(self, ranked_ids: List[str]) -> float:
        """
        Calculate diversity score based on uniqueness.
        Higher is more diverse.
        """
        if len(ranked_ids) <= 1:
            return 0.0
        
        # Simple diversity: ratio of unique IDs
        unique_ratio = len(set(ranked_ids)) / len(ranked_ids)
        return float(unique_ratio)
    
    def _calculate_fairness(self, ranked_ids: List[str]) -> float:
        """
        Calculate fairness index (Gini coefficient approximation).
        1.0 = perfectly fair, 0.0 = perfectly unfair
        """
        if not ranked_ids:
            return 0.0
        
        # Simulate distribution (in real case, use actual scores/exposures)
        n = len(ranked_ids)
        positions = list(range(1, n + 1))
        
        # Calculate Gini coefficient
        mean_position = np.mean(positions)
        abs_diff_sum = sum(abs(p1 - p2) for p1 in positions for p2 in positions)
        gini = abs_diff_sum / (2 * n * n * mean_position)
        
        # Convert to fairness index (1 - Gini)
        fairness = 1.0 - gini
        
        return float(np.clip(fairness, 0.0, 1.0))
    
    def _calculate_coverage(self, ranked_ids: List[str], ground_truth: List[str]) -> float:
        """Calculate what fraction of ground truth is covered"""
        if not ground_truth:
            return 0.0
        
        covered = sum(1 for gt_id in ground_truth if gt_id in ranked_ids)
        return float(covered / len(ground_truth))
    
    def _aggregate_fold_results(self, fold_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate cross-validation results"""
        aggregated = {
            "ndcg": {},
            "precision": {},
            "recall": {},
            "f1": {},
            "diversity_mean": 0.0,
            "fairness_mean": 0.0
        }
        
        # Average metrics across folds
        for metric_type in ["ndcg", "precision", "recall", "f1"]:
            for k in fold_results[0].get(metric_type, {}).keys():
                values = [fold.get(metric_type, {}).get(k, 0) for fold in fold_results]
                aggregated[metric_type][k] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values))
                }
        
        # Average diversity and fairness
        diversity_values = [fold.get("diversity", 0) for fold in fold_results]
        fairness_values = [fold.get("fairness_index", 0) for fold in fold_results]
        
        aggregated["diversity_mean"] = float(np.mean(diversity_values))
        aggregated["fairness_mean"] = float(np.mean(fairness_values))
        
        return aggregated
    
    def _generate_text_report(self, metrics: Dict[str, Any]) -> str:
        """Generate text report"""
        lines = [
            "=" * 60,
            "EVALUATION DASHBOARD REPORT",
            "=" * 60,
            ""
        ]
        
        # NDCG
        lines.append("Normalized Discounted Cumulative Gain (nDCG):")
        for k, score in metrics.get("ndcg", {}).items():
            lines.append(f"  nDCG{k}: {score:.4f}")
        lines.append("")
        
        # Precision
        lines.append("Precision:")
        for k, score in metrics.get("precision", {}).items():
            lines.append(f"  Precision{k}: {score:.4f}")
        lines.append("")
        
        # Recall
        lines.append("Recall:")
        for k, score in metrics.get("recall", {}).items():
            lines.append(f"  Recall{k}: {score:.4f}")
        lines.append("")
        
        # Other metrics
        lines.append(f"Diversity Score: {metrics.get('diversity', 0):.4f}")
        lines.append(f"Fairness Index: {metrics.get('fairness_index', 0):.4f}")
        lines.append(f"Coverage: {metrics.get('coverage', 0):.4f}")
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def _generate_html_report(self, metrics: Dict[str, Any]) -> str:
        """Generate HTML report"""
        html = """
        <html>
        <head><title>Evaluation Dashboard</title></head>
        <body>
        <h1>Evaluation Dashboard Report</h1>
        <table border="1">
        <tr><th>Metric</th><th>Value</th></tr>
        """
        
        for metric_type in ["ndcg", "precision", "recall", "f1"]:
            for k, score in metrics.get(metric_type, {}).items():
                html += f"<tr><td>{metric_type.upper()}{k}</td><td>{score:.4f}</td></tr>"
        
        html += f"<tr><td>Diversity</td><td>{metrics.get('diversity', 0):.4f}</td></tr>"
        html += f"<tr><td>Fairness</td><td>{metrics.get('fairness_index', 0):.4f}</td></tr>"
        html += "</table></body></html>"
        
        return html
