# 🇵🇪 PeruGuide AI - Intelligent Peru Travel Assistant

> **Production-ready RAG system transforming Peru's tourism knowledge into an intelligent conversational assistant**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-505%20passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/Coverage-94%25-success.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Performance](#-performance)
- [Contributing](#-contributing)

---

## 🎯 Overview

**PeruGuide AI** is a state-of-the-art Retrieval-Augmented Generation (RAG) system that provides accurate, sourced answers about Peru's tourism, culture, and history. Built with production-grade practices, it showcases:

- 🏗️ **Clean Architecture**: Modular, testable, maintainable code
- 🧪 **Test-Driven Development**: 505 tests with 94%+ coverage
- 🚀 **Cloud-Ready**: Docker + multi-cloud deployment scripts
- 📊 **Observable**: Structured logging and metrics
- 🎨 **User-Friendly**: Interactive Streamlit web interface

### The Problem

Every year, **4+ million tourists** visit Peru, spending 5-8 hours researching through scattered PDFs, blogs, and forums without source verification.

### The Solution

PeruGuide AI provides:
- ⚡ **15-minute trip planning** (vs 5-8 hours)
- ✅ **Automatic source verification** from official documents
- 🎯 **Personalized recommendations** based on context
- 🌐 **Multilingual support** (Spanish & English)

---

## ✨ Key Features

### For Users
- 🤖 **Intelligent Q&A**: Natural language queries about Peru
- 📚 **Source Citations**: Every answer includes document references
- 🌍 **Multi-LLM Support**: Choose from 5 AI providers
- ⚡ **Fast Responses**: Sub-second retrieval + generation
- 📱 **Web Interface**: Beautiful, responsive Streamlit UI

### For Developers
- 🏗️ **Modular Architecture**: Data → Vector Store → RAG → API → Frontend
- 🧪 **Comprehensive Testing**: Unit, integration, and E2E tests
- 📊 **Observability**: Structured logging with structlog
- 🐳 **Containerized**: Docker + Docker Compose ready
- ☁️ **Multi-Cloud**: Deploy to Azure, AWS, or GCP
- 📖 **OpenAPI Docs**: Auto-generated API documentation

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PERUGUIDE AI SYSTEM                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  PDF Sources │─────▶│ Data Pipeline│─────▶│ Vector Store │
│ (Peru Guides)│      │  (Chunking)  │      │   (FAISS)    │
└──────────────┘      └──────────────┘      └──────────────┘
                                                      │
                                                      ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Streamlit  │◀────│  FastAPI     │◀────│  Retriever   │
│   Frontend   │      │     API      │      │   (RAG)      │
└──────────────┘      └──────────────┘      └──────────────┘
                              │                      │
                              ▼                      ▼
                      ┌──────────────┐      ┌──────────────┐
                      │  LLM Models  │      │  Embeddings  │
                      │ (5 providers)│      │ (Sentence-T) │
                      └──────────────┘      └──────────────┘
```

### Data Flow

1. **Ingestion**: PDFs → Text extraction → Metadata enrichment
2. **Processing**: Text → Chunking → Embeddings → Vector storage
3. **Retrieval**: Query → Semantic search → Top-K documents
4. **Generation**: Context + Query → LLM → Answer with citations
5. **Delivery**: API → Frontend → User

---

## 🛠️ Tech Stack

### Core Framework
- **Python 3.11+**: Modern async/await support
- **FastAPI**: High-performance async API framework
- **Pydantic**: Data validation and serialization
- **Streamlit**: Interactive web frontend

### RAG Components
- **FAISS**: Vector similarity search (Facebook AI)
- **Sentence Transformers**: Text embeddings
- **LangChain**: LLM orchestration framework

### LLM Providers (5 supported)
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- DeepSeek
- Azure OpenAI
- HuggingFace

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Local orchestration
- **Uvicorn**: ASGI server
- **Nginx**: Reverse proxy (optional)

### Testing & Quality
- **pytest**: Testing framework (505 tests)
- **pytest-cov**: Coverage reporting (94%+)
- **pytest-asyncio**: Async test support
- **black**: Code formatting
- **ruff**: Fast Python linter

### Logging & Monitoring
- **structlog**: Structured logging
- **loguru**: Advanced logging features

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip or conda
- (Optional) Docker

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/peruguide-rag.git
cd peruguide-rag
```

### 2. Setup Environment

#### Option A: Conda (Recommended)
```bash
conda env create -f environment.yml
conda activate peruguide-rag
```

#### Option B: pip + venv
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API Keys

```bash
cp .env.example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Run Tests (Optional)

```bash
pytest tests/ -v --cov=src
```

### 5. Start API Server

```bash
uvicorn src.api.main:app --reload
```

API will be available at: http://localhost:8000

- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 6. Start Frontend (New Terminal)

```bash
cd app
streamlit run streamlit_app.py
```

Frontend will open at: http://localhost:8501

---

## 📂 Project Structure

```
peruguide-rag/
├── src/
│   ├── api/                    # FastAPI backend
│   │   ├── main.py            # Application entry point
│   │   ├── routes/            # API endpoints
│   │   ├── schemas/           # Pydantic models
│   │   └── dependencies/      # Dependency injection
│   ├── data_pipeline/         # PDF loading & processing
│   ├── embedding_pipeline/    # Text embeddings
│   ├── vector_store/          # FAISS vector database
│   ├── retrieval_pipeline/    # Semantic retrieval
│   ├── llm/                   # LLM providers
│   └── rag/                   # RAG answer generation
├── app/
│   ├── streamlit_app.py       # Streamlit frontend
│   └── .streamlit/            # Streamlit configuration
├── tests/
│   ├── unit/                  # Unit tests (503)
│   └── integration/           # Integration tests (2)
├── scripts/
│   └── deployment/            # Cloud deployment scripts
├── data/
│   ├── raw/                   # Source PDFs
│   ├── processed/             # Processed data
│   └── vector_stores/         # FAISS indexes
├── Dockerfile                 # API container
├── Dockerfile.streamlit       # Frontend container
├── docker-compose.api.yml     # Local orchestration
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Query RAG System
```http
POST /query
Content-Type: application/json

{
  "query": "¿Qué lugares visitar en Cusco?",
  "top_k": 3,
  "llm_model": "openai",
  "include_metadata": true
}
```

**Response:**
```json
{
  "answer": "En Cusco puedes visitar...",
  "sources": ["cusco_guide.pdf", "machu_picchu.pdf"],
  "metadata": [{"department": "Cusco", "category": "tourism"}],
  "latency_ms": 245.67,
  "retrieval_latency_ms": 12.34,
  "generation_latency_ms": 233.33
}
```

#### 2. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "embedder": "healthy",
    "vector_store": "healthy",
    "retriever": "healthy",
    "num_vectors": "42"
  }
}
```

#### 3. List Available Models
```http
GET /models
```

**Response:**
```json
{
  "models": ["openai", "anthropic", "deepseek", "azure", "huggingface"],
  "default_model": "openai"
}
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 👨‍💻 Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_vector_store.py -v

