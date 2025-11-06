"""Interactive Ethics Filter - Pre-ranking ethical/regulatory screening"""

from typing import Dict, List, Any, Set
import re


class InteractiveEthicsFilter:
    """
    Pre-ranking ethical and regulatory compliance screening.
    Flags or down-ranks non-compliant ideas.
    """
    
    def __init__(self):
        """Initialize ethics filter with compliance rules"""
        # Prohibited content patterns
        self.prohibited_keywords = {
            "violence", "weapon", "harmful", "illegal", "discriminatory",
            "racist", "sexist", "hate", "exploit", "manipulate",
            "mislead", "fraud", "scam", "pyramid", "ponzi"
        }
        
        # High-risk domains requiring special attention
        self.high_risk_domains = {
            "cryptocurrency", "gambling", "tobacco", "alcohol",
            "pharmaceutical", "medical device", "financial services"
        }
        
        # Required compliance indicators
        self.compliance_keywords = {
            "ethical", "compliant", "regulated", "certified",
            "transparent", "privacy", "consent", "gdpr", "hipaa"
        }
        
        self.filter_history = []
    
    def flagged(self, idea_text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check if idea should be flagged for ethical concerns.
        
        Args:
            idea_text: Combined title and description
            metadata: Optional metadata with tags, domain info
            
        Returns:
            Dictionary with flagging decision and reasons
            
        Security: Sanitizes input, safe regex matching
        """
        # Input sanitization
        safe_text = str(idea_text)[:5000].lower()
        
        flags = []
        severity = "none"
        should_flag = False
        compliance_score = 0.0
        
        # Check for prohibited content
        prohibited_found = self._check_prohibited(safe_text)
        if prohibited_found:
            flags.append({
                "type": "prohibited_content",
                "keywords": list(prohibited_found),
                "severity": "high",
                "action": "block"
            })
            severity = "high"
            should_flag = True
        
        # Check high-risk domains
        high_risk_found = self._check_high_risk(safe_text, metadata)
        if high_risk_found:
            # Check if proper compliance indicators present
            compliance_found = self._check_compliance(safe_text)
            
            if not compliance_found:
                flags.append({
                    "type": "missing_compliance",
                    "domains": list(high_risk_found),
                    "severity": "medium",
                    "action": "downrank",
                    "recommendation": "Add compliance documentation"
                })
                if severity != "high":
                    severity = "medium"
                should_flag = True
            else:
                # Has compliance indicators
                compliance_score = len(compliance_found) / 5.0  # Normalize
                compliance_score = min(1.0, compliance_score)
        
        # Check for ethical indicators (positive signals)
        ethical_score = self._calculate_ethical_score(safe_text, metadata)
        
        # Privacy and data protection checks
        privacy_concerns = self._check_privacy_concerns(safe_text)
        if privacy_concerns:
            flags.append({
                "type": "privacy_concern",
                "issues": privacy_concerns,
                "severity": "medium",
                "action": "review",
                "recommendation": "Ensure GDPR/privacy compliance"
            })
            if severity == "none":
                severity = "medium"
        
        # Record in history
        self.filter_history.append({
            "idea_text_hash": self._hash_text(idea_text),
            "flagged": should_flag,
            "flags": flags,
            "severity": severity
        })
        
        return {
            "flagged": should_flag,
            "severity": severity,
            "flags": flags,
            "compliance_score": float(compliance_score),
            "ethical_score": float(ethical_score),
            "action": "block" if severity == "high" else "downrank" if severity == "medium" else "pass",
            "adjustment_factor": self._get_adjustment_factor(severity, ethical_score)
        }
    
    def _check_prohibited(self, text: str) -> Set[str]:
        """Check for prohibited keywords"""
        found = set()
        for keyword in self.prohibited_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                found.add(keyword)
        return found
    
    def _check_high_risk(self, text: str, metadata: Dict[str, Any] = None) -> Set[str]:
        """Check for high-risk domains"""
        found = set()
        
        # Check in text
        for domain in self.high_risk_domains:
            if re.search(r'\b' + re.escape(domain) + r'\b', text):
                found.add(domain)
        
        # Check in metadata tags
        if metadata and "tags" in metadata:
            tags = metadata.get("tags", [])
            if isinstance(tags, list):
                for tag in tags:
                    tag_lower = str(tag).lower()
                    if tag_lower in self.high_risk_domains:
                        found.add(tag_lower)
        
        return found
    
    def _check_compliance(self, text: str) -> Set[str]:
        """Check for compliance keywords"""
        found = set()
        for keyword in self.compliance_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                found.add(keyword)
        return found
    
    def _check_privacy_concerns(self, text: str) -> List[str]:
        """Check for privacy-related concerns"""
        concerns = []
        
        # Data collection without privacy mention
        if re.search(r'\b(collect|gather|track|monitor)\b.*\bdata\b', text):
            if not re.search(r'\b(privacy|consent|gdpr|anonymous|encrypt)\b', text):
                concerns.append("Data collection without privacy safeguards mentioned")
        
        # Personal information handling
        if re.search(r'\b(personal|sensitive|private)\b.*\b(information|data)\b', text):
            if not re.search(r'\b(protect|secure|encrypt|privacy)\b', text):
                concerns.append("Personal information handling without security mention")
        
        return concerns
    
    def _calculate_ethical_score(self, text: str, metadata: Dict[str, Any] = None) -> float:
        """Calculate ethical alignment score"""
        score = 0.0
        
        # Positive ethical indicators
        ethical_indicators = {
            "sustainable": 0.15,
            "ethical": 0.15,
            "fair": 0.10,
            "inclusive": 0.10,
            "accessible": 0.10,
            "transparent": 0.10,
            "responsible": 0.10,
            "community": 0.10,
            "environmental": 0.10
        }
        
        for indicator, weight in ethical_indicators.items():
            if re.search(r'\b' + re.escape(indicator) + r'\b', text):
                score += weight
        
        # ESG-related terms
        if metadata and "esg_scores" in metadata:
            esg = metadata.get("esg_scores", {})
            if isinstance(esg, dict):
                score += esg.get("total_esg", 0.0) * 0.2
        
        return min(1.0, score)
    
    def _get_adjustment_factor(self, severity: str, ethical_score: float) -> float:
        """
        Get score adjustment factor based on filtering results.
        
        Returns:
            Multiplier for final score [0, 1]
        """
        if severity == "high":
            return 0.0  # Block completely
        elif severity == "medium":
            # Moderate downranking, but ethical score can help
            base_penalty = 0.5
            ethical_bonus = ethical_score * 0.3
            return min(1.0, base_penalty + ethical_bonus)
        else:
            # Boost for high ethical scores
            return min(1.0, 1.0 + ethical_score * 0.1)
    
    def _hash_text(self, text: str) -> str:
        """Generate hash of text for tracking"""
        import hashlib
        return hashlib.sha256(str(text).encode()).hexdigest()[:16]
