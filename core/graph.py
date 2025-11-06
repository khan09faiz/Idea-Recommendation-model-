"""Idea Relationship Graph Module"""

import numpy as np
from typing import List, Dict
from collections import defaultdict


class IdeaRelationshipGraph:
    """Builds and analyzes idea relationship networks"""
    
    def __init__(self, similarity_threshold: float = 0.5):
        """
        Initialize graph builder
        
        Args:
            similarity_threshold: Minimum similarity for edge creation
        """
        self.similarity_threshold = similarity_threshold
        self.graph = {}  # Adjacency list: idea_id -> [(neighbor_id, weight), ...]
        self.influence_scores = {}
    
    def build_graph(self, ideas: List):
        """
        Build graph based on embedding similarity and shared tags
        
        Args:
            ideas: List of Idea objects
        """
        self.graph = {idea.idea_id: [] for idea in ideas}
        
        for i, idea1 in enumerate(ideas):
            for idea2 in ideas[i+1:]:
                # Cosine similarity from embeddings
                sim = float(np.dot(idea1.embedding, idea2.embedding))
                
                # Boost for shared tags
                shared_tags = set(idea1.tags) & set(idea2.tags)
                sim += 0.1 * len(shared_tags)
                
                # Create bidirectional edge if above threshold
                if sim >= self.similarity_threshold:
                    self.graph[idea1.idea_id].append((idea2.idea_id, sim))
                    self.graph[idea2.idea_id].append((idea1.idea_id, sim))
    
    def calculate_influence(self) -> Dict[str, float]:
        """
        Calculate influence scores using weighted degree centrality
        
        Returns:
            Dictionary mapping idea_id to influence score ∈ [0, 1]
        """
        for idea_id, neighbors in self.graph.items():
            # Sum of edge weights = weighted degree
            influence = sum(weight for _, weight in neighbors)
            self.influence_scores[idea_id] = influence
        
        # Normalize to [0, 1]
        if self.influence_scores:
            max_inf = max(self.influence_scores.values())
            if max_inf > 0:
                self.influence_scores = {
                    k: v / max_inf
                    for k, v in self.influence_scores.items()
                }
        
        return self.influence_scores
    
    def propagate_provenance(self, initial_scores: Dict[str, float],
                            iterations: int = 3) -> Dict[str, float]:
        """
        Propagate provenance confidence through graph
        
        Args:
            initial_scores: Initial provenance scores per idea
            iterations: Number of propagation iterations
            
        Returns:
            Updated provenance scores
        """
        scores = initial_scores.copy()
        
        for _ in range(iterations):
            new_scores = {}
            for idea_id, neighbors in self.graph.items():
                if not neighbors:
                    new_scores[idea_id] = scores.get(idea_id, 0.5)
                    continue
                
                # Weighted average of own score and neighbors
                own_score = scores.get(idea_id, 0.5)
                neighbor_scores = [
                    scores.get(nid, 0.5) * weight
                    for nid, weight in neighbors
                ]
                avg_neighbor = np.mean(neighbor_scores) if neighbor_scores else 0.5
                
                # 70% own score, 30% neighbor influence
                new_scores[idea_id] = 0.7 * own_score + 0.3 * avg_neighbor
            
            scores = new_scores
        
        return scores
