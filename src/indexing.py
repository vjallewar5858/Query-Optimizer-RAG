"""
Document Indexing Pipeline.
Processes documents and creates embeddings for the vector database.
"""

import argparse
from pathlib import Path
from typing import List
import re
from src.utils.embeddings import EmbeddingGenerator
from src.utils.database import VectorDatabase
from src.utils.logger import get_logger
from config.settings import (
    EMBEDDING_MODEL, VECTOR_DB_PATH, DOCUMENTS_DIR,
    CHUNK_SIZE, CHUNK_OVERLAP
)

logger = get_logger(__name__)

class DocumentIndexer:
    """
    Indexes documents by converting them to embeddings.
    
    Process:
    1. Load documents from files
    2. Split documents into chunks (for context preservation)
    3. Generate embeddings for each chunk
    4. Store in vector database
    """
    
    def __init__(self, embedding_model: str = EMBEDDING_MODEL,
                 db_path: str = VECTOR_DB_PATH,
                 chunk_size: int = CHUNK_SIZE,
                 chunk_overlap: int = CHUNK_OVERLAP):
        """
        Initialize indexer.
        
        Args:
            embedding_model: Name of embedding model
            db_path: Path to vector database
            chunk_size: Characters per chunk
            chunk_overlap: Overlap between chunks to preserve context
        """
        self.embeddings = EmbeddingGenerator(embedding_model)
        self.db = VectorDatabase(db_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info("✓ DocumentIndexer initialized")
    
    def index_documents(self, documents_dir: str, refresh: bool = False):
        """
        Index all documents in a directory.
        
        Args:
            documents_dir: Directory containing document files (.txt)
            refresh: If True, clear database before indexing
        """
        documents_path = Path(documents_dir)
        
        if not documents_path.exists():
            logger.error(f"Documents directory not found: {documents_dir}")
            return
        
        if refresh:
            logger.info("Clearing existing database...")
            self.db.clear()
        
        # Find all text files
        text_files = list(documents_path.glob("*.txt"))
        
        if not text_files:
            logger.warning(f"No .txt files found in {documents_dir}")
            return
        
        logger.info(f"Found {len(text_files)} documents to index")
        
        total_chunks = 0
        for file_path in text_files:
            logger.info(f"Indexing: {file_path.name}")
            chunks = self._chunk_document(str(file_path))
            
            # Generate embeddings and store
            for chunk in chunks:
                embedding = self.embeddings.embed_single(chunk)
                self.db.add_document(chunk, embedding, source=file_path.name)
            
            total_chunks += len(chunks)
            logger.info(f"  ✓ Created {len(chunks)} chunks")
        
        logger.info(f"✓ Indexing complete: {total_chunks} total chunks in database")
    
    def _chunk_document(self, file_path: str) -> List[str]:
        """
        Split document into overlapping chunks.
        
        Args:
            file_path: Path to document file
            
        Returns:
            List of text chunks
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into chunks with overlap
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + self.chunk_size
            chunk = content[start:end]
            
            # Avoid splitting mid-sentence (break at period)
            if end < len(content):
                last_period = chunk.rfind('.')
                if last_period > self.chunk_size // 2:  # Only if period is substantial
                    end = start + last_period + 1
                    chunk = content[start:end]
            
            chunks.append(chunk.strip())
            
            # Move start position with overlap
            start = end - self.chunk_overlap
        
        return [c for c in chunks if len(c) > 50]  # Filter very small chunks
    
    def clear_index(self):
        """Delete all indexed documents."""
        logger.info("Clearing database...")
        self.db.clear()
    
    def get_stats(self) -> dict:
        """Get indexing statistics."""
        count = self.db.count_documents()
        return {
            "total_documents": count,
            "database_path": str(self.db.db_path)
        }
    
    def close(self):
        """Close database connection."""
        self.db.close()


def main():
    """Command-line interface for indexing documents."""
    parser = argparse.ArgumentParser(
        description="Index documents for RAG system"
    )
    parser.add_argument(
        "--documents-dir",
        type=str,
        default=str(DOCUMENTS_DIR),
        help="Directory containing documents to index"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(VECTOR_DB_PATH),
        help="Path to output vector database"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Clear existing database before indexing"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Starting Document Indexing Pipeline")
    logger.info("=" * 60)
    
    indexer = DocumentIndexer(db_path=args.output)
    
    try:
        indexer.index_documents(args.documents_dir, refresh=args.refresh)
        stats = indexer.get_stats()
        logger.info(f"\nIndexing Statistics:")
        logger.info(f"  Total documents: {stats['total_documents']}")
        logger.info(f"  Database: {stats['database_path']}")
    
    except Exception as e:
        logger.error(f"Error during indexing: {e}")
    
    finally:
        indexer.close()


if __name__ == "__main__":
    main()
