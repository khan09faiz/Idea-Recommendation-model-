"""Market Trend Analysis Module"""

from typing import List


class MarketTrendAnalyzer:
    """Analyzes market trends from text and tags"""
    
    def __init__(self):
        self.trend_keywords = {
            "ai": 0.9, "blockchain": 0.7, "sustainability": 0.8, "cloud": 0.6,
            "mobile": 0.5, "iot": 0.7, "automation": 0.8, "analytics": 0.6,
            "machine learning": 0.9, "cryptocurrency": 0.7, "quantum": 0.8,
            "metaverse": 0.7, "5g": 0.6, "cybersecurity": 0.8
        }
    
    def analyze_trend(self, text: str, tags: List[str]) -> float:
        """
        Calculate trend score ∈ [0, 1] based on trending topics
        
        Args:
            text: Idea description
            tags: List of tags
            
        Returns:
            Trend score indicating market relevance
        """
        text_lower = text.lower()
        combined = text_lower + " " + " ".join([t.lower() for t in tags])
        
        score = 0.0
        matches = 0
        
        for keyword, weight in self.trend_keywords.items():
            if keyword in combined:
                score += weight
                matches += 1
        
        # Return average if matches found, else neutral
        return min(1.0, score / max(1, matches)) if matches > 0 else 0.5
