"""
Query Decomposer module.
Breaks complex questions into simpler, answerable sub-questions.
"""

from typing import List
import anthropic
from src.utils.logger import get_logger

logger = get_logger(__name__)

class QueryDecomposer:
    """
    Decomposes complex questions into sub-questions.
    
    How it works:
    1. Analyzes the input question
    2. Identifies implicit questions within it
    3. Breaks it into focused, answerable parts
    4. Ensures sub-questions are specific and clear
    
    This makes retrieval more effective because each sub-question
    has a clearer semantic meaning to search for.
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize the decomposer with Anthropic API.
        
        Args:
            api_key: Anthropic API key
            model: Claude model name to use
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        logger.info(f"✓ QueryDecomposer initialized with model {model}")
    
    def decompose(self, question: str, max_questions: int = 5) -> List[str]:
        """
        Break a complex question into sub-questions.
        
        Args:
            question: The original complex question
            max_questions: Maximum number of sub-questions to generate
            
        Returns:
            List of sub-questions
        """
        logger.info(f"Decomposing question: {question[:100]}...")
        
        system_prompt = f"""You are an expert question analyzer. Your task is to break down 
complex questions into 2-{max_questions} simpler, specific sub-questions.

Guidelines:
1. Each sub-question should be answerable independently
2. Sub-questions should cover different aspects of the original question
3. Avoid repetition between sub-questions
4. Keep questions focused and specific (not vague)
5. Order by logical dependency (foundational questions first)

Return ONLY the sub-questions as a numbered list, nothing else.
Example format:
1. What is photosynthesis?
2. How does photosynthesis differ from cellular respiration?
3. What organisms use photosynthesis?"""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Break down this question:\n{question}"
                    }
                ]
            )
            
            response_text = message.content[0].text
            sub_questions = self._parse_questions(response_text)
            
            logger.info(f"✓ Generated {len(sub_questions)} sub-questions")
            for i, sq in enumerate(sub_questions, 1):
                logger.debug(f"  {i}. {sq}")
            
            return sub_questions
            
        except Exception as e:
            logger.error(f"Error decomposing question: {e}")
            # Fallback: return original question
            return [question]
    
    @staticmethod
    def _parse_questions(response: str) -> List[str]:
        """
        Parse numbered questions from LLM response.
        
        Args:
            response: Raw response text containing numbered questions
            
        Returns:
            List of cleaned question strings
        """
        questions = []
        lines = response.strip().split('\n')
        
        for line in lines:
            # Remove numbering (1., 2., etc.)
            line = line.strip()
            if line and any(line.startswith(f"{i}.") for i in range(1, 20)):
                # Remove the number prefix
                question = line.split(".", 1)[1].strip()
                if question:
                    questions.append(question)
        
        return questions if questions else [response.strip()]
