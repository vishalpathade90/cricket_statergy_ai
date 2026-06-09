# 🧠 DocMind AI — PDF Q&A Chatbot

> **RAG-powered document intelligence built with LangChain, ChromaDB & GPT-4**

A production-grade PDF Q&A system demonstrating the core architecture behind modern Generative AI applications — semantic search, vector embeddings, and retrieval-augmented generation.

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────────────┐
                    │           DocMind AI Pipeline            │
                    └─────────────────────────────────────────┘

  PDF Upload          Text Extraction        Chunking
  ──────────    →     ──────────────    →    ─────────
  pdfplumber          Raw text +             RecursiveCharacter
  (page-aware)        page metadata          TextSplitter

  Embedding           Vector Storage         Retrieval
  ─────────    →      ──────────────    →    ─────────
  OpenAI              ChromaDB               Top-K Semantic
  text-embed-3-small  (1536-d vectors)       Cosine Similarity

  Generation
  ──────────
  GPT-4o-mini
  (Context-grounded,
  citation-aware)
```

### Core Concepts Demonstrated
| Concept | Implementation | Why It Matters |
|---------|----------------|----------------|
| **Chunking Strategy** | `RecursiveCharacterTextSplitter` with overlap | Preserves semantic coherence; prevents information loss at boundaries |
| **Vector Embeddings** | OpenAI `text-embedding-3-small` (1536-d) | Converts text to dense vectors for semantic similarity search |
| **Vector Database** | ChromaDB (open-source, local) | Fast approximate nearest-neighbor search at scale |
| **RAG** | LangChain retrieval chain | Grounds LLM in document facts; eliminates hallucination |
| **Prompt Engineering** | System prompt with injected context | Controls LLM behavior and ensures citation-aware responses |
| **Multi-turn Memory** | Rolling conversation history | Enables follow-up questions with context retention |

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/yourusername/docmind-ai
cd docmind-ai
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run
```bash
streamlit run app.py
```
Open http://localhost:8501

---

## 📁 Project Structure

```
docmind-ai/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── assets/
│   └── style.css           # Custom dark UI theme
└── src/
    ├── __init__.py
    ├── pdf_processor.py    # PDF parsing + chunking
    ├── vector_store.py     # ChromaDB embedding storage
    ├── llm_chain.py        # RAG pipeline + prompt design
    └── utils.py            # Formatting helpers
```

---

## ⚙️ Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chunk_size` | 500 | Target characters per chunk. Larger = more context, less precision |
| `chunk_overlap` | 50 | Characters shared between adjacent chunks |
| `top_k` | 4 | Chunks retrieved per query |
| `model` | gpt-4o-mini | LLM for generation. gpt-4o for best quality |
| `temperature` | 0.1 | LLM randomness. Low = factual, consistent |

---

## 🧪 How RAG Works (Step-by-Step)

1. **Ingestion Phase** (one-time per document)
   - Extract text from PDF pages with `pdfplumber`
   - Split into overlapping chunks (default: 500 chars, 50 overlap)
   - Embed each chunk with OpenAI's `text-embedding-3-small`
   - Store 1536-dimensional vectors in ChromaDB

2. **Query Phase** (per user question)
   - Embed the user's question into the same vector space
   - Find top-4 most similar chunks via cosine similarity
   - Inject retrieved chunks into the LLM system prompt
   - GPT-4o-mini generates a grounded, citation-aware answer

---

## 💡 Resume Talking Points

- **"I built a production RAG pipeline"** — end-to-end: PDF parsing → chunking → embedding → vector retrieval → LLM generation
- **"I understand chunking tradeoffs"** — larger chunks = more context but noisier retrieval; overlap prevents boundary information loss
- **"I designed the prompt architecture"** — system prompt constrains LLM to document context, preventing hallucination
- **"I used ChromaDB for vector storage"** — open-source alternative to Pinecone; understands local vs cloud tradeoffs
- **"Multi-turn conversation with memory"** — rolling history window prevents token bloat while preserving context

---

## 🔧 Extending This Project

- **Add Hugging Face local embeddings** → replace `OpenAIEmbeddings` with `HuggingFaceEmbeddings`
- **Multi-PDF support** → add a collection manager per document
- **Streaming responses** → use `ChatOpenAI(streaming=True)` with `st.write_stream()`
- **Reranking** → add a Cohere or cross-encoder reranker after retrieval
- **Evaluation** → integrate RAGAS framework to measure faithfulness and answer relevance

---

## 📦 Tech Stack

| Tool | Version | Role |
|------|---------|------|
| Streamlit | ≥1.32 | Web UI framework |
| LangChain | ≥0.2 | RAG orchestration |
| ChromaDB | ≥0.5 | Vector database |
| OpenAI | ≥1.30 | Embeddings + LLM |
| pdfplumber | ≥0.11 | PDF text extraction |

---

## 📄 License
MIT License — free to use, modify, and include in your portfolio.
