"""MMR Diversity Ranking Module"""

from typing import List, Dict, Any
import numpy as np


class MMRDiversityRanker:
    """Maximal Marginal Relevance for diverse rankings"""
    
    def __init__(self, lambda_param: float = 0.5):
        """
        Args:
            lambda_param: Balance between relevance and diversity (0=diversity, 1=relevance)
        """
        self.lambda_param = lambda_param
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return np.dot(vec1, vec2) / (norm1 * norm2)
    
    def mmr_rank(self, ideas: List, query_embedding: np.ndarray,
                 top_k: int = 10) -> List[Dict[str, Any]]:
        """
        MMR ranking: balance relevance to query with diversity
        
        Args:
            ideas: List of Idea objects (with embeddings)
            query_embedding: Query vector
            top_k: Number of diverse results
            
        Returns:
            Ranked list with MMR scores
        """
        if not ideas:
            return []
        
        # Compute relevance scores
        relevance = []
        for idea in ideas:
            sim = self.cosine_similarity(idea.embedding, query_embedding)
            relevance.append(sim)
        
        # MMR selection
        selected = []
        remaining = list(range(len(ideas)))
        
        # Select first item (highest relevance)
        first_idx = np.argmax(relevance)
        selected.append(first_idx)
        remaining.remove(first_idx)
        
        # Iteratively select diverse items
        while len(selected) < top_k and remaining:
            mmr_scores = []
            
            for idx in remaining:
                # Relevance component
                rel = relevance[idx]
                
                # Diversity component (max similarity to selected)
                max_sim = max(
                    self.cosine_similarity(ideas[idx].embedding, ideas[s].embedding)
                    for s in selected
                )
                
                # MMR formula
                mmr = self.lambda_param * rel - (1 - self.lambda_param) * max_sim
                mmr_scores.append((idx, mmr))
            
            # Select best MMR
            best_idx, best_mmr = max(mmr_scores, key=lambda x: x[1])
            selected.append(best_idx)
            remaining.remove(best_idx)
        
        # Build result
        result = []
        for rank, idx in enumerate(selected, 1):
            result.append({
                "rank": rank,
                "idea_id": ideas[idx].idea_id,
                "title": ideas[idx].title,
                "relevance": relevance[idx],
                "mmr_score": self.lambda_param * relevance[idx]
            })
        
        return result
    
    def adjust_lambda(self, user_preference: str):
        """
        Adjust lambda based on user preference
        
        Args:
            user_preference: "relevance", "balanced", or "diversity"
        """
        if user_preference == "relevance":
            self.lambda_param = 0.8
        elif user_preference == "diversity":
            self.lambda_param = 0.2
        else:
            self.lambda_param = 0.5
