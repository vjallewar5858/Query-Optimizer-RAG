"""
Configuration settings for Query Optimizer RAG system.
All parameters can be overridden via environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_DB_PATH = DATA_DIR / "vector_db.db"

# Create directories if they don't exist
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError(
        "ANTHROPIC_API_KEY not found in environment. "
        "Create a .env file with your API key. See .env.example"
    )

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "claude-3-5-sonnet-20241022")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))

# Retrieval Configuration
TOP_K = int(os.getenv("TOP_K", "5"))  # Number of documents to retrieve per sub-question
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))  # Characters per document chunk
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))  # Overlap between chunks

# Embedding Configuration
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)
EMBEDDING_DIM = 384  # Dimension of embeddings (depends on model)

# Query Decomposition
MAX_SUB_QUESTIONS = int(os.getenv("MAX_SUB_QUESTIONS", "5"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Feature Flags
ENABLE_SIMILARITY_THRESHOLD = os.getenv("ENABLE_SIMILARITY_THRESHOLD", "true").lower() == "true"
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))

print(f"✓ Configuration loaded")
print(f"  Model: {MODEL_NAME}")
print(f"  Embedding: {EMBEDDING_MODEL}")
print(f"  Database: {VECTOR_DB_PATH}")
