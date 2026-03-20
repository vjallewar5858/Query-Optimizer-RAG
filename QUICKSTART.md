# Quick Start Guide

Get your Query Optimizer RAG system running in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- ~500MB disk space for dependencies

## Step 1: Clone & Install

```bash
# Clone the repository
git clone <your-repo-url>
cd query-optimizer-rag

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate      # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

⏱️ Takes ~2 minutes (first time downloads models)

## Step 2: Set Up API Key

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=sk-ant-xxxxx
```

**Get your API key:**
1. Go to https://console.anthropic.com
2. Create account (free, no credit card needed)
3. Copy your API key
4. Paste into `.env` file

## Step 3: Index Documents

```bash
# Index the sample documents
python src/indexing.py
```

**Output:**
```
✓ Loading embedding model...
✓ Found 1 documents to index
Indexing: sample.txt
  ✓ Created 45 chunks
✓ Indexing complete: 45 total chunks in database
```

## Step 4: Run Your First Query

```bash
# Simple query
python src/query.py --query "What is photosynthesis?"

# Complex query with decomposition
python src/query.py --query "Compare photosynthesis and chemosynthesis. Why is photosynthesis dominant?"

# Verbose mode (shows all steps)
python src/query.py --query "Your question here" --verbose
```

**Sample Output:**
```
======================================================================
QUERY OPTIMIZER RESULT
======================================================================

Original Question:
What is photosynthesis?

Sub-questions identified:
  1. What is photosynthesis?
  2. What are the key processes involved in photosynthesis?
  3. Why is photosynthesis important for life?

----------------------------------------------------------------------
SYNTHESIZED ANSWER:
----------------------------------------------------------------------

Photosynthesis is a biological process that converts light energy...
[Full comprehensive answer with citations]

----------------------------------------------------------------------
Retrieved 12 relevant documents
======================================================================
```

## Step 5: Add Your Own Documents

```bash
# 1. Add text files to data/documents/
cp your_document.txt data/documents/

# 2. Re-index
python src/indexing.py

# 3. Query
python src/query.py --query "Your question about your documents"
```

## Next Steps

### Explore the System
```bash
# Run tests
pytest tests/ -v

# Check configuration
cat config/settings.py

# View example queries
cat examples/example_queries.txt
```

### Customize
Edit `config/settings.py` to change:
- Model (default: claude-3-5-sonnet)
- Temperature (higher = more creative)
- Number of documents retrieved (TOP_K)
- Embedding model (default: all-MiniLM-L6-v2)

### Integrate Into Your Project
```python
from src.query import QueryOptimizer

# In your Python code
optimizer = QueryOptimizer()
result = optimizer.query("Your question")
print(result['answer'])
optimizer.close()
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
```bash
# Check your .env file exists and has the key
cat .env
# Should show: ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### "No documents in database"
```bash
# Re-index your documents
python src/indexing.py --refresh
```

### Slow queries?
```bash
# Edit config/settings.py, reduce TOP_K from 5 to 3
# Fewer documents = faster retrieval
```

### Poor quality answers?
```bash
# Add more documents to data/documents/
# Larger, more diverse knowledge base = better answers
```

## Understanding What's Happening

### When you run a query:

1. **Decompose** (5-10 seconds)
   - LLM analyzes your question
   - Breaks into sub-questions
   - Example: "Compare X and Y" → "What is X?", "What is Y?", "How different?"

2. **Retrieve** (2-5 seconds)
   - System searches for relevant documents
   - Uses semantic similarity (meaning-based, not keyword)
   - Finds best matches for each sub-question

3. **Synthesize** (10-20 seconds)
   - LLM reads all relevant documents
   - Understands connections between them
   - Generates coherent answer with citations

**Total time: 20-40 seconds (depending on document count)**

## Pro Tips

✅ **Better answers:**
- Add high-quality, diverse documents
- Use specific, detailed questions
- Break very complex questions into parts

✅ **Faster responses:**
- Reduce `TOP_K` in settings
- Use smaller embedding model
- Keep documents under 5000 characters each

✅ **For production:**
- Use a real vector database (Pinecone, Weaviate)
- Add caching for repeated queries
- Implement rate limiting
- Add authentication

## Common Questions

**Q: Can I use my own documents?**
A: Yes! Add `.txt` files to `data/documents/` then run indexing.

**Q: Can I use different LLM models?**
A: Yes. Edit `config/settings.py` and change `MODEL_NAME`.

**Q: Does this work offline?**
A: No, it needs API calls to Anthropic. For local-only, use open-source LLMs (see advanced docs).

**Q: How many documents can it handle?**
A: Tested up to 1000 documents. For more, use a real vector database.

**Q: Can I share my answers?**
A: Yes! Results are saved to `last_query_result.txt`. Just share that file.

## Next: Read the Full README

For advanced configuration, integration patterns, and architecture details, see `README.md`

Happy querying! 🚀
