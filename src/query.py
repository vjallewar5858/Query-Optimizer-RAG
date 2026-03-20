"""
Main Query Interface.
Orchestrates the complete RAG pipeline: decomposition -> retrieval -> synthesis.
"""

import argparse
from typing import List, Dict
from src.models.decomposer import QueryDecomposer
from src.models.retriever import DocumentRetriever
from src.models.synthesizer import AnswerSynthesizer
from src.utils.logger import get_logger
from config.settings import (
    ANTHROPIC_API_KEY, TOP_K, VECTOR_DB_PATH, EMBEDDING_MODEL
)

logger = get_logger(__name__)

class QueryOptimizer:
    """
    Complete RAG system: Decompose -> Retrieve -> Synthesize.
    
    This orchestrates the three-step process:
    1. Decompose: Break question into sub-questions
    2. Retrieve: Find relevant documents for each sub-question
    3. Synthesize: Combine documents into coherent answer
    """
    
    def __init__(self, 
                 api_key: str = ANTHROPIC_API_KEY,
                 model: str = "claude-3-5-sonnet-20241022",
                 embedding_model: str = EMBEDDING_MODEL,
                 db_path: str = VECTOR_DB_PATH,
                 top_k: int = TOP_K):
        """
        Initialize the Query Optimizer.
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
            embedding_model: Embedding model for similarity
            db_path: Path to vector database
            top_k: Number of documents to retrieve per question
        """
        logger.info("Initializing Query Optimizer system...")
        
        self.decomposer = QueryDecomposer(api_key, model)
        self.retriever = DocumentRetriever(embedding_model, db_path)
        self.synthesizer = AnswerSynthesizer(api_key, model)
        self.top_k = top_k
        
        logger.info("✓ Query Optimizer ready")
    
    def query(self, question: str, return_intermediate: bool = False) -> Dict:
        """
        Process a question through the complete RAG pipeline.
        
        Args:
            question: The user's question
            return_intermediate: If True, include decomposition and retrieval in response
            
        Returns:
            Dict with keys: question, answer, and optionally sub_questions, retrieved_docs
        """
        logger.info("\n" + "="*70)
        logger.info(f"Processing: {question}")
        logger.info("="*70)
        
        result = {"question": question}
        
        try:
            # Step 1: Decompose
            logger.info("\n[1/3] Decomposing question...")
            sub_questions = self.decomposer.decompose(question)
            result["sub_questions"] = sub_questions
            
            for i, sq in enumerate(sub_questions, 1):
                logger.info(f"      {i}. {sq}")
            
            # Step 2: Retrieve
            logger.info("\n[2/3] Retrieving relevant documents...")
            retrieved_docs = self.retriever.retrieve_batch(sub_questions, self.top_k)
            
            for i, (sq, docs) in enumerate(zip(sub_questions, retrieved_docs), 1):
                logger.info(f"      Sub-q {i}: Found {len(docs)} relevant documents")
                for doc in docs[:2]:  # Show top 2
                    logger.debug(f"        - {doc['source']} (similarity: {doc['similarity']:.2f})")
            
            result["retrieved_docs_count"] = sum(len(d) for d in retrieved_docs)
            if return_intermediate:
                result["retrieved_docs"] = retrieved_docs
            
            # Step 3: Synthesize
            logger.info("\n[3/3] Synthesizing answer...")
            answer = self.synthesizer.synthesize(question, sub_questions, retrieved_docs)
            result["answer"] = answer
            
            logger.info("✓ Processing complete")
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            result["answer"] = f"Error: {str(e)}"
            result["error"] = True
        
        return result
    
    def close(self):
        """Clean up resources."""
        self.retriever.close()
        logger.info("✓ Query Optimizer closed")
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, *args):
        """Context manager cleanup."""
        self.close()


def format_output(result: Dict) -> str:
    """Format result for console display."""
    output_lines = []
    
    output_lines.append("\n" + "="*70)
    output_lines.append("QUERY OPTIMIZER RESULT")
    output_lines.append("="*70)
    
    output_lines.append(f"\nOriginal Question:\n{result['question']}")
    
    if "sub_questions" in result:
        output_lines.append("\n" + "-"*70)
        output_lines.append("Sub-questions identified:")
        for i, sq in enumerate(result['sub_questions'], 1):
            output_lines.append(f"  {i}. {sq}")
    
    output_lines.append("\n" + "-"*70)
    output_lines.append("SYNTHESIZED ANSWER:")
    output_lines.append("-"*70)
    output_lines.append(result['answer'])
    
    if "retrieved_docs_count" in result:
        output_lines.append("\n" + "-"*70)
        output_lines.append(f"Retrieved {result['retrieved_docs_count']} relevant documents")
    
    output_lines.append("\n" + "="*70)
    
    return "\n".join(output_lines)


def main():
    """Command-line interface for querying."""
    parser = argparse.ArgumentParser(
        description="Query the RAG system with complex questions"
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Your question"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show intermediate results (decomposition, retrieval)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=TOP_K,
        help="Number of documents to retrieve per sub-question"
    )
    
    args = parser.parse_args()
    
    logger.info("Query Optimizer RAG System")
    logger.info("Starting query interface...")
    
    try:
        optimizer = QueryOptimizer(top_k=args.top_k)
        result = optimizer.query(args.query, return_intermediate=args.verbose)
        
        # Format and print result
        formatted_output = format_output(result)
        print(formatted_output)
        
        # Save result to file
        with open("last_query_result.txt", "w") as f:
            f.write(formatted_output)
        logger.info("✓ Result saved to last_query_result.txt")
        
        optimizer.close()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
