# Architecture Guide

Detailed explanation of how Query Optimizer RAG works, perfect for understanding the system design.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Question                           │
│         "Compare X and Y. Why is X more common?"           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Query Decomposer (LLM)                         │
│  Breaks complex question into answerable sub-questions     │
│                                                              │
│  Output: ["What is X?", "What is Y?", "Why X dominant?"]  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Document Retriever (Semantic Search)               │
│  Finds relevant documents for each sub-question            │
│  Uses embeddings (vector similarity)                       │
│                                                              │
│  For each sub-question:                                    │
│    1. Convert to embedding (vector)                        │
│    2. Compare to document embeddings                       │
│    3. Return top-K most similar documents                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           Answer Synthesizer (LLM)                          │
│  Combines all retrieved documents into one answer          │
│                                                              │
│  Input:                                                    │
│    - Original question                                    │
│    - Sub-questions                                        │
│    - All relevant documents                               │
│                                                              │
│  Output: Comprehensive answer with citations              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Final Answer                              │
│         With sources cited and step-by-step reasoning      │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Query Decomposer

**Purpose:** Break complex questions into simpler parts

**How it works:**
```
Input: "How do neural networks learn, and why do they sometimes fail?"

LLM reasoning:
  - This question has 2 main parts
  - First part: mechanism of learning
  - Second part: failure modes
  
Output: [
  "What is a neural network?",
  "How do neural networks learn from data?",
  "What causes neural networks to fail?",
  "What are overfitting and underfitting?"
]
```

**Why it matters:**
- Single complex question has ambiguous meaning
- Multiple focused questions are easier to search for
- Results are more targeted and relevant

**Technology:**
- Uses Claude LLM to analyze question structure
- Generates contextually appropriate sub-questions
- Typically produces 2-5 sub-questions

---

### 2. Document Retriever

**Purpose:** Find relevant documents using semantic similarity

**Key concept: Embeddings**

An embedding is a vector (list of numbers) representing meaning:

```
"The cat sat on the mat"  →  [0.12, -0.45, 0.78, 0.23, ...]
"A feline rested on carpet"  →  [0.11, -0.46, 0.79, 0.22, ...]
                                  ↑     ↑      ↑    ↑
                           Similar numbers = similar meaning!
```

**The search process:**

```
1. Convert query to embedding:
   "What is photosynthesis?" → Query Vector (384 dimensions)

2. Compare to all documents:
   - Document 1 embedding → Similarity: 0.95 ✓ (VERY SIMILAR)
   - Document 2 embedding → Similarity: 0.42   (somewhat related)
   - Document 3 embedding → Similarity: 0.15   (not relevant)

3. Return top-K (say K=5):
   Return the 5 most similar documents

4. Use them for answer generation
```

**Similarity Calculation: Cosine Similarity**

```
Cosine similarity measures the angle between vectors:

    • 1.0 = same direction (identical meaning)
    • 0.5 = moderate angle (related meaning)
    • 0.0 = perpendicular (unrelated)
   -1.0 = opposite (contradictory)

Formula: similarity = (vec1 · vec2) / (|vec1| × |vec2|)
         where · is dot product and |·| is magnitude
```

**Embedding Models**

The project uses `sentence-transformers/all-MiniLM-L6-v2`:
- Fast (indexes 1000 documents in seconds)
- 384-dimensional embeddings
- Good for general text
- Alternative: `all-mpnet-base-v2` (better but slower)

**Why embeddings beat keyword search:**

```
Query: "How do birds fly?"

Keyword search finds:
- "The birds flew away" ✓
- "Flight training for birds" ✓
- "My bird is flying away" ✓
- "I'm feeling fly today" ✗ (wrong "fly")

Embedding search finds:
- Documents about bird biology ✓
- Documents about aerodynamics ✓
- Documents about bird physiology ✓
- (Ignores unrelated "fly" uses)
```

---

### 3. Answer Synthesizer

**Purpose:** Create coherent answer from multiple documents

**Process:**

```
Step 1: Gather context
- Original question: "Compare X and Y"
- Sub-questions: ["What is X?", "What is Y?", "How do they differ?"]
- Retrieved documents: 15 relevant documents about X and Y

Step 2: Format context for LLM
```
For sub-question 1 (What is X?):
- Document 1: "X is defined as..." [similarity: 0.95]
- Document 2: "X is characterized by..." [similarity: 0.88]
- ...

For sub-question 2 (What is Y?):
- Document 3: "Y differs from X in..." [similarity: 0.92]
- ...
```

Step 3: LLM synthesis
LLM reads all context and:
- Understands question intent
- Identifies key information
- Finds relationships between documents
- Fills in missing connections
- Structures answer logically
- Adds citations

Step 4: Output comprehensive answer
"X is [definition from docs]. In contrast, Y is [definition]...
This difference arises from [synthesis from multiple docs]..."
```

**Citation System:**

When synthesizer generates answers, it includes source attribution:

```
"Photosynthesis requires light, water, and CO2.
[Source: bio_textbook.txt] The light energy is
captured by chlorophyll molecules in leaves.
[Source: plant_physiology.txt]"
```

This:
- Increases credibility (readers can verify)
- Shows where information came from
- Helps detect if sources are conflicting
- Supports further research

---

## Data Flow

### Indexing Phase (One-time setup)

```
Raw documents (text files)
    ↓
Document Chunking
  (split into ~1000 char pieces for better context)
    ↓
Embedding Generation
  (convert text to vectors using embedding model)
    ↓
Vector Database Storage
  (SQLite with vectors indexed for fast search)
    ↓
Ready for queries!
```

