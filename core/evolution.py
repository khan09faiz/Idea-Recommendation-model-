"""Knowledge Evolution Tracker Module"""

from typing import List, Dict, Any
from datetime import datetime, timedelta


class KnowledgeEvolutionTracker:
    """Tracks how ideas evolve over time"""
    
    def __init__(self):
        self.version_history = {}
    
    def track_version(self, idea_id: str, version_data: Dict[str, Any]):
        """
        Store version snapshot of an idea
        
        Args:
            idea_id: Idea identifier
            version_data: Snapshot data (title, description, scores, etc.)
        """
        if idea_id not in self.version_history:
            self.version_history[idea_id] = []
        
        version_data["timestamp"] = datetime.now()
        self.version_history[idea_id].append(version_data)
    
    def get_evolution_trajectory(self, idea_id: str) -> List[Dict[str, Any]]:
        """
        Get full evolution history for an idea
        
        Args:
            idea_id: Idea identifier
            
        Returns:
            List of version snapshots
        """
        return self.version_history.get(idea_id, [])
    
    def compute_evolution_rate(self, idea_id: str) -> float:
        """
        Compute rate of change (how fast idea is evolving)
        
        Args:
            idea_id: Idea identifier
            
        Returns:
            Evolution rate (changes per day)
        """
        history = self.version_history.get(idea_id, [])
        if len(history) < 2:
            return 0.0
        
        first = history[0]["timestamp"]
        last = history[-1]["timestamp"]
        days = max((last - first).days, 1)
        
        return len(history) / days
    
    def detect_stagnation(self, ideas: List, threshold_days: int = 30) -> List[Dict[str, Any]]:
        """
        Identify ideas that haven't changed in a while
        
        Args:
            ideas: List of Idea objects
            threshold_days: Days without update to consider stagnant
            
        Returns:
            List of stagnant ideas
        """
        stagnant = []
        cutoff = datetime.now() - timedelta(days=threshold_days)
        
        for idea in ideas:
            history = self.version_history.get(idea.idea_id, [])
            if not history:
                last_update = datetime.now()
            else:
                last_update = history[-1]["timestamp"]
            
            if last_update < cutoff:
                stagnant.append({
                    "idea_id": idea.idea_id,
                    "title": idea.title,
                    "last_update": last_update,
                    "days_stagnant": (datetime.now() - last_update).days
                })
        
        return stagnant
    
    def recommend_refresh(self, ideas: List) -> List[str]:
        """
        Recommend ideas that should be refreshed/updated
        
        Args:
            ideas: List of Idea objects
            
        Returns:
            List of idea_ids needing refresh
        """
        stagnant = self.detect_stagnation(ideas, threshold_days=45)
        return [s["idea_id"] for s in stagnant]
