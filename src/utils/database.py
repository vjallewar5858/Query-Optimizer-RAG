"""
Vector database management.
Stores document embeddings and enables semantic search.
"""

import sqlite3
import json
import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger(__name__)

class VectorDatabase:
    """
    Simple SQLite-based vector database.
    
    This is a lightweight vector store for demonstration.
    For production, consider: Pinecone, Weaviate, Milvus, FAISS, etc.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize vector database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Create database tables if they don't exist."""
        self.conn = sqlite3.connect(str(self.db_path))
        cursor = self.conn.cursor()
        
        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source TEXT,
                chunk_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Embeddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                embedding BLOB NOT NULL,
                FOREIGN KEY(document_id) REFERENCES documents(id)
            )
        """)
        
        self.conn.commit()
        logger.info(f"✓ Vector database initialized at {self.db_path}")
    
    def add_document(self, content: str, embedding: np.ndarray, source: str = None) -> int:
        """
        Add a document with its embedding.
        
        Args:
            content: Document text content
            embedding: Numpy array (vector representation)
            source: Original source of the document (filename, URL, etc.)
            
        Returns:
            Document ID
        """
        cursor = self.conn.cursor()
        
        # Insert document
        cursor.execute(
            "INSERT INTO documents (content, source) VALUES (?, ?)",
            (content, source)
        )
        doc_id = cursor.lastrowid
        
        # Insert embedding (convert numpy array to binary)
        embedding_bytes = embedding.astype(np.float32).tobytes()
        cursor.execute(
            "INSERT INTO embeddings (document_id, embedding) VALUES (?, ?)",
            (doc_id, embedding_bytes)
        )
        
        self.conn.commit()
        return doc_id
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple]:
        """
        Find most similar documents to query embedding.
        
        Uses cosine similarity for semantic search.
        
        Args:
            query_embedding: Query as numpy vector
            top_k: Number of results to return
            
        Returns:
            List of (content, source, similarity_score) tuples
        """
        cursor = self.conn.cursor()
        
        # Get all documents with embeddings
        cursor.execute("""
            SELECT d.id, d.content, d.source, e.embedding
            FROM documents d
            JOIN embeddings e ON d.id = e.document_id
        """)
        
        results = []
        for doc_id, content, source, embedding_bytes in cursor.fetchall():
            # Convert binary back to numpy array
            embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, embedding)
            results.append((content, source, similarity))
        
        # Sort by similarity (descending) and return top_k
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:top_k]
    
    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Cosine similarity measures angle between vectors.
        - 1.0 = identical direction (very similar)
        - 0.0 = perpendicular (unrelated)
        - -1.0 = opposite direction (very different)
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score between -1 and 1
        """
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    def get_document(self, doc_id: int) -> Optional[Tuple]:
        """
        Retrieve a document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            (content, source) tuple or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT content, source FROM documents WHERE id = ?", (doc_id,))
        result = cursor.fetchone()
        return result
    
    def count_documents(self) -> int:
        """Get total number of indexed documents."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        return cursor.fetchone()[0]
    
    def clear(self):
        """Delete all documents and embeddings."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM embeddings")
        cursor.execute("DELETE FROM documents")
        self.conn.commit()
        logger.info("✓ Database cleared")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("✓ Database connection closed")
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, *args):
        """Context manager cleanup."""
        self.close()
