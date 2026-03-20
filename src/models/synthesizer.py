"""
Answer Synthesizer module.
Combines retrieved information into coherent answers.
"""

from typing import List, Dict
import anthropic
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AnswerSynthesizer:
    """
    Synthesizes final answers from retrieved documents.
    
    How it works:
    1. Takes original question + all retrieved documents
    2. Uses LLM to understand relationships between documents
    3. Generates a coherent answer that synthesizes all information
    4. Includes source attribution for credibility
    
    This ensures the answer is:
    - Comprehensive (covers all aspects)
    - Coherent (logically flows)
    - Cited (traceable back to sources)
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize synthesizer with Anthropic API.
        
        Args:
            api_key: Anthropic API key
            model: Claude model name to use
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        logger.info(f"✓ AnswerSynthesizer initialized with model {model}")
    
    def synthesize(self, 
                   original_question: str,
                   sub_questions: List[str],
                   retrieved_docs: List[List[dict]]) -> str:
        """
        Synthesize a comprehensive answer from retrieved documents.
        
        Args:
            original_question: The original complex question
            sub_questions: List of decomposed questions
            retrieved_docs: List of retrieved documents for each sub-question
                           Structure: List[List[{"content": str, "source": str, "similarity": float}]]
            
        Returns:
            Synthesized answer with citations
        """
        logger.info("Synthesizing answer from retrieved documents...")
        
        # Prepare context from retrieved documents
        context = self._format_context(sub_questions, retrieved_docs)
        
        system_prompt = """You are an expert synthesizer. Your task is to create a comprehensive,
coherent answer that synthesizes information from multiple sources.

Guidelines:
1. Answer the original question thoroughly
2. Use information from ALL provided documents
3. Cite sources clearly (e.g., [Source: document name])
4. Organize information logically (related concepts together)
5. Connect ideas between documents to show relationships
6. Be accurate - don't invent information not in the documents
7. If documents conflict, acknowledge both perspectives
8. Make the answer easy to understand for someone with zero background knowledge

Format your answer clearly with logical sections if needed."""
        
        user_message = f"""Original Question: {original_question}

Context from Multiple Sources:
{context}

Please synthesize a comprehensive answer that addresses the original question using all 
the information provided above. Include citations to show where information came from."""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            answer = message.content[0].text
            logger.info("✓ Answer synthesis complete")
            return answer
            
        except Exception as e:
            logger.error(f"Error synthesizing answer: {e}")
            return f"Error generating answer: {str(e)}"
    
    @staticmethod
    def _format_context(sub_questions: List[str], 
                       retrieved_docs: List[List[dict]]) -> str:
        """
        Format retrieved documents into readable context.
        
        Groups documents by sub-question for clarity.
        
        Args:
            sub_questions: Original sub-questions
            retrieved_docs: Retrieved documents for each
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, (sub_q, docs) in enumerate(zip(sub_questions, retrieved_docs), 1):
            context_parts.append(f"\n--- For Sub-question {i}: {sub_q} ---")
            
            if not docs:
                context_parts.append("(No relevant documents found)")
                continue
            
            for j, doc in enumerate(docs, 1):
                source = doc.get("source", "Unknown")
                similarity = doc.get("similarity", 0)
                content = doc.get("content", "")[:500]  # Limit length
                
                context_parts.append(
                    f"\nDocument {j} (From: {source}, Relevance: {similarity:.2f})\n"
                    f"{content}..."
                )
        
        return "\n".join(context_parts)
    
    def generate_summary(self, answer: str, max_length: int = 200) -> str:
        """
        Generate a short summary of the answer.
        
        Args:
            answer: Full answer text
            max_length: Maximum length of summary
            
        Returns:
            Brief summary
        """
        logger.debug("Generating answer summary...")
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize this in {max_length} characters or less:\n\n{answer}"
                    }
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Fallback: return first portion
            return answer[:max_length] + "..."
