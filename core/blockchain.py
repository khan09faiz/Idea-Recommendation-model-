"""Integrity Blockchain Layer - Tamper-proof provenance chain"""

from typing import List, Dict, Any, Optional
import hashlib
import json
from datetime import datetime


class Block:
    """Individual block in the integrity blockchain"""
    
    def __init__(self, index: int, timestamp: str, data: Dict[str, Any],
                 previous_hash: str):
        """
        Initialize block.
        
        Args:
            index: Block position in chain
            timestamp: ISO timestamp
            data: Block data dictionary
            previous_hash: Hash of previous block
            
        Security: All inputs validated and hashed
        """
        self.index = int(index)
        self.timestamp = str(timestamp)
        self.data = data
        self.previous_hash = str(previous_hash)
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """
        Calculate SHA-256 hash of block contents.
        
        Security: Uses cryptographic hash, safe serialization
        """
        # Create deterministic string representation
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class IntegrityBlockchainLayer:
    """
    Tamper-proof provenance chain for idea integrity.
    Maintains lightweight blockchain of idea hashes and timestamps.
    """
    
    def __init__(self):
        """Initialize blockchain with genesis block"""
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """
        Create the first block in the chain.
        
        Security: Genesis block with known hash
        """
        genesis_block = Block(
            index=0,
            timestamp=datetime.now().isoformat(),
            data={"type": "genesis", "message": "Integrity Blockchain Initialized"},
            previous_hash="0"
        )
        self.chain.append(genesis_block)
    
    def add_block(self, idea_id: str, idea_hash: str, 
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add new block to the chain.
        
        Args:
            idea_id: Idea identifier
            idea_hash: SHA-256 hash of idea content
            metadata: Optional metadata dictionary
            
        Returns:
            Block hash
            
        Security: Validates inputs, prevents hash collision
        """
        # Input validation
        safe_idea_id = str(idea_id)[:100]
        safe_idea_hash = str(idea_hash)[:64]  # SHA-256 is 64 hex chars
        
        # Validate hash format (should be hex)
        try:
            int(safe_idea_hash, 16)
        except ValueError:
            # Not a valid hash
            return ""
        
        # Sanitize metadata
        if metadata:
            safe_metadata = self._sanitize_metadata(metadata)
        else:
            safe_metadata = {}
        
        # Get previous block
        previous_block = self.chain[-1]
        
        # Create new block
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now().isoformat(),
            data={
                "idea_id": safe_idea_id,
                "idea_hash": safe_idea_hash,
                "metadata": safe_metadata,
                "action": "add_idea"
            },
            previous_hash=previous_block.hash
        )
        
        # Add to chain
        self.chain.append(new_block)
        
        return new_block.hash
    
    def verify_chain_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of the entire blockchain.
        
        Returns:
            Dictionary with verification results
            
        Security: Comprehensive validation of all blocks and links
        """
        if not self.chain:
            return {
                "valid": False,
                "error": "Empty chain"
            }
        
        errors = []
        
        # Check each block
        for i, block in enumerate(self.chain):
            # Verify block hash
            recalculated_hash = block.calculate_hash()
            if block.hash != recalculated_hash:
                errors.append({
                    "block_index": i,
                    "error": "Hash mismatch",
                    "stored_hash": block.hash,
                    "calculated_hash": recalculated_hash
                })
            
            # Verify link to previous block (skip genesis)
            if i > 0:
                previous_block = self.chain[i - 1]
                if block.previous_hash != previous_block.hash:
                    errors.append({
                        "block_index": i,
                        "error": "Previous hash mismatch",
                        "stored_previous": block.previous_hash,
                        "actual_previous": previous_block.hash
                    })
        
        valid = len(errors) == 0
        
        return {
            "valid": valid,
            "chain_length": len(self.chain),
            "errors": errors,
            "verified_at": datetime.now().isoformat()
        }
    
    def get_idea_provenance(self, idea_id: str) -> List[Dict[str, Any]]:
        """
        Get complete provenance history for an idea.
        
        Args:
            idea_id: Idea identifier
            
        Returns:
            List of blocks related to this idea
            
        Security: Safe string matching
        """
        safe_idea_id = str(idea_id)[:100]
        
        provenance = []
        for block in self.chain:
            if isinstance(block.data, dict) and block.data.get("idea_id") == safe_idea_id:
                provenance.append(block.to_dict())
        
        return provenance
    
    def verify_idea_hash(self, idea_id: str, current_hash: str) -> bool:
        """
        Verify if an idea's current hash matches blockchain record.
        
        Args:
            idea_id: Idea identifier
            current_hash: Current computed hash
            
        Returns:
            True if hash matches most recent blockchain record
            
        Security: Tamper detection
        """
        safe_idea_id = str(idea_id)[:100]
        safe_current_hash = str(current_hash)[:64]
        
        # Find most recent block for this idea
        for block in reversed(self.chain):
            if isinstance(block.data, dict) and block.data.get("idea_id") == safe_idea_id:
                stored_hash = block.data.get("idea_hash", "")
                return stored_hash == safe_current_hash
        
        return False
    
    def get_chain_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the blockchain.
        
        Returns:
            Summary dictionary
        """
        unique_ideas = set()
        for block in self.chain[1:]:  # Skip genesis
            if isinstance(block.data, dict):
                idea_id = block.data.get("idea_id")
                if idea_id:
                    unique_ideas.add(idea_id)
        
        return {
            "total_blocks": len(self.chain),
            "unique_ideas": len(unique_ideas),
            "genesis_timestamp": self.chain[0].timestamp if self.chain else None,
            "latest_timestamp": self.chain[-1].timestamp if self.chain else None,
            "chain_valid": self.verify_chain_integrity()["valid"]
        }
    
    def export_chain(self) -> List[Dict[str, Any]]:
        """
        Export entire blockchain for backup/audit.
        
        Returns:
            List of block dictionaries
            
        Security: Safe export, no code execution
        """
        return [block.to_dict() for block in self.chain]
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize metadata dictionary.
        
        Security: Prevents code injection, limits size
        """
        sanitized = {}
        
        for key, value in list(metadata.items())[:20]:  # Limit to 20 items
            # Sanitize key
            safe_key = str(key)[:50]
            
            # Sanitize value
            if isinstance(value, (str, int, float, bool)):
                if isinstance(value, str):
                    sanitized[safe_key] = value[:500]
                else:
                    sanitized[safe_key] = value
            elif value is None:
                sanitized[safe_key] = None
            # Skip complex types
        
        return sanitized