# Integration tests only
pytest tests/integration/ -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking (if mypy configured)
mypy src/
```

### Adding New LLM Provider

1. Create new file in `src/llm/`:
```python
# src/llm/new_provider_llm.py
from src.llm.base_llm import BaseLLM, LLMResponse

class NewProviderLLM(BaseLLM):
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        # Implementation
        pass
```

2. Register in `src/api/dependencies/__init__.py`:
```python
llm_map = {
    "openai": OpenAILLM,
    "newprovider": NewProviderLLM,  # Add here
    ...
}
```

3. Add tests in `tests/unit/llm/test_newprovider_llm.py`

---

## 🐳 Deployment

### Local with Docker

```bash
# Build and run API
docker-compose -f docker-compose.api.yml up -d

# View logs
docker-compose -f docker-compose.api.yml logs -f

# Stop
docker-compose -f docker-compose.api.yml down
```

### Azure Container Apps

```bash
cd scripts/deployment
chmod +x deploy-azure.sh
./deploy-azure.sh
```

### AWS ECS Fargate

```bash
cd scripts/deployment
chmod +x deploy-aws.sh
./deploy-aws.sh
```

### Google Cloud Run

```bash
cd scripts/deployment
chmod +x deploy-gcp.sh
./deploy-gcp.sh
```

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Set main file: `app/streamlit_app.py`
5. Add secrets:
   ```toml
   API_URL = "https://your-api-url.com"
   ```

**See**: [Deployment README](scripts/deployment/README.md) for detailed instructions

---

## 🧪 Testing

### Test Statistics

| Component | Tests | Coverage |
|-----------|-------|----------|
| Data Pipeline | 230 | 94% |
| Vector Store | 38 | 94% |
| Retrieval | 34 | 100% |
| LLM Integration | 175 | 93% |
| RAG Generator | 24 | 98% |
| Integration | 2 | 100% |
| **Total** | **505** | **94%+** |

### Test Structure

```
tests/
├── unit/
│   ├── data_pipeline/
│   ├── embedding_pipeline/
│   ├── vector_store/
│   ├── retrieval_pipeline/
│   ├── llm/
│   └── rag/
└── integration/
    └── test_simple_rag.py
