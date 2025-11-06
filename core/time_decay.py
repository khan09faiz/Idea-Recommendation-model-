"""Time Decay Module"""

import numpy as np
from datetime import datetime


class TimeDecayModule:
    """Applies exponential decay to idea freshness"""
    
    def __init__(self, lambda_decay: float = 0.01):
        """
        Initialize time decay calculator
        
        Args:
            lambda_decay: Decay rate parameter (higher = faster decay)
        """
        self.lambda_decay = lambda_decay
    
    def calculate_freshness(self, timestamp: datetime) -> float:
        """
        Calculate freshness score ∈ [0, 1] with exponential decay
        
        Args:
            timestamp: Idea timestamp
            
        Returns:
            Freshness score (1.0 = brand new, approaches 0 as age increases)
        """
        days_old = (datetime.now() - timestamp).days
        freshness = np.exp(-self.lambda_decay * days_old)
        return max(0.0, min(1.0, float(freshness)))
