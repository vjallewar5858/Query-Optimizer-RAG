# Query Optimizer RAG

A production-ready Retrieval-Augmented Generation (RAG) system that intelligently breaks down complex questions into simpler sub-questions, retrieves relevant information, and synthesizes comprehensive answers.

## What is this project?

Imagine you ask a complex question like:
> "What's the difference between photosynthesis in plants versus chemosynthesis in deep-sea bacteria, and why did photosynthesis become dominant?"

Without Query Optimizer, a simple RAG system would:
1. Search for information about photosynthesis
2. Maybe miss the comparison angle
3. Return fragmented answers

**With Query Optimizer**, the system:
1. **Understands** your question is actually 3 questions
2. **Breaks it down** into: "What is photosynthesis?", "What is chemosynthesis?", "Why photosynthesis dominance?"
3. **Retrieves** specific information for each sub-question
4. **Synthesizes** a coherent, comprehensive answer that ties everything together

This is useful because real-world questions are rarely simple. They often require:
- Comparisons between concepts
- Historical context
- Multi-step reasoning
- Domain expertise synthesis

## How does it work?

### High-Level Flow

```
User Question
    ↓
Query Decomposer (LLM analyzes question structure)
    ↓
Break into Sub-Questions
    ↓
Parallel Retrieval (search knowledge base for each sub-question)
    ↓
Retrieval Results (relevant documents for each)
    ↓
Answer Synthesizer (LLM combines results coherently)
    ↓
Final Answer
```

### Key Components

**1. Query Decomposer**
- Analyzes the input question
- Identifies implicit questions within it
- Extracts key concepts and relationships
- Returns a list of focused sub-questions

**2. Vector Retriever**
- Uses semantic embeddings (vector similarity)
- Searches your knowledge base
- Returns top-K most relevant documents for each sub-question
- Preserves document context and metadata

**3. Answer Synthesizer**
- Takes all retrieved information
- Understands the logical flow between pieces
- Generates a single, coherent answer
- Provides source attribution

**4. Knowledge Base**
- Your documents/content
- Converted to vector embeddings
- Stored in a vector database (SQLite with vector tables)
- Can be easily updated/extended

## Features

✅ **Smart question decomposition** - Breaks complex queries into manageable parts  
✅ **Semantic search** - Finds relevant information by meaning, not keywords  
✅ **Multi-step reasoning** - Synthesizes information across multiple documents  
✅ **Source attribution** - Shows where answers came from  
✅ **Lightweight** - No expensive cloud dependencies, runs locally  
✅ **Easy to extend** - Add your own knowledge base in minutes  
✅ **Production-ready** - Includes error handling, logging, configuration  

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd query-optimizer-rag
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the root directory:
```
ANTHROPIC_API_KEY=your_api_key_here
```

