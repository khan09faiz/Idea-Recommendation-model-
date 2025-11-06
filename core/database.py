"""
Database Module
SQLite-based storage with integrity hashing and FAISS vector search
"""

import sqlite3
import json
import hashlib
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

# FAISS import with fallback
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️  FAISS not available, using simple cosine similarity")


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
    SQLite database with integrity hashing and FAISS vector similarity search.
    Ensures data integrity and tamper-evident storage.
    Automatically uses FAISS for large datasets (>100 ideas), simple search for small ones.
    """
    
    def __init__(self, db_path: str = "data/ideas.db", use_faiss: bool = True):
        """
        Initialize database connection and schema.
        
        Args:
            db_path: Path to SQLite database file
            use_faiss: Whether to use FAISS (auto-fallback if unavailable)
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.use_faiss = use_faiss and FAISS_AVAILABLE
        self.faiss_index = None
        self.faiss_id_map = []  # Maps FAISS index to idea_id
        self.embedding_dim = None
        self._init_schema()
        
        # Build FAISS index if enabled
        if self.use_faiss:
            self._build_faiss_index()
    
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
        Prevents duplicate ideas by checking title.
        
        Args:
            idea: Idea object to add
            
        Returns:
            Generated idea_id if successful, None if duplicate or error
        """
        try:
            # Check if idea with same title already exists
            cursor = self.conn.cursor()
            cursor.execute("SELECT idea_id FROM ideas WHERE title = ?", (idea.title,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"⚠️  Duplicate detected: '{idea.title}' already exists (ID: {existing[0]})")
                return None
            
            # Generate idea_id if empty
            if not idea.idea_id:
                idea.idea_id = hashlib.md5(f"{idea.title}{idea.timestamp.isoformat()}".encode()).hexdigest()[:16]
            
            # Generate integrity hash
            idea.hash_signature = self._generate_hash(idea)
            
            cursor.execute("""
                INSERT INTO ideas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            
            # Rebuild FAISS index if using FAISS and dataset is large enough
            if self.use_faiss:
                ideas_count = len(self.get_all_ideas())
                if ideas_count >= 100:
                    self.rebuild_faiss_index()
            
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
    
    def _build_faiss_index(self):
        """
        Build or rebuild FAISS index from all ideas in database.
        Uses IndexFlatIP (inner product) for normalized vectors.
        Auto-switches to simple search if <100 ideas.
        """
        ideas = self.get_all_ideas()
        
        if not ideas:
            return
        
        # Use FAISS only for large datasets
        if len(ideas) < 100:
            print(f"📊 Dataset size: {len(ideas)} ideas - using simple similarity (FAISS threshold: 100)")
            self.faiss_index = None
            return
        
        # Get embedding dimension from first idea
        self.embedding_dim = len(ideas[0].embedding)
        
        # Create FAISS index (IndexFlatIP for inner product/cosine similarity)
        self.faiss_index = faiss.IndexFlatIP(self.embedding_dim)
        
        # Prepare embeddings matrix
        embeddings = np.array([idea.embedding for idea in ideas], dtype=np.float32)
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.faiss_index.add(embeddings)
        
        # Update ID mapping
        self.faiss_id_map = [idea.idea_id for idea in ideas]
        
        print(f"✅ FAISS index built: {len(ideas)} ideas, dimension {self.embedding_dim}")
    
    def rebuild_faiss_index(self):
        """
        Rebuild FAISS index (call after adding/removing ideas).
        """
        if self.use_faiss:
            self._build_faiss_index()
    
    def search_similar(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Find similar ideas using FAISS or cosine similarity.
        Automatically uses FAISS for large datasets (>100 ideas).
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (idea_id, similarity_score) tuples
        """
        ideas = self.get_all_ideas()
        
        if not ideas:
            return []
        
        # Use FAISS if index exists and dataset is large enough
        if self.use_faiss and self.faiss_index is not None and len(ideas) >= 100:
            return self._search_with_faiss(query_embedding, top_k)
        else:
            return self._search_simple(query_embedding, top_k, ideas)
    
    def _search_with_faiss(self, query_embedding: np.ndarray, top_k: int) -> List[Tuple[str, float]]:
        """
        FAISS-based vector search (for large datasets).
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            
        Returns:
            List of (idea_id, similarity_score) tuples
        """
        # Prepare query vector
        query_vector = query_embedding.astype(np.float32).reshape(1, -1)
        faiss.normalize_L2(query_vector)
        
        # Search
        similarities, indices = self.faiss_index.search(query_vector, min(top_k, len(self.faiss_id_map)))
        
        # Map indices to idea_ids
        results = []
        for i, (idx, sim) in enumerate(zip(indices[0], similarities[0])):
            if idx < len(self.faiss_id_map):
                idea_id = self.faiss_id_map[idx]
                results.append((idea_id, float(sim)))
        
        return results
    
    def _search_simple(self, query_embedding: np.ndarray, top_k: int, ideas: List) -> List[Tuple[str, float]]:
        """
        Simple cosine similarity search (for small datasets).
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            ideas: List of ideas
            
        Returns:
            List of (idea_id, similarity_score) tuples
        """
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
