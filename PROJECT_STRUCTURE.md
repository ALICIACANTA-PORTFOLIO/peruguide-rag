# 📊 PeruGuide AI - Project Structure Visualization

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PeruGuide AI System                            │
│                     Production-Ready RAG Application                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
        ┌──────────────────┐ ┌──────────────┐ ┌─────────────────┐
        │  FEATURE PIPELINE│ │   TRAINING   │ │INFERENCE PIPELINE│
        │   (Data Prep)    │ │  (Optional)  │ │   (RAG Chain)    │
        └──────────────────┘ └──────────────┘ └─────────────────┘
```

---

## 📁 Directory Structure

```
peruguide-rag/
│
├─ 📂 analisis/                    # 🔍 Research & Analysis (Archive)
│  │                               # Todo el análisis previo almacenado aquí
│  ├─ materials_analysis_comprehensive.json
│  ├─ PLANTEAMIENTO_DEFINITIVO_CON_ANALISIS.md
│  ├─ deep_analysis_books.py
│  └─ [otros archivos de análisis]
│
├─ 📂 src/                         # 💻 Core Source Code
│  ├─ config.py                    # ⚙️ Pydantic settings
│  │
│  ├─ 📂 data_pipeline/            # 🔄 FEATURE PIPELINE
│  │  ├─ __init__.py
│  │  ├─ 📂 loaders/
│  │  │  ├─ __init__.py
│  │  │  ├─ pdf_loader.py         # 📄 PDF extraction
│  │  │  └─ directory_loader.py   # 📚 Batch loading
│  │  ├─ 📂 processors/
│  │  │  ├─ __init__.py
│  │  │  ├─ cleaner.py            # 🧹 Text cleaning
│  │  │  └─ metadata_extractor.py # 🏷️ Metadata extraction
│  │  └─ 📂 chunkers/
│  │     ├─ __init__.py
│  │     └─ recursive_splitter.py # ✂️ Text chunking
│  │
│  ├─ 📂 embedding_pipeline/       # 🧠 Embeddings
│  │  ├─ __init__.py
│  │  ├─ 📂 models/
│  │  │  ├─ __init__.py
│  │  │  └─ sentence_transformer.py # 🔢 Vector embeddings
│  │  └─ batch_processor.py        # ⚡ Batch processing
│  │
│  ├─ 📂 vector_store/             # 💾 Vector Database
│  │  ├─ __init__.py
│  │  ├─ abstract_store.py        # 🎨 Abstract interface
│  │  ├─ faiss_store.py           # 🚀 FAISS (dev)
│  │  └─ chroma_store.py          # 🗄️ Chroma (prod)
│  │
│  ├─ 📂 retrieval_pipeline/       # 🔍 INFERENCE - Retrieval
│  │  ├─ __init__.py
│  │  ├─ 📂 retrievers/
│  │  │  ├─ __init__.py
│  │  │  ├─ dense_retriever.py    # 🎯 Vector similarity
│  │  │  └─ hybrid_retriever.py   # 🔀 Hybrid search
│  │  └─ 📂 rerankers/
│  │     ├─ __init__.py
│  │     └─ cross_encoder.py      # 📊 Reranking
│  │
│  ├─ 📂 inference_pipeline/       # 🤖 INFERENCE - Generation
│  │  ├─ __init__.py
│  │  ├─ 📂 llm/
│  │  │  ├─ __init__.py
│  │  │  ├─ mistral_client.py     # 🎭 LLM client
│  │  │  └─ prompt_templates.py   # 📝 Prompts
│  │  ├─ 📂 chains/
│  │  │  ├─ __init__.py
│  │  │  └─ rag_chain.py          # 🔗 RAG orchestration
│  │  └─ 📂 postprocessing/
│  │     ├─ __init__.py
│  │     ├─ citation_formatter.py # 📚 Citations
│  │     └─ confidence_scorer.py  # 📈 Confidence
│  │
│  ├─ 📂 evaluation/               # ✅ Metrics & Evaluation
│  │  ├─ __init__.py
│  │  ├─ ragas_evaluator.py       # 📊 RAGAS metrics
│  │  ├─ test_dataset.json        # 📋 Test Q&A pairs
│  │  └─ metrics_logger.py        # 📈 Logging
│  │
│  └─ 📂 utils/                    # 🛠️ Utilities
│     ├─ __init__.py
│     ├─ logger.py                # 📝 Structured logging
│     └─ monitoring.py            # 📊 Prometheus metrics
│
├─ 📂 api/                         # 🌐 REST API (FastAPI)
│  ├─ __init__.py
│  ├─ main.py                      # 🚀 FastAPI app
│  ├─ 📂 routers/
│  │  ├─ __init__.py
│  │  ├─ query.py                 # 💬 /query endpoint
│  │  ├─ feedback.py              # 💭 /feedback endpoint
│  │  └─ admin.py                 # ⚙️ /health, /metrics
│  ├─ 📂 models/
│  │  ├─ __init__.py
│  │  └─ schemas.py               # 📦 Pydantic models
│  └─ 📂 middleware/
│     ├─ __init__.py
│     ├─ auth.py                  # 🔐 Authentication
│     └─ rate_limit.py            # 🚦 Rate limiting
│
├─ 📂 app/                         # 🎨 User Interface (Streamlit)
│  ├─ Home.py                      # 🏠 Main app
│  └─ 📂 pages/
│     ├─ Chat.py                  # 💬 Chat interface
│     ├─ Sources.py               # 📚 Source browser
│     └─ Analytics.py             # 📊 Analytics
│
├─ 📂 tests/                       # 🧪 Test Suite
│  ├─ __init__.py
│  ├─ conftest.py                 # 🔧 pytest fixtures
│  ├─ 📂 unit/                    # Unit tests
│  │  ├─ test_chunking.py
│  │  ├─ test_retrieval.py
│  │  ├─ test_generation.py
│  │  └─ test_utils.py
│  └─ 📂 integration/             # Integration tests
│     ├─ test_pipeline.py
│     └─ test_api.py
│
├─ 📂 .github/workflows/           # 🔄 CI/CD
│  ├─ ci.yml                      # ✅ Continuous Integration
│  └─ cd.yml                      # 🚀 Continuous Deployment
│
├─ 📂 docker/                      # 🐳 Containerization
│  ├─ Dockerfile                  # 📦 Multi-stage build
│  ├─ docker-compose.yml          # 🎼 Orchestration
│  └─ .dockerignore
│
├─ 📂 docs/                        # 📚 Documentation (MkDocs)
│  ├─ index.md                    # Home
│  ├─ architecture/               # Architecture docs
│  ├─ api/                        # API reference
│  ├─ development/                # Dev guides
│  └─ deployment/                 # Deployment guides
│
├─ 📂 notebooks/                   # 📓 Jupyter Notebooks
│  ├─ 📂 legacy/                  # Original academic work
│  │  ├─ MNA_NLP_actividad_chatbot_LLM_RAG (3).ipynb
│  │  └─ NLP_LLM_con_RAG_y_VectorDatabase_FAISS_Chrome_Wikipedia.ipynb
│  └─ 📂 experiments/             # Experimental notebooks
│     ├─ 01_data_exploration.ipynb
│     ├─ 02_embedding_comparison.ipynb
│     ├─ 03_prompt_tuning.ipynb
│     └─ 04_evaluation_analysis.ipynb
│
├─ 📂 data/                        # 💾 Data Directory
│  ├─ 📂 raw/                     # Raw PDF files
│  ├─ 📂 processed/               # Processed chunks
│  └─ 📂 vector_stores/           # Vector indices
│
├─ 📂 Books/                       # 📚 Reference Materials
│  ├─ 📂 llm/                     # LLM engineering books
│  └─ 📂 story-telling/           # Storytelling books
│
├─ 📂 Complementarios Peru/        # 🇵🇪 Official Peru PDFs
│
├─ 📄 .env.example                 # Environment template
├─ 📄 .gitignore                   # Git ignore patterns
├─ 📄 .pre-commit-config.yaml      # Pre-commit hooks
├─ 📄 pyproject.toml               # Project metadata
├─ 📄 requirements.txt             # Core dependencies
├─ 📄 requirements-dev.txt         # Dev dependencies
├─ 📄 pytest.ini                   # pytest config
├─ 📄 mkdocs.yml                   # MkDocs config
├─ 📄 README.md                    # ⭐ Main README
├─ 📄 DEVELOPMENT_ROLES.md         # 👥 Role definitions
└─ 📄 LICENSE                      # MIT License
```

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA FLOW                                    │
└─────────────────────────────────────────────────────────────────────┘

1️⃣ INGESTION
   📄 PDFs (30+) → pdf_loader.py → Extracted Text
                                         │
2️⃣ PROCESSING                            ▼
   Extracted Text → cleaner.py → Cleaned Text
                                         │
3️⃣ CHUNKING                              ▼
   Cleaned Text → recursive_splitter.py → Chunks (512 chars)
                                         │
4️⃣ EMBEDDING                             ▼
   Chunks → sentence_transformer.py → Embeddings (768-dim)
                                         │
5️⃣ INDEXING                              ▼
   Embeddings → chroma_store.py → Vector Store
                                         │
6️⃣ QUERY                                 ▼
   User Query → dense_retriever.py → Top-5 Chunks
                                         │
7️⃣ GENERATION                            ▼
   Top-5 + Query → rag_chain.py → LLM Response
                                         │
8️⃣ POST-PROCESSING                       ▼
   LLM Response → citation_formatter.py → Final Answer
                                         │
9️⃣ DISPLAY                               ▼
   Final Answer → Streamlit UI → 👤 User
```

