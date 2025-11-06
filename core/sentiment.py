"""Sentiment Analysis Module"""

class SentimentAnalyzer:
    """Calculates sentiment polarity using lexicon-based approach"""
    
    def __init__(self):
        self.positive_words = {
            "good", "great", "excellent", "amazing", "innovative", "revolutionary",
            "powerful", "efficient", "valuable", "useful", "profitable", "success",
            "opportunity", "growth", "strong", "quality", "benefit", "advantage"
        }
        self.negative_words = {
            "bad", "poor", "terrible", "weak", "risky", "expensive", "difficult",
            "complex", "failing", "loss", "problem", "issue", "threat", "danger"
        }
    
    def analyze(self, text: str) -> float:
        """
        Calculate sentiment polarity ∈ [-1, 1]
        
        Args:
            text: Input text
            
        Returns:
            Sentiment score between -1 (negative) and 1 (positive)
        """
        words = text.lower().split()
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        polarity = (pos_count - neg_count) / total
        return max(-1.0, min(1.0, polarity))