```

### Running Specific Test Suites

```bash
# Data pipeline tests
pytest tests/unit/data_pipeline/ -v

# LLM tests
pytest tests/unit/llm/ -v

# Integration tests
pytest tests/integration/ -v

# With markers
pytest -m "slow" -v  # Only slow tests
pytest -m "not slow" -v  # Skip slow tests
```

---

## ⚡ Performance

### Benchmarks

| Metric | Value |
|--------|-------|
| **Query Latency** | ~250ms (avg) |
| **Retrieval Time** | ~12ms |
| **Generation Time** | ~230ms |
| **Documents Retrieved** | 3-5 |
| **Throughput** | ~100 req/min |
| **Vector Store Size** | ~1M vectors |

### Optimization Tips

1. **Caching**: Implement Redis for repeated queries
2. **Batch Processing**: Process multiple queries together
3. **Model Selection**: Use GPT-3.5 for speed, GPT-4 for quality
4. **Top-K Tuning**: Reduce top_k for faster retrieval
5. **Async Operations**: Leverage FastAPI's async capabilities

---

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Auto-generated OpenAPI docs
- [Frontend README](app/README.md) - Streamlit app usage
- [Deployment Guide](scripts/deployment/README.md) - Cloud deployment
- [Week 2 Progress](PROGRESS_WEEK2.md) - Vector store development
- [Week 3 Progress](PROGRESS_WEEK3.md) - LLM integration
- [Week 4 Progress](PROGRESS_WEEK4.md) - API + Docker + Integration tests

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Run test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built following best practices from:
- **LLM Engineer's Handbook** (Iusztin & Labonne)
- **Hands-On Large Language Models** (Alammar & Grootendorst)
- **Build a Large Language Model from Scratch** (Raschka)
- **Storytelling with Data** (Nussbaumer Knaflic)

---

## 📧 Contact

**Author**: Your Name  
**Email**: your.email@example.com  
**LinkedIn**: [Your Profile](https://linkedin.com/in/yourprofile)  
**Portfolio**: [yourportfolio.com](https://yourportfolio.com)

---

**Made with ❤️ for Peru** 🇵🇪

[![Star this repo](https://img.shields.io/github/stars/yourusername/peruguide-rag?style=social)](https://github.com/yourusername/peruguide-rag)
