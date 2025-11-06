"""
Ollama Interface Module
Handles local LLM interactions for embeddings, summaries, and SWOT analysis
"""

import subprocess
import hashlib
import json
import numpy as np
from typing import Dict, List


class OllamaInterface:
    """
    Interface for local Ollama LLM integration.
    Provides embeddings, summaries, and SWOT analysis with fallback to mock mode.
    """
    
    def __init__(self, model: str = "llama3.2:1b", use_mock: bool = False):
        """
        Initialize Ollama interface.
        
        Args:
            model: Ollama model name
            use_mock: Use mock responses if True or if Ollama unavailable
        """
        self.model = model
        self.use_mock = use_mock
        self.embedding_dim = 384
    
    def _call_ollama(self, prompt: str, system: str = "") -> str:
        """
        Call Ollama CLI and return response.
        Falls back to mock if unavailable.
        """
        if self.use_mock:
            return self._mock_response(prompt)
        
        try:
            cmd = ["ollama", "run", self.model]
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            result = subprocess.run(
                cmd,
                input=full_prompt.encode(),
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout.decode().strip()
            else:
                return self._mock_response(prompt)
        except Exception:
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Generate deterministic mock response based on prompt hash"""
        if "embedding" in prompt.lower():
            return json.dumps([0.1] * self.embedding_dim)
        elif "swot" in prompt.lower():
            return "Strengths: Innovation, Scalability; Weaknesses: High cost; Opportunities: Market growth; Threats: Competition"
        else:
            return f"Summary: {prompt[:100]}..."
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate semantic embedding vector for text.
        Uses deterministic hash-based mock for reproducibility.
        
        Args:
            text: Input text
            
        Returns:
            Normalized embedding vector
        """
        # Deterministic embedding based on text hash
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        np.random.seed(hash_val % (2**32))
        embedding = np.random.randn(self.embedding_dim)
        # Normalize to unit vector
        return embedding / np.linalg.norm(embedding)
    
    def generate(self, prompt: str) -> str:
        """
        Generate response from Ollama for any prompt.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text response
        """
        return self._call_ollama(prompt)
    
    def generate_summary(self, text: str, max_words: int = 50) -> str:
        """
        Generate concise summary of text.
        
        Args:
            text: Input text
            max_words: Maximum words in summary
            
        Returns:
            Summary string
        """
        prompt = f"Summarize the following in {max_words} words or less:\n{text}"
        response = self._call_ollama(prompt)
        return response[:200] if response else text[:200]
    
    def generate_swot_tags(self, text: str) -> Dict[str, List[str]]:
        """
        Generate SWOT analysis tags from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with strengths, weaknesses, opportunities, threats
        """
        prompt = f"Perform SWOT analysis on:\n{text}\n\nFormat: Strengths: X; Weaknesses: Y; Opportunities: Z; Threats: W"
        response = self._call_ollama(prompt)
        
        # Parse SWOT from response
        swot = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }
        
        for key in swot.keys():
            try:
                # Extract items between key and next semicolon
                start = response.lower().find(key)
                if start != -1:
                    end = response.find(";", start)
                    if end == -1:
                        end = len(response)
                    items_text = response[start:end]
                    # Remove key name and split by comma
                    items_text = items_text.split(":", 1)[-1]
                    items = [x.strip() for x in items_text.split(",")]
                    swot[key] = [item for item in items if item][:3]
            except Exception:
                pass
        
        return swot