---

## 👥 Roles & Ownership

```
┌───────────────────────────────────────────────────────────────┐
│  Role               │  Primary Directory         │  Key Tasks │
├───────────────────────────────────────────────────────────────┤
│  Data Engineer      │  src/data_pipeline/        │  Ingest    │
│                     │                            │  Process   │
│                     │                            │  Chunk     │
├───────────────────────────────────────────────────────────────┤
│  ML Engineer        │  src/embedding_pipeline/   │  Embed     │
│                     │  src/retrieval_pipeline/   │  Retrieve  │
│                     │  src/inference_pipeline/   │  Generate  │
│                     │  src/evaluation/           │  Evaluate  │
├───────────────────────────────────────────────────────────────┤
│  Backend Engineer   │  api/                      │  API       │
│                     │  src/vector_store/         │  DB        │
├───────────────────────────────────────────────────────────────┤
│  Frontend Engineer  │  app/                      │  UI        │
├───────────────────────────────────────────────────────────────┤
│  DevOps Engineer    │  .github/workflows/        │  CI/CD     │
│                     │  docker/                   │  Deploy    │
├───────────────────────────────────────────────────────────────┤
│  QA Engineer        │  tests/                    │  Test      │
├───────────────────────────────────────────────────────────────┤
│  Technical Writer   │  docs/                     │  Document  │
│                     │  README.md                 │            │
└───────────────────────────────────────────────────────────────┘
```

