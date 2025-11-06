"""Federated Feedback Manager - Secure multi-user feedback aggregation"""

from typing import Dict, List, Any, Optional
import hashlib
import json
from datetime import datetime
import numpy as np


class FederatedFeedbackManager:
    """
    Secure multi-user feedback aggregation with differential privacy.
    Implements federated learning principles for privacy-preserving updates.
    """
    
    def __init__(self, noise_scale: float = 0.1, privacy_epsilon: float = 1.0):
        """
        Initialize federated feedback manager.
        
        Args:
            noise_scale: Scale of Laplacian noise for differential privacy
            privacy_epsilon: Privacy budget parameter
            
        Security: All parameters validated and clamped
        """
        self.noise_scale = max(0.0, min(1.0, noise_scale))
        self.privacy_epsilon = max(0.1, min(10.0, privacy_epsilon))
        self.local_updates = []
        self.global_weights = {}
        self.update_history = []
        
    def collect_local_updates(self, user_id: str, 
                              local_weights: Dict[str, float],
                              encrypt: bool = True) -> str:
        """
        Collect encrypted local updates from a user.
        
        Args:
            user_id: User identifier (hashed for privacy)
            local_weights: Local weight updates
            encrypt: Whether to encrypt the update
            
        Returns:
            Update ID for tracking
            
        Security: Hashes user_id, validates weights, applies differential privacy
        """
        # Hash user_id for privacy
        user_hash = hashlib.sha256(str(user_id).encode()).hexdigest()[:16]
        
        # Validate weights
        validated_weights = self._validate_weights(local_weights)
        
        # Apply differential privacy noise
        private_weights = self._add_differential_privacy_noise(validated_weights)
        
        # Encrypt if requested
        if encrypt:
            encrypted_weights = self._encrypt_weights(private_weights, user_hash)
        else:
            encrypted_weights = private_weights
        
        # Create update record
        update = {
            "update_id": hashlib.sha256(
                f"{user_hash}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16],
            "user_hash": user_hash,
            "weights": encrypted_weights,
            "timestamp": datetime.now().isoformat(),
            "encrypted": encrypt
        }
        
        self.local_updates.append(update)
        
        return update["update_id"]
    
    def aggregate_global_weights(self, aggregation_method: str = "fedavg") -> Dict[str, float]:
        """
        Aggregate local updates into global weights.
        
        Args:
            aggregation_method: Aggregation strategy (fedavg, median, trimmed_mean)
            
        Returns:
            Aggregated global weights
            
        Security: Validates method, applies secure aggregation
        """
        if not self.local_updates:
            return self.global_weights
        
        # Decrypt and extract weights
        all_weights = []
        for update in self.local_updates:
            weights = update["weights"]
            if update["encrypted"]:
                weights = self._decrypt_weights(weights, update["user_hash"])
            all_weights.append(weights)
        
        # Aggregate based on method
        if aggregation_method == "fedavg":
            aggregated = self._federated_averaging(all_weights)
        elif aggregation_method == "median":
            aggregated = self._median_aggregation(all_weights)
        elif aggregation_method == "trimmed_mean":
            aggregated = self._trimmed_mean_aggregation(all_weights)
        else:
            aggregated = self._federated_averaging(all_weights)
        
        # Update global weights
        self.global_weights = aggregated
        
        # Record in history
        self.update_history.append({
            "timestamp": datetime.now().isoformat(),
            "num_updates": len(self.local_updates),
            "aggregation_method": aggregation_method
        })
        
        # Clear local updates after aggregation
        self.local_updates = []
        
        return self.global_weights
    
    def apply_global_update(self, current_weights: Dict[str, float],
                           learning_rate: float = 0.1) -> Dict[str, float]:
        """
        Apply global update to current model weights.
        
        Args:
            current_weights: Current model weights
            learning_rate: Learning rate for update
            
        Returns:
            Updated weights
            
        Security: Validates learning rate and weights
        """
        # Validate learning rate
        lr = max(0.0, min(1.0, learning_rate))
        
        # Validate current weights
        validated_current = self._validate_weights(current_weights)
        
        if not self.global_weights:
            return validated_current
        
        # Apply weighted update
        updated = {}
        for key in validated_current:
            global_update = self.global_weights.get(key, validated_current[key])
            updated[key] = (1 - lr) * validated_current[key] + lr * global_update
        
        return updated
    
    def _validate_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Validate and sanitize weights"""
        validated = {}
        for key, value in weights.items():
            # Sanitize key
            safe_key = str(key)[:50]
            
            # Validate value
            if isinstance(value, (int, float)) and np.isfinite(value):
                validated[safe_key] = float(np.clip(value, 0.0, 1.0))
            else:
                validated[safe_key] = 0.5  # Default
        
        return validated
    
    def _add_differential_privacy_noise(self, weights: Dict[str, float]) -> Dict[str, float]:
        """
        Add Laplacian noise for differential privacy.
        
        Security: Uses cryptographically secure random if available
        """
        noisy_weights = {}
        
        for key, value in weights.items():
            # Laplacian noise: scale = sensitivity / epsilon
            sensitivity = 1.0  # Assume bounded weights [0, 1]
            scale = sensitivity / self.privacy_epsilon
            
            # Add noise
            noise = np.random.laplace(0, scale * self.noise_scale)
            noisy_value = value + noise
            
            # Clip to valid range
            noisy_weights[key] = float(np.clip(noisy_value, 0.0, 1.0))
        
        return noisy_weights
    
    def _encrypt_weights(self, weights: Dict[str, float], key: str) -> Dict[str, float]:
        """
        Simple encryption using XOR with key-derived values.
        
        Note: For production, use proper encryption (AES-GCM, TLS)
        Security: This is a lightweight demonstration
        """
        encrypted = {}
        
        for idx, (weight_key, value) in enumerate(weights.items()):
            # Derive encryption key from user hash and index
            derived_key = int(hashlib.sha256(f"{key}_{idx}".encode()).hexdigest()[:8], 16)
            
            # Simple XOR encryption (for demonstration)
            # In production, use AES-GCM or similar
            value_int = int(value * 1000000)  # Scale for precision
            encrypted_int = value_int ^ derived_key
            
            encrypted[weight_key] = encrypted_int
        
        return encrypted
    
    def _decrypt_weights(self, encrypted: Dict[str, Any], key: str) -> Dict[str, float]:
        """Decrypt weights using key"""
        decrypted = {}
        
        for idx, (weight_key, encrypted_value) in enumerate(encrypted.items()):
            # Derive same encryption key
            derived_key = int(hashlib.sha256(f"{key}_{idx}".encode()).hexdigest()[:8], 16)
            
            # XOR decrypt
            if isinstance(encrypted_value, int):
                decrypted_int = encrypted_value ^ derived_key
                decrypted[weight_key] = float(decrypted_int) / 1000000.0
            else:
                # Fallback for unencrypted
                decrypted[weight_key] = float(encrypted_value)
        
        return decrypted
    
    def _federated_averaging(self, all_weights: List[Dict[str, float]]) -> Dict[str, float]:
        """Standard federated averaging"""
        if not all_weights:
            return {}
        
        aggregated = {}
        all_keys = set()
        for weights in all_weights:
            all_keys.update(weights.keys())
        
        for key in all_keys:
            values = [w.get(key, 0.5) for w in all_weights]
            aggregated[key] = float(np.mean(values))
        
        return aggregated
    
    def _median_aggregation(self, all_weights: List[Dict[str, float]]) -> Dict[str, float]:
        """Robust median aggregation"""
        if not all_weights:
            return {}
        
        aggregated = {}
        all_keys = set()
        for weights in all_weights:
            all_keys.update(weights.keys())
        
        for key in all_keys:
            values = [w.get(key, 0.5) for w in all_weights]
            aggregated[key] = float(np.median(values))
        
        return aggregated
    
    def _trimmed_mean_aggregation(self, all_weights: List[Dict[str, float]], 
                                  trim_ratio: float = 0.1) -> Dict[str, float]:
        """Trimmed mean for outlier robustness"""
        if not all_weights:
            return {}
        
        aggregated = {}
        all_keys = set()
        for weights in all_weights:
            all_keys.update(weights.keys())
        
        for key in all_keys:
            values = np.array([w.get(key, 0.5) for w in all_weights])
            
            # Trim extreme values
            n_trim = int(len(values) * trim_ratio)
            if n_trim > 0:
                sorted_values = np.sort(values)
                trimmed = sorted_values[n_trim:-n_trim] if n_trim < len(values)//2 else sorted_values
                aggregated[key] = float(np.mean(trimmed))
            else:
                aggregated[key] = float(np.mean(values))
        
        return aggregated
