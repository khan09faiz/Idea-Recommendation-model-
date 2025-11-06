"""
Integrity Assurance Layer
Provides reproducibility, provenance tracking, and integrity validation
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any
from .database import IdeaDatabase


class IntegrityAssuranceLayer:
    """
    Ensures data integrity, reproducibility, and tamper-evident storage.
    Generates audit trails and validates system integrity.
    """
    
    def __init__(self, database: IdeaDatabase):
        """
        Initialize integrity layer.
        
        Args:
            database: IdeaDatabase instance
        """
        self.database = database
        self.audit_log = []
    
    def generate_hash(self, idea_data: Dict[str, Any]) -> str:
        """
        Generate SHA-256 hash for any data structure.
        
        Args:
            idea_data: Dictionary of idea attributes
            
        Returns:
            Hexadecimal hash string
        """
        # Sort keys for deterministic hashing
        sorted_data = json.dumps(idea_data, sort_keys=True)
        return hashlib.sha256(sorted_data.encode()).hexdigest()
    
    def generate_audit_manifest(self, run_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create audit manifest for reproducibility.
        
        Args:
            run_params: Dictionary containing:
                - run_id: Unique run identifier
                - model_version: Model version string
                - weights: Dictionary of α weights
                - timestamp: Run timestamp
                - parameters: Other relevant parameters
        
        Returns:
            Audit manifest dictionary
        """
        manifest = {
            "run_id": run_params.get("run_id", self._generate_run_id()),
            "timestamp": run_params.get("timestamp", datetime.now().isoformat()),
            "model_version": run_params.get("model_version", "1.0.0"),
            "weights": run_params.get("weights", {}),
            "parameters": run_params.get("parameters", {}),
            "manifest_hash": ""
        }
        
        # Generate hash of manifest itself (excluding hash field)
        manifest_copy = manifest.copy()
        manifest_copy.pop("manifest_hash")
        manifest["manifest_hash"] = self.generate_hash(manifest_copy)
        
        # Store in audit log
        self.audit_log.append(manifest)
        
        return manifest
    
    def _generate_run_id(self) -> str:
        """Generate unique run identifier"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:16]
    
    def validate_integrity(self) -> Dict[str, Any]:
        """
        Validate integrity of all database records.
        
        Returns:
            Validation report with:
                - total_records
                - valid_records
                - invalid_records
                - validity_rate
                - tampered_ids
        """
        verification = self.database.verify_integrity()
        
        report = {
            "status": "PASS" if verification["validity_rate"] == 1.0 else "FAIL",
            "total_records": verification["total"],
            "valid_records": verification["valid"],
            "invalid_records": verification["invalid"],
            "validity_rate": verification["validity_rate"],
            "tampered_ids": verification["invalid_ids"],
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def compute_integrity_score(self, idea_id: str) -> float:
        """
        Compute integrity score for an idea.
        Combines provenance trust, hash consistency, and reproducibility.
        
        Args:
            idea_id: Idea identifier
            
        Returns:
            Integrity score ∈ [0, 1]
        """
        idea = self.database.get_idea_by_id(idea_id)
        if not idea:
            return 0.0
        
        # Component 1: Hash consistency (binary: 0 or 1)
        expected_hash = self.database._generate_hash(idea)
        hash_valid = 1.0 if expected_hash == idea.hash_signature else 0.0
        
        # Component 2: Provenance score (already stored)
        provenance = idea.provenance_score
        
        # Component 3: Age-based reproducibility (newer = more reproducible)
        days_old = (datetime.now() - idea.timestamp).days
        reproducibility = max(0.0, 1.0 - (days_old / 365.0))  # Decays over a year
        
        # Weighted combination
        integrity = 0.5 * hash_valid + 0.3 * provenance + 0.2 * reproducibility
        
        return max(0.0, min(1.0, integrity))
    
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """
        Retrieve complete audit trail.
        
        Returns:
            List of audit manifests
        """
        return self.audit_log.copy()
    
    def export_integrity_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive integrity report.
        
        Returns:
            Full integrity report
        """
        validation = self.validate_integrity()
        
        # Compute integrity scores for all ideas
        ideas = self.database.get_all_ideas()
        integrity_scores = {
            idea.idea_id: self.compute_integrity_score(idea.idea_id)
            for idea in ideas
        }
        
        avg_integrity = sum(integrity_scores.values()) / len(integrity_scores) if integrity_scores else 0.0
        
        report = {
            "validation": validation,
            "average_integrity_score": avg_integrity,
            "individual_scores": integrity_scores,
            "audit_trail_entries": len(self.audit_log),
            "generated_at": datetime.now().isoformat()
        }
        
        return report
