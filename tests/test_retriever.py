"""
Tests for Document Retriever module.
"""

import unittest
import numpy as np
from src.utils.database import VectorDatabase
from src.utils.embeddings import EmbeddingGenerator
import tempfile
import os

class TestVectorDatabase(unittest.TestCase):
    """Test cases for VectorDatabase"""
    
    def setUp(self):
        """Create temporary database for testing"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()
        self.db = VectorDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up temporary database"""
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_add_document(self):
        """Test adding document to database"""
        content = "Test document content"
        embedding = np.random.rand(384).astype(np.float32)
        
        doc_id = self.db.add_document(content, embedding, source="test.txt")
        
        self.assertIsNotNone(doc_id)
        self.assertGreater(doc_id, 0)
    
    def test_count_documents(self):
        """Test document counting"""
        # Add 3 documents
        for i in range(3):
            embedding = np.random.rand(384).astype(np.float32)
            self.db.add_document(f"Document {i}", embedding)
        
        count = self.db.count_documents()
        self.assertEqual(count, 3)
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        vec1 = np.array([1, 0, 0], dtype=np.float32)
        vec2 = np.array([1, 0, 0], dtype=np.float32)
        vec3 = np.array([0, 1, 0], dtype=np.float32)
        
        # Same vectors should have similarity 1.0
        sim_same = VectorDatabase._cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(sim_same, 1.0, places=5)
        
        # Orthogonal vectors should have similarity 0.0
        sim_orth = VectorDatabase._cosine_similarity(vec1, vec3)
        self.assertAlmostEqual(sim_orth, 0.0, places=5)
    
    def test_search(self):
        """Test semantic search"""
        # Add multiple documents
        for i in range(5):
            embedding = np.random.rand(384).astype(np.float32)
            self.db.add_document(f"Document {i}", embedding, source=f"doc{i}.txt")
        
        # Search with random query
        query_embedding = np.random.rand(384).astype(np.float32)
        results = self.db.search(query_embedding, top_k=3)
        
        self.assertEqual(len(results), 3)
        # Results should have (content, source, similarity) structure
        for result in results:
            self.assertEqual(len(result), 3)
            self.assertIsInstance(result[2], float)  # similarity score


if __name__ == "__main__":
    unittest.main()
