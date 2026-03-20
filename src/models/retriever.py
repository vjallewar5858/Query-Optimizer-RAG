"""
Retriever module.
Performs semantic search to find relevant documents for queries.
"""

from typing import List, Tuple
import numpy as np
from src.utils.embeddings import EmbeddingGenerator
from src.utils.database import VectorDatabase
from src.utils.logger import get_logger
from config.settings import (
    EMBEDDING_MODEL, VECTOR_DB_PATH, TOP_K,
    SIMILARITY_THRESHOLD, ENABLE_SIMILARITY_THRESHOLD
)

logger = get_logger(__name__)

class DocumentRetriever:
    """
    Retrieves relevant documents for queries using semantic search.
    
    How it works:
    1. Convert query to embedding (same as documents)
    2. Compare query embedding to all document embeddings
    3. Find most similar documents using cosine similarity
    4. Return top-K results with similarity scores
    
    Semantic search finds meaning-based matches, not just keyword matches.
    """
    
    def __init__(self, embedding_model: str = EMBEDDING_MODEL, 
                 db_path: str = VECTOR_DB_PATH):
        """
        Initialize retriever with embedding model and database.
        
        Args:
            embedding_model: Name of embedding model to use
            db_path: Path to vector database
        """
        logger.info("Initializing DocumentRetriever...")
        self.embeddings = EmbeddingGenerator(embedding_model)
        self.db = VectorDatabase(db_path)
        logger.info("✓ DocumentRetriever initialized")
    
    def retrieve(self, query: str, top_k: int = TOP_K) -> List[dict]:
        """
        Retrieve most relevant documents for a query.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of dicts with keys: content, source, similarity
        """
        logger.debug(f"Retrieving documents for: {query[:80]}...")
        
        if self.db.count_documents() == 0:
            logger.warning("No documents in database. Index documents first.")
            return []
        
        # Convert query to embedding
        query_embedding = self.embeddings.embed_single(query)
        
        # Search database
        results = self.db.search(query_embedding, top_k)
        
        # Format results
        formatted_results = []
        for content, source, similarity in results:
            # Filter by similarity threshold if enabled
            if ENABLE_SIMILARITY_THRESHOLD and similarity < SIMILARITY_THRESHOLD:
                logger.debug(f"  Skipping result with low similarity: {similarity:.3f}")
                continue
            
            formatted_results.append({
                "content": content,
                "source": source or "Unknown",
                "similarity": similarity
            })
        
        logger.info(f"✓ Retrieved {len(formatted_results)} documents")
        return formatted_results
    
    def retrieve_batch(self, queries: List[str], top_k: int = TOP_K) -> List[List[dict]]:
        """
        Retrieve documents for multiple queries efficiently.
        
        Args:
            queries: List of query strings
            top_k: Number of results per query
            
        Returns:
            List of result lists (one per query)
        """
        logger.info(f"Batch retrieving for {len(queries)} queries...")
        results = [self.retrieve(q, top_k) for q in queries]
        logger.info(f"✓ Batch retrieval complete")
        return results
    
    def close(self):
        """Close database connection."""
        self.db.close()
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, *args):
        """Context manager cleanup."""
        self.close()
