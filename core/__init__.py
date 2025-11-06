"""
Core modules for Advanced Idea Recommendation System
"""

# Original modules
from .ollama_interface import OllamaInterface
from .database import IdeaDatabase, Idea
from .integrity import IntegrityAssuranceLayer
from .sentiment import SentimentAnalyzer
from .trend import MarketTrendAnalyzer
from .weights import ContextAwareWeightAdapter
from .feedback import UserFeedbackFineTuner
from .time_decay import TimeDecayModule
from .ranking import MultiFocusedViewRanker
from .graph import IdeaRelationshipGraph
from .cross_modal import CrossModalProcessor
from .explainability import ExplainabilityEngine
from .fairness import FairnessAndRobustnessModule
from .counterfactual import CounterfactualRankingEngine
from .esg import SustainabilityAndESGScorer
from .evolution import KnowledgeEvolutionTracker
from .mmr import MMRDiversityRanker
from .engine import RecommendationEngine

# New advanced modules
from .causal_reasoning import CausalReasoningModule
from .economic_feasibility import EconomicFeasibilityAnalyzer
from .federated_feedback import FederatedFeedbackManager
from .temporal_memory import TemporalMemoryManager
from .meta_learning import MetaLearningOptimizer
from .blockchain import IntegrityBlockchainLayer
from .ethics_filter import InteractiveEthicsFilter
from .twin_generator import IdeaTwinGenerator
from .evaluation import EvaluationDashboard

__all__ = [
    # Original modules
    'OllamaInterface',
    'IdeaDatabase',
    'Idea',
    'IntegrityAssuranceLayer',
    'SentimentAnalyzer',
    'MarketTrendAnalyzer',
    'ContextAwareWeightAdapter',
    'UserFeedbackFineTuner',
    'TimeDecayModule',
    'MultiFocusedViewRanker',
    'IdeaRelationshipGraph',
    'CrossModalProcessor',
    'ExplainabilityEngine',
    'FairnessAndRobustnessModule',
    'CounterfactualRankingEngine',
    'SustainabilityAndESGScorer',
    'KnowledgeEvolutionTracker',
    'MMRDiversityRanker',
    'RecommendationEngine',
    # New advanced modules
    'CausalReasoningModule',
    'EconomicFeasibilityAnalyzer',
    'FederatedFeedbackManager',
    'TemporalMemoryManager',
    'MetaLearningOptimizer',
    'IntegrityBlockchainLayer',
    'InteractiveEthicsFilter',
    'IdeaTwinGenerator',
    'EvaluationDashboard'
]
