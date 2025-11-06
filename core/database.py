"""
Database Module
SQLite-based storage with integrity hashing and vector search
"""

import sqlite3
import json
import hashlib
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Idea:
    """Core idea data structure"""
    idea_id: str
    title: str
    description: str
    embedding: np.ndarray
    sentiment: float = 0.0
    trend_score: float = 0.0
    provenance_score: float = 0.5
    timestamp: datetime = None
    tags: List[str] = None
    swot: Dict[str, List[str]] = None
    elo_rating: float = 1500.0
    bayesian_mean: float = 0.5
    uncertainty: float = 0.5
    hash_signature: str = ""
    author: str = "AI-Generated"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.tags is None:
            self.tags = []
        if self.swot is None:
            self.swot = {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}


class IdeaDatabase:
    """
    SQLite database with integrity hashing and vector similarity search.
    Ensures data integrity and tamper-evident storage.
    """
    
    def __init__(self, db_path: str = "ideas.db"):
        """
        Initialize database connection and schema.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_schema()
    
    def _init_schema(self):
        """Create database schema if not exists"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                idea_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                embedding BLOB,
                sentiment REAL DEFAULT 0.0,
                trend_score REAL DEFAULT 0.0,
                provenance_score REAL DEFAULT 0.5,
                timestamp TEXT,
                tags TEXT,
                swot TEXT,
                elo_rating REAL DEFAULT 1500.0,
                bayesian_mean REAL DEFAULT 0.5,
                uncertainty REAL DEFAULT 0.5,
                hash_signature TEXT,
                author TEXT DEFAULT 'AI-Generated'
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON ideas(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hash ON ideas(hash_signature)")
        
        self.conn.commit()
    
    def _generate_hash(self, idea: Idea) -> str:
        """
        Generate SHA-256 hash for idea integrity verification.
        
        Args:
            idea: Idea object
            
        Returns:
            Hexadecimal hash string
        """
        # Create deterministic string representation
        hash_data = f"{idea.idea_id}|{idea.title}|{idea.description}|{idea.timestamp.isoformat()}"
        return hashlib.sha256(hash_data.encode()).hexdigest()
    
    def add_idea(self, idea: Idea) -> str:
        """
        Add new idea to database with integrity hash.
        
        Args:
            idea: Idea object to add
            
        Returns:
            Generated idea_id if successful, None otherwise
        """
        try:
            # Generate idea_id if empty
            if not idea.idea_id:
                idea.idea_id = hashlib.md5(f"{idea.title}{idea.timestamp.isoformat()}".encode()).hexdigest()[:16]
            
            # Generate integrity hash
            idea.hash_signature = self._generate_hash(idea)
            
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO ideas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                idea.idea_id,
                idea.title,
                idea.description,
                idea.embedding.tobytes(),
                idea.sentiment,
                idea.trend_score,
                idea.provenance_score,
                idea.timestamp.isoformat(),
                json.dumps(idea.tags),
                json.dumps(idea.swot),
                idea.elo_rating,
                idea.bayesian_mean,
                idea.uncertainty,
                idea.hash_signature,
                idea.author
            ))
            self.conn.commit()
            return idea.idea_id
        except Exception as e:
            print(f"Error adding idea: {e}")
            return None
    
    def update_idea(self, idea: Idea) -> bool:
        """
        Update existing idea and regenerate hash.
        
        Args:
            idea: Updated idea object
            
        Returns:
            True if successful
        """
        return self.add_idea(idea)
    
    def get_idea_by_id(self, idea_id: str) -> Optional[Idea]:
        """
        Retrieve idea by ID.
        
        Args:
            idea_id: Unique idea identifier
            
        Returns:
            Idea object or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ideas WHERE idea_id = ?", (idea_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return Idea(
            idea_id=row[0],
            title=row[1],
            description=row[2],
            embedding=np.frombuffer(row[3], dtype=np.float64),
            sentiment=row[4],
            trend_score=row[5],
            provenance_score=row[6],
            timestamp=datetime.fromisoformat(row[7]),
            tags=json.loads(row[8]),
            swot=json.loads(row[9]),
            elo_rating=row[10],
            bayesian_mean=row[11],
            uncertainty=row[12],
            hash_signature=row[13],
            author=row[14] if len(row) > 14 else "AI-Generated"
        )
    
    def get_all_ideas(self) -> List[Idea]:
        """
        Retrieve all ideas from database.
        
        Returns:
            List of Idea objects
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT idea_id FROM ideas")
        return [self.get_idea_by_id(row[0]) for row in cursor.fetchall()]
    
    def verify_integrity(self) -> Dict[str, any]:
        """
        Verify integrity of all ideas by recomputing hashes.
        
        Returns:
            Dictionary with verification results
        """
        ideas = self.get_all_ideas()
        total = len(ideas)
        valid = 0
        invalid_ids = []
        
        for idea in ideas:
            expected_hash = self._generate_hash(idea)
            if expected_hash == idea.hash_signature:
                valid += 1
            else:
                invalid_ids.append(idea.idea_id)
        
        return {
            "total": total,
            "valid": valid,
            "invalid": len(invalid_ids),
            "validity_rate": valid / total if total > 0 else 1.0,
            "invalid_ids": invalid_ids
        }
    
    def search_similar(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Find similar ideas using cosine similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (idea_id, similarity_score) tuples
        """
        ideas = self.get_all_ideas()
        similarities = []
        
        for idea in ideas:
            # Cosine similarity via dot product (embeddings are normalized)
            sim = float(np.dot(query_embedding, idea.embedding))
            similarities.append((idea.idea_id, sim))
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def close(self):
        """Close database connection"""
        self.conn.close()
