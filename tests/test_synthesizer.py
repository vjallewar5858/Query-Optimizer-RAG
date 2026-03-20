"""
Tests for Answer Synthesizer module.
"""

import unittest
from src.models.synthesizer import AnswerSynthesizer

class TestAnswerSynthesizer(unittest.TestCase):
    """Test cases for AnswerSynthesizer"""
    
    def test_format_context(self):
        """Test context formatting"""
        sub_questions = [
            "What is photosynthesis?",
            "What is chemosynthesis?"
        ]
        
        retrieved_docs = [
            [
                {"content": "Photosynthesis uses light", "source": "bio.txt", "similarity": 0.95},
                {"content": "Plants do photosynthesis", "source": "plants.txt", "similarity": 0.88}
            ],
            [
                {"content": "Chemosynthesis uses chemicals", "source": "bio.txt", "similarity": 0.92}
            ]
        ]
        
        context = AnswerSynthesizer._format_context(sub_questions, retrieved_docs)
        
        # Check that context includes sub-questions
        self.assertIn("What is photosynthesis", context)
        self.assertIn("What is chemosynthesis", context)
        
        # Check that context includes document info
        self.assertIn("Photosynthesis uses light", context)
        self.assertIn("bio.txt", context)
        self.assertIn("0.95", context)
    
    def test_format_context_empty_docs(self):
        """Test formatting with no documents"""
        sub_questions = ["What is X?"]
        retrieved_docs = [[]]  # No documents
        
        context = AnswerSynthesizer._format_context(sub_questions, retrieved_docs)
        
        # Should gracefully handle empty results
        self.assertIn("What is X?", context)
        self.assertIn("No relevant documents", context)


if __name__ == "__main__":
    unittest.main()
