"""
Embedding generation utilities.
Converts text into vector representations for semantic similarity.
"""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from src.utils.logger import get_logger

logger = get_logger(__name__)

class EmbeddingGenerator:
    """
    Generates embeddings (vector representations) for text.
    
    Embeddings are numerical representations of text meaning.
    Similar texts get similar vectors, enabling semantic search.
    """
    
    def __init__(self, model_name: str):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence-transformers model to use
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("✓ Embedding model loaded")
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Convert multiple texts to embeddings.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Numpy array of shape (len(texts), embedding_dim)
        """
        logger.debug(f"Embedding {len(texts)} texts...")
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32
        )
        logger.debug(f"✓ Generated embeddings with shape {embeddings.shape}")
        return embeddings
    
    def embed_single(self, text: str) -> np.ndarray:
        """
        Embed a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            1D numpy array (embedding vector)
        """
        return self.model.encode(text)
    
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embedding vectors.
        
        Args:
            vec1: First embedding vector
            vec2: Second embedding vector
            
        Returns:
            Similarity score between -1 and 1 (higher = more similar)
        """
        # Cosine similarity: dot product of normalized vectors
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