---

## 📊 Implementation Phases

```
Phase 1: Week 1 - FOUNDATION
├─ Data Pipeline      [Data Engineer]
├─ Embedding Pipeline [ML Engineer]
└─ API Skeleton       [Backend Engineer]

Phase 2: Week 2 - INTEGRATION
├─ RAG Chain          [ML Engineer]
├─ API Endpoints      [Backend Engineer]
└─ UI Basic           [Frontend Engineer]

Phase 3: Week 3 - TESTING
├─ Test Suite         [QA Engineer]
├─ RAGAS Evaluation   [ML Engineer]
└─ CI/CD Setup        [DevOps Engineer]

Phase 4: Week 4 - DEPLOYMENT
├─ Docker + Deploy    [DevOps Engineer]
├─ Documentation      [Technical Writer]
└─ Final Testing      [All Roles]
```

---

## 🎯 Key Metrics Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                    SUCCESS METRICS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Technical Metrics                                       │
│  ├─ Faithfulness (RAGAS)         Target: >0.85  Status: ⏳│
│  ├─ Answer Relevancy (RAGAS)     Target: >0.80  Status: ⏳│
│  ├─ Context Precision (RAGAS)    Target: >0.75  Status: ⏳│
│  ├─ Latency (p95)                Target: <3s    Status: ⏳│
│  └─ Test Coverage                Target: >75%   Status: ⏳│
│                                                             │
│  🏗️ Engineering Metrics                                    │
│  ├─ Code Quality                 Target: A      Status: ⏳│
│  ├─ Documentation                Target: 100%   Status: 🟡│
│  ├─ CI/CD Pipeline               Target: Pass   Status: ⏳│
│  └─ Deployment                   Target: Live   Status: ⏳│
│                                                             │
│  👥 Portfolio Metrics                                       │
│  ├─ GitHub Stars                 Target: >50    Status: ⏳│
│  ├─ LinkedIn Views               Target: >500   Status: ⏳│
│  └─ Demo Uptime                  Target: >99%   Status: ⏳│
│                                                             │
└─────────────────────────────────────────────────────────────┘

Legend: ✅ Done | 🟡 In Progress | ⏳ Not Started | ❌ Blocked
```

---

## 🚀 Quick Start Commands

```bash
# Setup
git clone https://github.com/yourusername/peruguide-rag.git
cd peruguide-rag
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Development
pytest tests/ -v --cov=src
ruff check src/ api/ app/
black src/ api/ app/

# Run Application
uvicorn api.main:app --reload          # API
streamlit run app/Home.py              # UI

# Docker
docker-compose up --build
```

---

## 📞 Support

- 📖 Docs: `docs/`
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📧 Email: your.email@example.com

---

**Built with ❤️ following best practices from 9 books (2,959 pages analyzed)**
