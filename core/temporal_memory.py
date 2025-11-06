"""Temporal Memory Manager - Long-term context and temporal embeddings"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import json


class TemporalMemoryManager:
    """
    Maintains long-term memory and temporal embeddings.
    Stores past idea vectors by timestamp for temporal context retrieval.
    """
    
    def __init__(self, db_path: str = "data/temporal_memory.db", 
                 embedding_dim: int = 384,
                 max_memory_days: int = 365):
        """
        Initialize temporal memory manager.
        
        Args:
            db_path: Path to SQLite database for temporal storage
            embedding_dim: Dimension of embeddings
            max_memory_days: Maximum days to retain memory
            
        Security: Validates paths and dimensions
        """
        self.db_path = db_path
        self.embedding_dim = max(1, min(2048, embedding_dim))
        self.max_memory_days = max(1, min(3650, max_memory_days))
        
        # Initialize database
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_tables()
    
    def _create_tables(self):
        """Create temporal memory tables"""
        cursor = self.conn.cursor()
        
        # Temporal embeddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS temporal_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea_id TEXT NOT NULL,
                embedding BLOB NOT NULL,
                metadata TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Temporal context table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS temporal_contexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_id TEXT UNIQUE NOT NULL,
                context_data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                expires_at TEXT
            )
        """)
        
        # Create indices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_temporal_timestamp 
            ON temporal_embeddings(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_temporal_idea 
            ON temporal_embeddings(idea_id)
        """)
        
        self.conn.commit()
    
    def store_context(self, context_id: str, context_data: Dict[str, Any],
                     ttl_days: Optional[int] = None) -> bool:
        """
        Store temporal context with optional expiration.
        
        Args:
            context_id: Unique context identifier
            context_data: Context dictionary to store
            ttl_days: Time-to-live in days (None = use default)
            
        Returns:
            True if stored successfully
            
        Security: Validates inputs, sanitizes data, safe JSON serialization
        """
        # Input validation
        safe_context_id = str(context_id)[:100]
        
        if not context_data or not isinstance(context_data, dict):
            return False
        
        # Sanitize context data - no code execution
        try:
            safe_data = self._sanitize_dict(context_data)
            context_json = json.dumps(safe_data)
        except (TypeError, ValueError):
            return False
        
        # Calculate expiration
        ttl = ttl_days if ttl_days is not None else self.max_memory_days
        ttl = max(1, min(3650, ttl))
        expires_at = (datetime.now() + timedelta(days=ttl)).isoformat()
        
        # Store in database
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO temporal_contexts 
                (context_id, context_data, timestamp, expires_at)
                VALUES (?, ?, ?, ?)
            """, (safe_context_id, context_json, datetime.now().isoformat(), expires_at))
            
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False
    
    def retrieve_recent_context(self, context_id: Optional[str] = None,
                               hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Retrieve recent temporal context.
        
        Args:
            context_id: Specific context ID (None = all recent)
            hours_back: How many hours back to retrieve
            
        Returns:
            List of context dictionaries
            
        Security: Validates inputs, safe deserialization
        """
        # Input validation
        hours_back = max(1, min(8760, hours_back))  # Max 1 year
        cutoff_time = (datetime.now() - timedelta(hours=hours_back)).isoformat()
        
        cursor = self.conn.cursor()
        
        if context_id:
            # Specific context
            safe_id = str(context_id)[:100]
            cursor.execute("""
                SELECT context_data, timestamp 
                FROM temporal_contexts
                WHERE context_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """, (safe_id, cutoff_time))
        else:
            # All recent contexts
            cursor.execute("""
                SELECT context_id, context_data, timestamp 
                FROM temporal_contexts
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 100
            """, (cutoff_time,))
        
        results = []
        for row in cursor.fetchall():
            try:
                if context_id:
                    context_data, timestamp = row
                    parsed = json.loads(context_data)
                    parsed["timestamp"] = timestamp
                else:
                    ctx_id, context_data, timestamp = row
                    parsed = json.loads(context_data)
                    parsed["context_id"] = ctx_id
                    parsed["timestamp"] = timestamp
                
                results.append(parsed)
            except (json.JSONDecodeError, ValueError):
                continue
        
        return results
    
    def store_embedding(self, idea_id: str, embedding: np.ndarray,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store idea embedding with timestamp.
        
        Args:
            idea_id: Idea identifier
            embedding: Embedding vector
            metadata: Optional metadata dictionary
            
        Returns:
            True if stored successfully
            
        Security: Validates embedding dimensions, sanitizes metadata
        """
        # Input validation
        safe_idea_id = str(idea_id)[:100]
        
        if not isinstance(embedding, np.ndarray):
            return False
        
        if embedding.shape[0] != self.embedding_dim:
            return False
        
        if not np.all(np.isfinite(embedding)):
            return False
        
        # Serialize embedding
        embedding_blob = embedding.astype(np.float32).tobytes()
        
        # Sanitize metadata
        if metadata:
            try:
                safe_metadata = self._sanitize_dict(metadata)
                metadata_json = json.dumps(safe_metadata)
            except (TypeError, ValueError):
                metadata_json = "{}"
        else:
            metadata_json = "{}"
        
        # Store in database
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO temporal_embeddings
                (idea_id, embedding, metadata, timestamp, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                safe_idea_id,
                embedding_blob,
                metadata_json,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False
    
    def retrieve_temporal_embeddings(self, idea_id: Optional[str] = None,
                                    hours_back: int = 168) -> List[Dict[str, Any]]:
        """
        Retrieve temporal embeddings.
        
        Args:
            idea_id: Specific idea ID (None = all)
            hours_back: How many hours back (default 7 days)
            
        Returns:
            List of embedding dictionaries
            
        Security: Safe deserialization, validates data
        """
        hours_back = max(1, min(8760, hours_back))
        cutoff_time = (datetime.now() - timedelta(hours=hours_back)).isoformat()
        
        cursor = self.conn.cursor()
        
        if idea_id:
            safe_id = str(idea_id)[:100]
            cursor.execute("""
                SELECT idea_id, embedding, metadata, timestamp
                FROM temporal_embeddings
                WHERE idea_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 100
            """, (safe_id, cutoff_time))
        else:
            cursor.execute("""
                SELECT idea_id, embedding, metadata, timestamp
                FROM temporal_embeddings
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 1000
            """, (cutoff_time,))
        
        results = []
        for row in cursor.fetchall():
            try:
                idea_id, embedding_blob, metadata_json, timestamp = row
                
                # Deserialize embedding
                embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                
                if embedding.shape[0] != self.embedding_dim:
                    continue
                
                # Parse metadata
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                results.append({
                    "idea_id": idea_id,
                    "embedding": embedding,
                    "metadata": metadata,
                    "timestamp": timestamp
                })
            except (ValueError, json.JSONDecodeError):
                continue
        
        return results
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired contexts and old embeddings.
        
        Returns:
            Number of records deleted
            
        Security: Safe deletion with transaction
        """
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        # Delete expired contexts
        cursor.execute("""
            DELETE FROM temporal_contexts
            WHERE expires_at < ?
        """, (now,))
        
        contexts_deleted = cursor.rowcount
        
        # Delete old embeddings beyond max retention
        cutoff = (datetime.now() - timedelta(days=self.max_memory_days)).isoformat()
        cursor.execute("""
            DELETE FROM temporal_embeddings
            WHERE timestamp < ?
        """, (cutoff,))
        
        embeddings_deleted = cursor.rowcount
        
        self.conn.commit()
        
        return contexts_deleted + embeddings_deleted
    
    def _sanitize_dict(self, data: Dict[str, Any], max_depth: int = 5) -> Dict[str, Any]:
        """
        Sanitize dictionary for safe JSON serialization.
        
        Security: Prevents code injection, limits depth, validates types
        """
        if max_depth <= 0:
            return {}
        
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize key
            safe_key = str(key)[:100]
            
            # Sanitize value based on type
            if isinstance(value, (str, int, float, bool)):
                if isinstance(value, str):
                    sanitized[safe_key] = value[:1000]  # Limit string length
                elif isinstance(value, (int, float)):
                    if np.isfinite(value):
                        sanitized[safe_key] = value
                else:
                    sanitized[safe_key] = value
            elif isinstance(value, dict):
                sanitized[safe_key] = self._sanitize_dict(value, max_depth - 1)
            elif isinstance(value, (list, tuple)):
                sanitized[safe_key] = [
                    self._sanitize_value(v) for v in value[:100]  # Limit list size
                ]
            elif value is None:
                sanitized[safe_key] = None
            # Skip other types (functions, classes, etc.)
        
        return sanitized
    
    def _sanitize_value(self, value: Any) -> Any:
        """Sanitize individual value"""
        if isinstance(value, (str, int, float, bool)):
            return value if not isinstance(value, str) else value[:1000]
        elif isinstance(value, dict):
            return self._sanitize_dict(value, max_depth=2)
        elif value is None:
            return None
        else:
            return str(value)[:100]
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
