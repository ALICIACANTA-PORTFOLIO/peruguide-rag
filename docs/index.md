# Getting Started with PeruGuide AI

## Welcome! 👋

This guide will help you set up your development environment and start contributing to PeruGuide AI.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **VS Code** (recommended) ([Download](https://code.visualstudio.com/))
- **8GB+ RAM** (for local LLM inference)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/peruguide-rag.git
cd peruguide-rag
```

### Step 2: Create Virtual Environment

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Verify installation
python -c "import langchain; print('LangChain version:', langchain.__version__)"
```

### Step 4: Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configurations
# Use your favorite editor (VS Code, nano, vim, etc.)
```

**Key variables to configure:**

```env
# LLM Settings
LLM_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3
LLM_TEMPERATURE=0.3

# Vector Store
VECTOR_STORE_TYPE=chroma
VECTOR_STORE_PATH=./data/vector_stores

# Retrieval
RETRIEVAL_TOP_K=5
RETRIEVAL_SCORE_THRESHOLD=0.7
```

### Step 5: Prepare Data

```bash
# (Optional) Download sample PDFs to test
# The actual PDFs are in "Complementarios Peru/" folder

# Create necessary directories
mkdir -p data/raw data/processed data/vector_stores logs
```

### Step 6: Install Pre-commit Hooks

```bash
# Install pre-commit hooks for code quality
pre-commit install

# Run manually to test
pre-commit run --all-files
```

## Verify Installation

Run the following commands to verify everything is set up correctly:

```bash
# Run tests
pytest tests/ -v

# Check code quality
ruff check src/ api/ app/
black --check src/ api/ app/
mypy src/

# Start API (should show error about missing data, that's OK for now)
uvicorn api.main:app --reload
```

## Project Structure Overview

```
peruguide-rag/
├─ src/              # Core ML pipelines
├─ api/              # FastAPI backend
├─ app/              # Streamlit UI
├─ tests/            # Test suite
├─ docs/             # Documentation
├─ notebooks/        # Jupyter notebooks
├─ data/             # Data directory
└─ analisis/         # Research & analysis
```

## Next Steps

1. **Read the Architecture** → `docs/architecture/overview.md`
2. **Understand Your Role** → `DEVELOPMENT_ROLES.md`
3. **Start Implementing** → Follow the weekly roadmap

## Development Workflow

### Daily Workflow

```bash
# 1. Pull latest changes
git pull origin main

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes
# ... code ...

# 4. Run tests
pytest tests/ -v --cov=src

# 5. Check code quality
ruff check src/ tests/
black src/ tests/

# 6. Commit changes
git add .
git commit -m "feat: your feature description"

# 7. Push changes
git push origin feature/your-feature-name

# 8. Create Pull Request on GitHub
```

### Running the Application

#### Option 1: API Only

```bash
# Start FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Access:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

#### Option 2: UI Only

```bash
# Start Streamlit app
streamlit run app/Home.py

# Access: http://localhost:8501
```

#### Option 3: Full Stack

```bash
# Terminal 1: API
uvicorn api.main:app --reload

# Terminal 2: UI
streamlit run app/Home.py
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Solution: Ensure you're in the venv
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. Port Already in Use

```bash
# Solution: Use different port
uvicorn api.main:app --reload --port 8001
streamlit run app/Home.py --server.port 8502
```

#### 3. Out of Memory

```bash
# Solution: Reduce batch sizes in .env
EMBEDDING_BATCH_SIZE=16  # Default: 32
RETRIEVAL_TOP_K=3        # Default: 5
```

## Getting Help

- **Documentation**: Check `docs/` folder
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Email**: your.email@example.com

## Resources

- **LangChain Docs**: https://python.langchain.com/docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Streamlit Docs**: https://docs.streamlit.io/
- **RAGAS Docs**: https://docs.ragas.io/

---

**Ready to build? Let's go! 🚀**
