"""
Enhanced Recommendation Engine - Integrates all advanced modules
"""

from core.engine import RecommendationEngine as BaseEngine
from core.causal_reasoning import CausalReasoningModule
from core.economic_feasibility import EconomicFeasibilityAnalyzer
from core.federated_feedback import FederatedFeedbackManager
from core.temporal_memory import TemporalMemoryManager
from core.meta_learning import MetaLearningOptimizer
from core.blockchain import IntegrityBlockchainLayer
from core.ethics_filter import InteractiveEthicsFilter
from core.twin_generator import IdeaTwinGenerator
from core.evaluation import EvaluationDashboard

from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np


class EnhancedRecommendationEngine(BaseEngine):
    """
    Enhanced recommendation engine with all advanced modules integrated.
    Extends base engine with causal reasoning, economic feasibility,
    federated learning, blockchain integrity, and more.
    """
    
    def __init__(self, db_path: str = "data/ideas.db", ollama_model: str = "llama2"):
        """
        Initialize enhanced engine with all modules.
        
        Args:
            db_path: Path to SQLite database
            ollama_model: Ollama model name
        """
        # Initialize base engine
        super().__init__(db_path, ollama_model)
        
        # Initialize new advanced modules
        self.causal_reasoning = CausalReasoningModule()
        self.economic_feasibility = EconomicFeasibilityAnalyzer()
        self.federated_feedback = FederatedFeedbackManager()
        self.temporal_memory = TemporalMemoryManager()
        self.meta_learning = MetaLearningOptimizer()
        self.blockchain = IntegrityBlockchainLayer()
        self.ethics_filter = InteractiveEthicsFilter()
        self.twin_generator = IdeaTwinGenerator()
        self.evaluation_dashboard = EvaluationDashboard()
        
        print("✅ Enhanced Recommendation Engine initialized with 27 modules")
    
    def add_idea_enhanced(self, title: str, description: str, author: str = "system",
                         tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Add idea with enhanced pre-processing pipeline.
        
        Returns:
            Dictionary with idea_id, blockchain hash, and ethics assessment
        """
        # Ethics screening (pre-processing)
        combined_text = f"{title} {description}"
        ethics_result = self.ethics_filter.flagged(
            combined_text,
            metadata={"tags": tags} if tags else None
        )
        
        if ethics_result["flagged"] and ethics_result["severity"] == "high":
            return {
                "success": False,
                "error": "Idea blocked due to ethical concerns",
                "ethics_assessment": ethics_result
            }
        
        # Add idea using base method
        idea_id = self.add_idea(title, description, author, tags)
        
        # Check if idea was added (None means duplicate)
        if not idea_id:
            return {
                "success": False,
                "error": "Duplicate idea already exists",
                "duplicate": True
            }
        
        # Get the idea object
        idea = self.db.get_idea_by_id(idea_id)
        
        if not idea:
            return {
                "success": False,
                "error": "Failed to retrieve added idea"
            }
        
        # Economic feasibility analysis with dynamic feature extraction
        # Extract features from title and description
        title_lower = title.lower()
        desc_lower = description.lower()
        
        # Market size estimation based on keywords
        market_indicators = {
            'global': 0.9, 'international': 0.85, 'worldwide': 0.9,
            'national': 0.7, 'regional': 0.5, 'local': 0.3, 'niche': 0.4,
            'enterprise': 0.8, 'consumer': 0.7, 'b2b': 0.65, 'b2c': 0.7
        }
        market_size = 0.5  # Default
        for keyword, score in market_indicators.items():
            if keyword in title_lower or keyword in desc_lower:
                market_size = max(market_size, score)
        
        # Revenue potential based on business model keywords
        revenue_indicators = {
            'subscription': 0.8, 'saas': 0.85, 'platform': 0.75, 'marketplace': 0.8,
            'premium': 0.7, 'freemium': 0.65, 'advertising': 0.6, 'commission': 0.7,
            'license': 0.75, 'consulting': 0.55, 'service': 0.6, 'product': 0.7,
            'e-commerce': 0.75, 'online': 0.65, 'digital': 0.7
        }
        revenue_potential = 0.5  # Default
        for keyword, score in revenue_indicators.items():
            if keyword in title_lower or keyword in desc_lower:
                revenue_potential = max(revenue_potential, score)
        
        # Cost estimation (inverse - lower is better)
        cost_indicators = {
            'low-cost': 0.2, 'affordable': 0.3, 'budget': 0.3, 'cheap': 0.25,
            'minimal': 0.2, 'bootstrap': 0.25, 'lean': 0.3,
            'expensive': 0.8, 'costly': 0.85, 'premium': 0.7, 'luxury': 0.75,
            'hardware': 0.7, 'infrastructure': 0.75, 'manufacturing': 0.8,
            'software': 0.4, 'app': 0.35, 'web': 0.3, 'digital': 0.35,
            'ai': 0.5, 'ml': 0.5, 'automation': 0.45
        }
        cost = 0.5  # Default medium cost
        for keyword, score in cost_indicators.items():
            if keyword in title_lower or keyword in desc_lower:
                cost = score
                break  # Use first match
        
        # Adjust based on sentiment - positive sentiment suggests lower perceived cost/risk
        if idea.sentiment > 0.3:
            cost *= 0.9
        elif idea.sentiment < -0.3:
            cost *= 1.1
        
        feasibility = self.economic_feasibility.analyze_feasibility({
            "market_size": market_size,
            "revenue_potential": revenue_potential,
            "cost": min(cost, 1.0),
            "trend": idea.trend_score,
            "sentiment": idea.sentiment,
            "uncertainty": idea.uncertainty,
            "provenance": idea.provenance_score,
            "complexity": 0.5,  # Could be enhanced further
            "volatility": 0.5,
            "regulatory_risk": 0.3
        })
        
        # Store embedding in temporal memory
        self.temporal_memory.store_embedding(
            idea_id,
            idea.embedding,
            metadata={
                "title": title,
                "author": author,
                "tags": tags or []
            }
        )
        
        # Add to blockchain for integrity
        blockchain_hash = self.blockchain.add_block(
            idea_id,
            idea.hash_signature,
            metadata={
                "title": title,
                "author": author,
                "ethics_score": ethics_result["ethical_score"],
                "feasibility_score": feasibility["feasibility_score"]
            }
        )
        
        return {
            "success": True,
            "idea_id": idea_id,
            "blockchain_hash": blockchain_hash,
            "ethics_assessment": ethics_result,
            "feasibility_analysis": feasibility,
            "adjustment_factor": ethics_result["adjustment_factor"]
        }
    
    def get_recommendations_enhanced(self, query: str, top_k: int = 10,
                                    use_causal: bool = True,
                                    use_feasibility: bool = True,
                                    view: str = "consensus") -> List[Dict[str, Any]]:
        """
        Get enhanced recommendations with all advanced features.
        
        Args:
            query: User query
            top_k: Number of results
            use_causal: Use causal reasoning
            use_feasibility: Use economic feasibility
            view: Ranking view
            
        Returns:
            Enhanced recommendations with additional scores
        """
        # Get base recommendations
        base_results = self.get_recommendations(query, top_k * 2, view, use_mmr=True)
        
        # Enhance each result
        enhanced_results = []
        
        for result in base_results:
            idea_id = result["idea_id"]
            idea = self.db.get_idea_by_id(idea_id)
            
            if not idea:
                continue
            
            # Ethics check
            ethics_result = self.ethics_filter.flagged(
                f"{idea.title} {idea.description}",
                metadata={"tags": idea.tags}
            )
            
            # Apply ethics adjustment
            adjusted_score = result["final_score"] * ethics_result["adjustment_factor"]
            
            # Economic feasibility with dynamic feature extraction
            feasibility_score = 0.5
            if use_feasibility:
                # Extract features from idea
                title_lower = idea.title.lower()
                desc_lower = idea.description.lower() if idea.description else ""
                
                # Market size estimation
                market_indicators = {'global': 0.9, 'national': 0.7, 'local': 0.3, 'niche': 0.4}
                market_size = 0.5
                for keyword, score in market_indicators.items():
                    if keyword in title_lower or keyword in desc_lower:
                        market_size = max(market_size, score)
                
                # Revenue potential
                revenue_indicators = {'subscription': 0.8, 'saas': 0.85, 'platform': 0.75, 'marketplace': 0.8}
                revenue_potential = 0.5
                for keyword, score in revenue_indicators.items():
                    if keyword in title_lower or keyword in desc_lower:
                        revenue_potential = max(revenue_potential, score)
                
                # Cost estimation
                cost_indicators = {'low-cost': 0.2, 'affordable': 0.3, 'expensive': 0.8, 'hardware': 0.7}
                cost = 0.5
                for keyword, score in cost_indicators.items():
                    if keyword in title_lower or keyword in desc_lower:
                        cost = score
                        break
                
                feasibility = self.economic_feasibility.analyze_feasibility({
                    "market_size": market_size,
                    "revenue_potential": revenue_potential,
                    "cost": cost,
                    "trend": idea.trend_score,
                    "sentiment": idea.sentiment,
                    "uncertainty": idea.uncertainty,
                    "provenance": idea.provenance_score,
                    "complexity": 0.5,
                    "volatility": 0.5,
                    "regulatory_risk": 0.3
                })
                feasibility_score = feasibility["feasibility_score"]
                adjusted_score = adjusted_score * 0.8 + feasibility_score * 0.2
            
            # Causal impact
            causal_impact = 0.0
            if use_causal:
                causal_features = {
                    "sentiment": idea.sentiment,
                    "trend": idea.trend_score,
                    "elo": idea.elo_rating / 1500.0,
                    "provenance": idea.provenance_score
                }
                causal_impact = self.causal_reasoning.compute_causal_impact_score(causal_features)
                adjusted_score = adjusted_score * 0.9 + causal_impact * 0.1
            
            # Blockchain verification
            blockchain_verified = self.blockchain.verify_idea_hash(idea_id, idea.hash_signature)
            
            enhanced_results.append({
                **result,
                "adjusted_final_score": float(adjusted_score),
                "ethics_score": float(ethics_result["ethical_score"]),
                "ethics_compliance": float(ethics_result["compliance_score"]),
                "feasibility_score": float(feasibility_score),
                "causal_impact": float(causal_impact),
                "blockchain_verified": blockchain_verified
            })
        
        # Re-sort by adjusted score
        enhanced_results.sort(key=lambda x: x["adjusted_final_score"], reverse=True)
        
        # Update ranks
        for i, result in enumerate(enhanced_results[:top_k], 1):
            result["rank"] = i
        
        return enhanced_results[:top_k]
    
    def submit_federated_feedback(self, user_id: str, 
                                  idea_feedbacks: Dict[str, float]) -> Dict[str, Any]:
        """
        Submit feedback using federated learning approach.
        
        Args:
            user_id: User identifier
            idea_feedbacks: Dictionary of idea_id -> feedback_value
            
        Returns:
            Status dictionary
        """
        # Convert feedbacks to weight updates
        local_weights = self._feedback_to_weights(idea_feedbacks)
        
        # Collect encrypted local update
        update_id = self.federated_feedback.collect_local_updates(
            user_id,
            local_weights,
            encrypt=True
        )
        
        # Store in temporal memory
        self.temporal_memory.store_context(
            f"feedback_{update_id}",
            {
                "user_hash": update_id,
                "num_feedbacks": len(idea_feedbacks),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return {
            "success": True,
            "update_id": update_id,
            "num_feedbacks": len(idea_feedbacks)
        }
    
    def optimize_weights_meta_learning(self, ground_truth: List[str],
                                      n_iterations: int = 50) -> Dict[str, float]:
        """
        Optimize α-weights using meta-learning.
        
        Args:
            ground_truth: Ground truth ideal ranking
            n_iterations: Optimization iterations
            
        Returns:
            Optimized weights
        """
        ideas = self.db.get_all_ideas()
        
        def ranking_func(weights, ideas_list):
            # Simple ranking function for optimization
            ranked = sorted(
                ideas_list,
                key=lambda x: sum(
                    weights.get(k, 0.1) * getattr(x, k, 0.5)
                    for k in weights.keys()
                ),
                reverse=True
            )
            return [idea.idea_id for idea in ranked]
        
        optimized_weights = self.meta_learning.optimize_weights(
            ranking_func,
            ground_truth,
            ideas,
            metric="ndcg",
            n_iterations=n_iterations
        )
        
        return optimized_weights
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive system report with all metrics"""
        # Base audit
        base_audit = self.generate_audit_report()
        
        # Blockchain integrity
        blockchain_summary = self.blockchain.get_chain_summary()
        blockchain_integrity = self.blockchain.verify_chain_integrity()
        
        # Temporal memory stats
        recent_contexts = len(self.temporal_memory.retrieve_recent_context(hours_back=24))
        recent_embeddings = len(self.temporal_memory.retrieve_temporal_embeddings(hours_back=168))
        
        # Federated feedback stats
        fed_history_count = len(self.federated_feedback.update_history)
        
        # Meta-learning stats
        ml_history_count = len(self.meta_learning.optimization_history)
        best_metric = self.meta_learning.best_metric
        
        return {
            "timestamp": datetime.now().isoformat(),
            "base_audit": base_audit,
            "blockchain": {
                "summary": blockchain_summary,
                "integrity": blockchain_integrity
            },
            "temporal_memory": {
                "recent_contexts_24h": recent_contexts,
                "recent_embeddings_7d": recent_embeddings
            },
            "federated_learning": {
                "update_rounds": fed_history_count
            },
            "meta_learning": {
                "optimization_runs": ml_history_count,
                "best_ndcg": float(best_metric) if best_metric > -np.inf else None
            }
        }
    
    def _feedback_to_weights(self, feedbacks: Dict[str, float]) -> Dict[str, float]:
        """Convert feedback signals to weight updates"""
        # Simplified: adjust weights based on average feedback
        avg_feedback = np.mean(list(feedbacks.values())) if feedbacks else 0.5
        
        # Return slightly adjusted weights
        base_weights = {
            "elo": 0.15,
            "bayesian": 0.15,
            "sentiment": 0.15,
            "trend": 0.15,
            "provenance": 0.1,
            "freshness": 0.1,
            "causal": 0.1,
            "uncertainty": 0.05,
            "serendipity": 0.05
        }
        
        # Adjust based on feedback (simple approach)
        adjustment = (avg_feedback - 0.5) * 0.1
        adjusted = {k: v + adjustment / len(base_weights) for k, v in base_weights.items()}
        
        # Normalize
        total = sum(adjusted.values())
        return {k: v / total for k, v in adjusted.items()}
