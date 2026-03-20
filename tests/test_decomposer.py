"""
Tests for Query Decomposer module.
"""

import unittest
from unittest.mock import Mock, patch
from src.models.decomposer import QueryDecomposer

class TestQueryDecomposer(unittest.TestCase):
    """Test cases for QueryDecomposer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test-key"
    
    def test_parse_questions(self):
        """Test parsing numbered questions from text"""
        response = """1. What is photosynthesis?
2. How does it differ from chemosynthesis?
3. Why is it important?"""
        
        questions = QueryDecomposer._parse_questions(response)
        
        self.assertEqual(len(questions), 3)
        self.assertIn("photosynthesis", questions[0].lower())
        self.assertIn("chemosynthesis", questions[1].lower())
    
    def test_parse_questions_with_extra_text(self):
        """Test parsing questions with extra formatting"""
        response = """Here are the questions:
1. Question one
2. Question two
Some extra text here"""
        
        questions = QueryDecomposer._parse_questions(response)
        
        self.assertGreaterEqual(len(questions), 2)
        self.assertIn("one", questions[0])
    
    def test_empty_response(self):
        """Test handling empty response"""
        response = ""
        questions = QueryDecomposer._parse_questions(response)
        
        # Should handle gracefully
        self.assertIsInstance(questions, list)


if __name__ == "__main__":
    unittest.main()