Get your API key from [Anthropic Console](https://console.anthropic.com)

### 3. Prepare Your Knowledge Base

Add documents to `data/documents/`:
```
data/documents/
├── document1.txt
├── document2.txt
└── document3.txt
```

### 4. Index Documents

```bash
python src/indexing.py --documents-dir data/documents --output data/vector_db.db
```

This converts your documents into embeddings and stores them in a database.

### 5. Run Queries

```bash
python src/query.py --query "Your complex question here"
```

**Example output:**
```
Query: "Compare machine learning and deep learning. What makes deep learning special?"

Sub-questions identified:
1. What is machine learning?
2. What is deep learning?
3. What are the key differences?
4. Why is deep learning special?

Answer:
Machine learning is a broad field where computers learn patterns from data 
without being explicitly programmed. Deep learning is a subset that uses 
neural networks with multiple layers...

[Full synthesized answer with source citations]
```

## Project Structure

```
query-optimizer-rag/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Example environment variables
├── config/
│   └── settings.py                    # Configuration management
├── data/
│   ├── documents/                     # Your knowledge base documents
│   │   └── example.txt
│   └── vector_db.db                   # Generated vector embeddings
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── decomposer.py              # Query decomposition logic
│   │   ├── retriever.py               # Vector search logic
│   │   └── synthesizer.py             # Answer synthesis logic
│   ├── indexing.py                    # Document indexing pipeline
│   ├── query.py                       # Main query interface
│   └── utils/
│       ├── __init__.py
│       ├── embeddings.py              # Embedding generation
│       ├── database.py                # Vector database operations
│       └── logger.py                  # Logging utilities
├── tests/
│   ├── __init__.py
│   ├── test_decomposer.py
│   ├── test_retriever.py
│   └── test_synthesizer.py
└── examples/
    ├── sample_documents.txt
    └── example_queries.txt
```

## Understanding the Code (No Prior Knowledge Required)

### What is an Embedding?

Think of it like a fingerprint for text:
- Each document is converted into a list of numbers (vector)
- Similar documents have similar number patterns
- The system finds documents by comparing number patterns, not word matching
- This catches meaning better than keyword search

**Example:**
```
"The cat sat on the mat" → [0.12, -0.45, 0.78, 0.23, ...]
"A feline rested on the carpet" → [0.11, -0.46, 0.79, 0.22, ...]
```
These vectors are very similar even though words differ!

### What is Query Decomposition?

Breaking a complex question into simpler parts that are easier to answer:

**Original:** "How have renewable energies evolved since 2010, and what are barriers to adoption?"

**Decomposed:**
1. What renewable energy sources existed in 2010?
2. How have they improved/changed since then?
3. What are current barriers to adoption?

Each sub-question can be answered separately, then combined.

### What is Synthesis?

Combining multiple pieces of information into one coherent answer:

**Retrieved pieces:**
- Doc1: "Wind turbines increased efficiency 40%"
- Doc2: "Solar costs dropped 90% since 2010"
- Doc3: "Grid infrastructure is a major barrier"

**Synthesized answer:**
"Renewable energies have advanced dramatically since 2010. Wind and solar have seen enormous improvements in efficiency and cost-effectiveness. However, adoption still faces barriers in grid modernization..."

## Configuration

Edit `config/settings.py` to customize:

```python
# Model settings
MODEL_NAME = "claude-3-5-sonnet-20241022"  # LLM model
TEMPERATURE = 0.3                          # Lower = more focused

# Retrieval settings
TOP_K = 5                                   # Documents to retrieve per sub-question
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Database
VECTOR_DB_PATH = "data/vector_db.db"
DOCUMENTS_DIR = "data/documents"
```

## Advanced Usage

### Custom Decomposition Strategy

Modify `src/models/decomposer.py` to change how questions are broken down:

```python
# Default: LLM-based decomposition
# Alternative: Pattern-based rules for specific domains
```

### Different Embeddings Model

For better quality, use larger models (slower but more accurate):

```python
# In settings.py
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Better, slower
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"   # Default, fast
```

### Add New Documents

```bash
# Add documents to data/documents/
# Re-index
python src/indexing.py --refresh
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run specific tests:

```bash
pytest tests/test_decomposer.py -v
pytest tests/test_retriever.py -v
```

## Common Issues & Solutions

**Q: "ANTHROPIC_API_KEY not found"**  
A: Create `.env` file with your API key. See Quick Start section.

**Q: "No documents found"**  
A: Ensure documents are in `data/documents/` and run `python src/indexing.py`

**Q: "Very slow queries"**  
A: Reduce `TOP_K` in settings.py, or use smaller embedding model

**Q: "Poor quality answers"**  
A: Add more documents to knowledge base, or refine document preprocessing

## Performance Tips

1. **Faster indexing**: Use smaller documents (< 2000 tokens each)
2. **Better answers**: Include diverse, high-quality documents
3. **Cheaper API calls**: Reduce `TOP_K` from 5 to 3
4. **Local-only**: Replace Anthropic API with open-source models (see docs)

## What You Can Build With This

- **Research assistant**: Index papers, ask complex comparative questions
- **Business analyst**: Query internal documents, reports, policies
- **Educational tool**: Build knowledge base, answer student questions
- **Customer support**: RAG over documentation, FAQs, knowledge base
- **Legal assistant**: Search contracts, find relevant clauses
- **Medical reference**: Query medical literature safely with attribution

## Future Enhancements

- [ ] Multi-turn conversation (memory of previous questions)
- [ ] Hybrid search (keyword + semantic combined)
- [ ] Confidence scoring for answers
- [ ] Real-time document updates
- [ ] Web interface (Gradio/Streamlit)
- [ ] Docker containerization
- [ ] Caching layer for repeated queries

## Contributing

Contributions welcome! Areas to improve:
- Add more test coverage
- Optimize vector search performance
- Implement alternative retrieval strategies
- Add more embedding models

## License

MIT License - see LICENSE file for details

## Resources

- [Anthropic API Docs](https://docs.anthropic.com)
- [RAG Papers & Concepts](https://arxiv.org/)
- [Vector Embeddings Explained](https://www.pinecone.io/learn/)
- [LangChain Documentation](https://python.langchain.com)

## Questions?

If something is unclear:
1. Check the `examples/` folder for sample usage
2. Review inline code comments in `src/models/`
3. Run tests to see expected behavior
4. Check GitHub issues

---

**Built for learning and production use. Star if helpful!** ⭐
