"""Main Recommendation Engine - Orchestrates all modules"""

from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime

from core.ollama_interface import OllamaInterface
from core.database import IdeaDatabase, Idea
from core.integrity import IntegrityAssuranceLayer
from core.sentiment import SentimentAnalyzer
from core.trend import MarketTrendAnalyzer
from core.weights import ContextAwareWeightAdapter
from core.feedback import UserFeedbackFineTuner
from core.time_decay import TimeDecayModule
from core.ranking import MultiFocusedViewRanker
from core.graph import IdeaRelationshipGraph
from core.cross_modal import CrossModalProcessor
from core.explainability import ExplainabilityEngine
from core.fairness import FairnessAndRobustnessModule
from core.counterfactual import CounterfactualRankingEngine
from core.esg import SustainabilityAndESGScorer
from core.evolution import KnowledgeEvolutionTracker
from core.mmr import MMRDiversityRanker


class RecommendationEngine:
    """Complete end-to-end recommendation system"""
    
    def __init__(self, db_path: str = "data/ideas.db", ollama_model: str = "llama2"):
        """
        Initialize all modules
        
        Args:
            db_path: Path to SQLite database
            ollama_model: Ollama model name
        """
        # Core modules
        self.ollama = OllamaInterface(model=ollama_model)
        self.db = IdeaDatabase(db_path)
        self.integrity = IntegrityAssuranceLayer(self.db)
        
        # Analysis modules
        self.sentiment = SentimentAnalyzer()
        self.trend = MarketTrendAnalyzer()
        self.weights = ContextAwareWeightAdapter()
        self.feedback = UserFeedbackFineTuner()
        self.time_decay = TimeDecayModule()
        self.ranking = MultiFocusedViewRanker()
        self.graph = IdeaRelationshipGraph()
        
        # Advanced modules
        self.cross_modal = CrossModalProcessor(self.ollama)
        self.explainability = ExplainabilityEngine()
        self.fairness = FairnessAndRobustnessModule()
        self.counterfactual = CounterfactualRankingEngine()
        self.esg = SustainabilityAndESGScorer()
        self.evolution = KnowledgeEvolutionTracker()
        self.mmr = MMRDiversityRanker()
    
    def add_idea(self, title: str, description: str, author: str = "system",
                tags: Optional[List[str]] = None) -> str:
        """
        Add new idea to system
        
        Args:
            title: Idea title
            description: Idea description
            author: Author name
            tags: Optional tags list
            
        Returns:
            Idea ID
        """
        # Generate embedding
        embedding = self.ollama.generate_embedding(description)
        
        # Generate SWOT tags
        if tags is None:
            swot = self.ollama.generate_swot_tags(description)
            tags = []
        else:
            swot = None
        
        # Analyze sentiment
        sentiment = self.sentiment.analyze(description)
        
        # Analyze trend
        trend_score = self.trend.analyze_trend(description, tags if tags else [])
        
        # Create idea object
        idea = Idea(
            idea_id="",  # Will be generated
            title=title,
            description=description,
            embedding=embedding,
            tags=tags,
            swot=swot,
            timestamp=datetime.now(),
            sentiment=sentiment,
            trend_score=trend_score,
            elo_rating=1500.0,
            bayesian_mean=0.5,
            uncertainty=0.3,
            provenance_score=0.7
        )
        
        # Verify it's not adversarial
        if not self.fairness.filter_adversarial(idea):
            raise ValueError("Idea flagged as adversarial/spam")
        
        # Add to database
        idea_id = self.db.add_idea(idea)
        
        # Track version
        self.evolution.track_version(idea_id, {
            "title": title,
            "description": description,
            "sentiment": sentiment,
            "trend": trend_score
        })
        
        return idea_id
    
    def get_recommendations(self, query: str, top_k: int = 10,
                          view: str = "consensus",
                          use_mmr: bool = True) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations
        
        Args:
            query: User query
            top_k: Number of results
            view: Ranking perspective (user/market/swot/consensus)
            use_mmr: Apply MMR diversity
            
        Returns:
            List of recommended ideas with scores and explanations
        """
        # Get all ideas
        ideas = self.db.get_all_ideas()
        
        if not ideas:
            return []
        
        # Check for bias
        bias_report = self.fairness.detect_bias(ideas)
        
        # Get query embedding
        query_emb = self.ollama.generate_embedding(query)
        
        # Search similar ideas
        similar_ideas = self.db.search_similar(query_emb, top_k=top_k * 2)
        ideas_subset = [self.db.get_idea_by_id(idea_id) for idea_id, sim_score in similar_ideas]
        ideas_subset = [i for i in ideas_subset if i is not None]
        
        # Build relationship graph
        self.graph.build_graph(ideas_subset)
        influence_scores = self.graph.calculate_influence()
        
        # Compute scores for each idea
        scored_ideas = []
        for idea in ideas_subset:
            # Time freshness
            freshness = self.time_decay.calculate_freshness(idea.timestamp)
            
            # Graph influence
            influence = influence_scores.get(idea.idea_id, 0.0)
            
            # ESG score
            esg = self.esg.compute_esg_score(idea)
            
            # Compute components
            components = {
                "elo": idea.elo_rating / 1500.0,  # Normalize
                "bayesian_mean": idea.bayesian_mean,
                "uncertainty": idea.uncertainty,
                "sentiment": idea.sentiment,
                "provenance": idea.provenance_score,
                "freshness": freshness,
                "trend": idea.trend_score,
                "causal_impact": influence,
                "serendipity": 1.0 - similar_ideas[0][1] if similar_ideas else 0.5  # Inverse of similarity
            }
            
            # Get weights
            weights = self.weights.adapt_weights({
                "domain": "general",
                "market_volatility": 0.5,
                "data_quality": idea.provenance_score,
                "fairness_adjustment": False
            })
            
            # Rebalance if bias detected
            if bias_report["bias_detected"]:
                weights = self.fairness.rebalance_weights(weights, bias_report)
            
            # Calculate final score
            final_score = sum(components[k] * weights[k] for k in components.keys())
            
            # Integrate ESG
            final_score = self.esg.aggregate_with_esg(final_score, esg["total_esg"])
            
            # Integrity score boost
            integrity_score = self.integrity.compute_integrity_score(idea.idea_id)
            final_score *= (1 + integrity_score * 0.1)
            
            scored_ideas.append({
                "idea": idea,
                "final_score": final_score,
                "components": components,
                "weights": weights,
                "esg": esg,
                "integrity": integrity_score
            })
        
        # Sort by score
        scored_ideas.sort(key=lambda x: x["final_score"], reverse=True)
        
        # Apply view-based ranking if requested
        if view != "consensus":
            view_ranked = self.ranking.rank_by_view([s["idea"] for s in scored_ideas], view)
            # Reorder scored_ideas
            id_to_scored = {s["idea"].idea_id: s for s in scored_ideas}
            scored_ideas = [id_to_scored[vr["idea_id"]] for vr in view_ranked if vr["idea_id"] in id_to_scored]
        
        # Apply MMR diversity
        if use_mmr:
            mmr_results = self.mmr.mmr_rank(
                [s["idea"] for s in scored_ideas],
                query_emb,
                top_k=top_k
            )
            # Reorder
            id_to_scored = {s["idea"].idea_id: s for s in scored_ideas}
            scored_ideas = [id_to_scored[mmr["idea_id"]] for mmr in mmr_results if mmr["idea_id"] in id_to_scored]
        else:
            scored_ideas = scored_ideas[:top_k]
        
        # Generate explanations
        results = []
        for rank, item in enumerate(scored_ideas[:top_k], 1):
            idea = item["idea"]
            
            # Counterfactual explanations
            counterfactuals = self.explainability.generate_counterfactuals(
                idea,
                rank,
                item["components"]
            )
            
            # Top features
            top_features = self.explainability.explain_top_features(
                item["components"],
                item["weights"]
            )
            
            # Factor breakdown
            breakdown = self.explainability.generate_factor_breakdown(
                item["components"],
                item["weights"],
                item["final_score"]
            )
            
            results.append({
                "rank": rank,
                "idea_id": idea.idea_id,
                "title": idea.title,
                "summary": idea.description[:200] if len(idea.description) > 200 else idea.description,
                "description": idea.description,
                "tags": idea.tags,
                "author": idea.author,
                "final_score": item["final_score"],
                "esg_scores": item["esg"],
                "integrity_score": item["integrity"],
                "explanation": {
                    "counterfactuals": counterfactuals,
                    "top_features": top_features,
                    "breakdown": breakdown
                }
            })
        
        return results
    
    def submit_feedback(self, idea_id: str, feedback_type: str,
                       value: float, context: Optional[Dict] = None):
        """
        Submit user feedback
        
        Args:
            idea_id: Idea identifier
            feedback_type: Type (like/dislike/click/time_spent)
            value: Feedback value
            context: Optional context dictionary
        """
        self.feedback.collect_feedback(idea_id, feedback_type, value, context)
        
        # Update idea parameters
        idea = self.db.get_idea_by_id(idea_id)
        if idea:
            updated = self.feedback.update_idea_parameters(idea)
            # Update in DB
            self.db.conn.execute(
                "UPDATE ideas SET elo_score=?, bayesian_mean=?, bayesian_std=? WHERE idea_id=?",
                (updated.elo_score, updated.bayesian_mean, updated.bayesian_std, idea_id)
            )
            self.db.conn.commit()
    
    def generate_audit_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit and integrity report"""
        ideas = self.db.get_all_ideas()
        
        # Integrity check
        integrity_report = self.db.verify_integrity()
        
        # Bias check
        bias_report = self.fairness.detect_bias(ideas)
        
        # Audit manifest with run parameters
        manifest = self.integrity.generate_audit_manifest({
            "run_id": self.integrity._generate_run_id(),
            "timestamp": datetime.now().isoformat(),
            "model_version": "1.0.0",
            "weights": {},
            "parameters": {"total_ideas": len(ideas)}
        })
        
        # Stagnation check
        stagnant = self.evolution.detect_stagnation(ideas)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_ideas": len(ideas),
            "integrity": integrity_report,
            "bias": bias_report,
            "manifest": manifest,
            "stagnant_ideas": stagnant,
            "recommendations": {
                "refresh_needed": self.evolution.recommend_refresh(ideas)
            }
        }
    
    def run_counterfactual_analysis(self, query: str) -> Dict[str, Any]:
        """
        Run counterfactual scenario analysis
        
        Args:
            query: Query string
            
        Returns:
            Scenario comparison report
        """
        ideas = self.db.get_all_ideas()
        
        # Generate scenarios
        self.counterfactual.generate_scenario(ideas, "base", {})
        self.counterfactual.generate_scenario(ideas, "sentiment_heavy", {"sentiment": 2.0})
        self.counterfactual.generate_scenario(ideas, "trend_heavy", {"trend": 2.0})
        self.counterfactual.generate_scenario(ideas, "diversity_heavy", {"serendipity": 3.0})
        
        # Compare
        comparison = self.counterfactual.compare_scenarios([
            "base", "sentiment_heavy", "trend_heavy", "diversity_heavy"
        ])
        
        return comparison