### Query Phase (Happens for every question)

```
User Question
    ↓
Decomposer LLM Call (~5-10 sec)
    ├─ Input: User question
    ├─ Output: 3-5 sub-questions
    ↓
For each sub-question:
    ├─ Generate embedding (~1 sec)
    ├─ Vector search in database (~1 sec)
    └─ Retrieve top-5 documents
    ↓
Synthesizer LLM Call (~10-20 sec)
    ├─ Input: All retrieved documents + original question
    ├─ Output: Comprehensive answer with citations
    ↓
Final Answer
    └─ Saved to last_query_result.txt
```

---

## Key Algorithms

### 1. Cosine Similarity

```python
def cosine_similarity(vec1, vec2):
    """
    Measures how similar two vectors are.
    
    Returns: -1.0 to 1.0
      1.0  = identical
      0.0  = unrelated
     -1.0  = opposite
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sqrt(sum(x**2 for x in vec1))
    magnitude2 = sqrt(sum(x**2 for x in vec2))
    
    return dot_product / (magnitude1 * magnitude2)
```

### 2. Document Chunking

```python
def chunk_document(text, chunk_size=1000, overlap=200):
    """
    Split long documents into overlapping pieces.
    
    Why overlap?
    - Preserves context at chunk boundaries
    - Improves semantic coherence
    - Slightly slower indexing but better answers
    
    Example:
    Original: "Alice and Bob were friends. They met in..."
                              chunk1↓              ↓chunk2
    Chunk1: "Alice and Bob were friends. They met in school..."
    Chunk2: "They met in school. Bob loved playing..."
                           ↑ overlap
    """
```

### 3. Query Decomposition Logic

```
Algorithm: Recursive Question Analysis

1. Identify if question has multiple parts:
   - Conjunctions: "and", "or"
   - Comparison words: "compare", "versus", "difference"
   - Causal words: "why", "how", "because"
   - Temporal words: "before", "after", "then"

2. Extract implicit questions
3. Ensure each is specific and answerable
4. Order by dependency (simpler questions first)
```

---

## Why This Architecture?

### Advantages

✅ **Accurate**: Semantic search finds meaning, not keywords
✅ **Comprehensive**: Decomposition ensures all aspects covered
✅ **Explainable**: Citations show where answers come from
✅ **Scalable**: Can work with thousands of documents
✅ **Flexible**: Works with any text-based knowledge base
✅ **Fast**: Parallel retrieval for multiple sub-questions

### Limitations & Trade-offs

❌ **API Dependency**: Requires Anthropic API calls (not free)
❌ **Latency**: 20-40 seconds per query (multiple LLM calls)
❌ **Vector DB Size**: Embeddings need storage (384 dims × docs)
❌ **Context Window**: Very long documents lose some context
❌ **Hallucination**: LLM might invent facts if docs are unclear

---

## Comparison to Alternatives

### Simple RAG (Keyword Search)
```
Your question
    ↓
Keyword matching in documents
    ↓
Return results
```
- ✓ Fast
- ✗ Poor quality (misses semantic matches)
- ✗ Can't handle complex questions

### Query Optimizer RAG (This Project)
```
Your question
    ↓
Decompose into sub-questions
    ↓
Semantic search for each
    ↓
Synthesize comprehensive answer
```
- ✓ High quality answers
- ✓ Handles complex questions
- ✗ Slower (multiple LLM calls)
- ✗ More expensive

### Agentic RAG (Advanced)
```
Your question
    ↓
Agent decides what to do:
  - Decompose further?
  - Search for more info?
  - Refine previous answer?
    ↓
Iterative refinement
    ↓
Best possible answer
```
- ✓ Best quality
- ✗ Much slower
- ✗ Most expensive

---

## Performance Characteristics

### Time Complexity

```
Indexing (one-time):
- O(n × m) where n = documents, m = embedding time
- Typical: 1000 docs = 10-30 seconds

Query Processing (per question):
- Decomposition: O(1) constant LLM call
- Retrieval: O(n × d) where d = embedding dimensions
  (but with fast vector search: effectively O(log n))
- Synthesis: O(1) constant LLM call
- Total: ~20-40 seconds per query
```

### Space Complexity

```
Knowledge Base:
- Text storage: ~1 byte per character
- Embeddings: 384 floats × 4 bytes = 1536 bytes per document
- Typical: 1000 documents = 2-5 MB database

For 100,000 documents:
- ~2 GB storage (very manageable)
```

### Cost Analysis

```
Per query cost (using Claude 3.5 Sonnet):
- Decomposition: ~1000 tokens input = ~$0.0003
- Synthesis: ~3000 tokens input = ~$0.0009
- Average answer cost: $0.0012 per query (~0.1 cents)
```

---

## Extension Points

### You can easily modify:

1. **Embedding Model**
   - Swap to better model for higher quality
   - Language-specific models for non-English text

2. **Vector Database**
   - Replace SQLite with Pinecone, Weaviate, Milvus
   - Enable horizontal scaling

3. **Decomposition Strategy**
   - Add domain-specific rules
   - Fine-tune for your use case

4. **Retrieval Strategy**
   - Add keyword filtering before semantic search
   - Implement hybrid search (keyword + semantic)

5. **Answer Synthesis**
   - Add post-processing for formatting
   - Implement confidence scoring
   - Add fact-checking layer

---

## Next: See the Code

Review these files in order:
1. `src/models/decomposer.py` - Question analysis
2. `src/models/retriever.py` - Semantic search
3. `src/models/synthesizer.py` - Answer generation
4. `src/query.py` - Orchestration

Each file has detailed comments explaining every step!
